from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import SystemSnapshot, PanelSnapshot
from .queries import (
    get_latest_system,
    get_latest_panels,
    get_day_history,
    get_hourly_history,
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
