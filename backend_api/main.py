from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime, timedelta

from .models import SystemSnapshot, PanelSnapshot
from .queries import (
    get_latest_system,
    get_latest_panels,
    get_day_history,
    get_hourly_history,
    get_db_connection,   # ← REQUIRED for the daily summary endpoint
)
from .health import router as health_router

app = FastAPI(title="PVS6 Solar API")
app.include_router(health_router)


# ---------------------------------------------------------
# PANEL DECODER (Recovered from your original installation)
# ---------------------------------------------------------
PANEL_DECODER = {
    "E00121852000075": "R1C1",
    "E00121852023052": "R1C2",
    "E00121852025410": "R1C3",
    "E00121852033052": "R1C4",
    "E00121852033089": "R1C5",
    "E00121852033095": "R1C6",
    "E00121852033142": "R1C7",
    "E00121925111981": "R1C8",

    "E00121852033832": "R2C1",
    "E00121852033929": "R2C2",
    "E00121852033934": "R2C3",
    "E00121852034031": "R2C4",
    "E00121852051287": "R2C5",
    "E00121852051329": "R2C6",
    "E00121925115844": "R2C7"
}


# ---------------------------------------------------------
# HEALTH SCORING (Row‑agnostic, safe for your real serials)
# ---------------------------------------------------------
def compute_panel_scores(panels):
    if not panels:
        return panels

    ac_values = [p.ac_power_kw or 0 for p in panels]
    ac_values_sorted = sorted(ac_values)
    median_ac = ac_values_sorted[len(ac_values_sorted) // 2]

    for p in panels:
        health_score = (p.ac_power_kw or 0) / median_ac if median_ac > 0 else 0

        p.health_score = round(health_score, 3)
        p.normalized_output = 1.0
        p.combined_score = p.health_score

        if p.combined_score >= 0.95:
            p.status = "green"
        elif p.combined_score >= 0.85:
            p.status = "yellow"
        elif p.combined_score >= 0.70:
            p.status = "orange"
        else:
            p.status = "red"

    return panels


# ---------------------------------------------------------
# CORS (Frontend access)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# SYSTEM ENDPOINTS
# ---------------------------------------------------------
@app.get("/api/current", response_model=SystemSnapshot)
def api_current():
    return get_latest_system()


@app.get("/api/history/day")
def api_history_day(date: str):
    return get_day_history(date)


@app.get("/api/history/day/hourly")
def api_history_day_hourly(date: str):
    return get_hourly_history(date)


@app.get("/mode")
def get_mode():
    try:
        with open("/home/pi/pvs6-monitor/mode", "r") as f:
            return {"mode": f.read().strip()}
    except (FileNotFoundError, OSError):
        return {"mode": "unknown"}


@app.get("/api/system/current")
def api_system_current():
    import sqlite3
    from .queries import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT timestamp, production_kw, consumption_kw, grid_kw
        FROM readings
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    row = cur.fetchone()
    conn.close()

    if not row:
        return {"error": "no data"}

    ts, solar, load, grid = row

    return {
        "timestamp": ts,
        "solar_kw": solar,
        "load_kw": load,
        "net_kw": solar - load,
        "grid_kw": grid
    }


# ---------------------------------------------------------
# PANELS ENDPOINT (Decoder + scoring + correct DB schema)
# ---------------------------------------------------------
@app.get("/api/panels", response_model=list[PanelSnapshot])
def api_panels():
    rows = get_latest_panels()

    panels = []
    for r in rows:
        serial = r["inverter_serial"]
        physical_label = PANEL_DECODER.get(serial, "UNKNOWN")

        panel = PanelSnapshot(
            inverter_serial=serial,
            module_serial=r["module_serial"],
            model=r["model"],
            state=r["state"],
            state_descr=r["state_descr"],
            ac_power_kw=r["ac_power_kw"],
            dc_power_kw=r["dc_power_kw"],
            lifetime_ac_kwh=r["lifetime_ac_kwh"],
            ac_voltage_v=r["ac_voltage_v"],
            ac_current_a=r["ac_current_a"],
            dc_voltage_v=r["dc_voltage_v"],
            dc_current_a=r["dc_current_a"],
            heatsink_temp_c=r["heatsink_temp_c"],
            timestamp=r["timestamp"],
            physical_label=physical_label
        )

        panels.append(panel)

    panels = compute_panel_scores(panels)

    # Sort by physical layout (R1C1 → R2C7)
    panels.sort(key=lambda p: p.physical_label)

    return panels

def compute_summary(first, last):
    prod = last["production_lifetime_kwh"] - first["production_lifetime_kwh"]
    imp  = last["grid_imported_lifetime_kwh"] - first["grid_imported_lifetime_kwh"]
    exp  = last["grid_exported_lifetime_kwh"] - first["grid_exported_lifetime_kwh"]

    cons = prod + imp - exp
    net  = prod - cons

    return {
        "production_kwh": round(prod, 3),
        "consumption_kwh": round(cons, 3),
        "grid_import_kwh": round(imp, 3),
        "grid_export_kwh": round(exp, 3),
        "net_kwh": round(net, 3)
    }

@app.get("/api/summary/daily")
def api_daily_summary(date: str):
    """
    Returns daily totals for production, consumption, import, export, and net.
    Example: /api/summary/daily?date=2026-05-13
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Convert YYYY-MM-DD to start/end timestamps
        start_dt = datetime.strptime(date, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=1) - timedelta(seconds=1)

        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())

        # First sample
        cur.execute("""
            SELECT *
            FROM readings
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
            LIMIT 1;
        """, (start_ts, end_ts))
        first = cur.fetchone()

        # Last sample
        cur.execute("""
            SELECT *
            FROM readings
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT 1;
        """, (start_ts, end_ts))
        last = cur.fetchone()

        if not first or not last:
            return {"error": "No data for this date"}

        # Extract cumulative values
        prod = last["production_lifetime_kwh"] - first["production_lifetime_kwh"]
        imp  = last["grid_imported_lifetime_kwh"] - first["grid_imported_lifetime_kwh"]
        exp  = last["grid_exported_lifetime_kwh"] - first["grid_exported_lifetime_kwh"]

        # Compute consumption and net
        cons = prod + imp - exp
        net  = prod - cons

        return {
            "production_kwh": round(prod, 3),
            "consumption_kwh": round(cons, 3),
            "grid_import_kwh": round(imp, 3),
            "grid_export_kwh": round(exp, 3),
            "net_kwh": round(net, 3)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary/weekly")
def api_weekly_summary(date: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        end_dt = datetime.strptime(date, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=6)

        start_ts = int(start_dt.replace(hour=0, minute=0, second=0).timestamp())
        end_ts = int(end_dt.replace(hour=23, minute=59, second=59).timestamp())

        # First sample of the week
        cur.execute("""
            SELECT *
            FROM readings
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
            LIMIT 1;
        """, (start_ts, end_ts))
        first = cur.fetchone()

        # Last sample of the week
        cur.execute("""
            SELECT *
            FROM readings
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT 1;
        """, (start_ts, end_ts))
        last = cur.fetchone()

        if not first or not last:
            return {"error": "No data for this week"}

        return compute_summary(first, last)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary/monthly")
def api_monthly_summary(date: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        dt = datetime.strptime(date, "%Y-%m-%d")

        # First day of month
        start_dt = dt.replace(day=1, hour=0, minute=0, second=0)

        # Last day of month
        if dt.month == 12:
            next_month = dt.replace(year=dt.year + 1, month=1, day=1)
        else:
            next_month = dt.replace(month=dt.month + 1, day=1)

        end_dt = next_month - timedelta(seconds=1)

        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())

        # First sample of the month
        cur.execute("""
            SELECT *
            FROM readings
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
            LIMIT 1;
        """, (start_ts, end_ts))
        first = cur.fetchone()

        # Last sample of the month
        cur.execute("""
            SELECT *
            FROM readings
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT 1;
        """, (start_ts, end_ts))
        last = cur.fetchone()

        if not first or not last:
            return {"error": "No data for this month"}

        return compute_summary(first, last)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary/yearly")
def api_yearly_summary(date: str):
    """
    Example: /api/summary/yearly?date=2026
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        year = int(date)

        # Start of year
        start_dt = datetime(year, 1, 1, 0, 0, 0)

        # End of year
        end_dt = datetime(year, 12, 31, 23, 59, 59)

        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())

        # First sample of the year
        cur.execute("""
            SELECT *
            FROM readings
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
            LIMIT 1;
        """, (start_ts, end_ts))
        first = cur.fetchone()

        # Last sample of the year
        cur.execute("""
            SELECT *
            FROM readings
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT 1;
        """, (start_ts, end_ts))
        last = cur.fetchone()

        if not first or not last:
            return {"error": "No data for this year"}

        return compute_summary(first, last)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
