from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import SystemSnapshot, PanelSnapshot

from .queries import (
    get_latest_system,
    get_latest_panels,
    get_day_history,
    get_hourly_history,
)

from .models import SystemSnapshot, PanelSnapshot
from .health import router as health_router

app = FastAPI(title="PVS6 Solar API")

app.include_router(health_router)


def compute_panel_scores(panels):
    # Group by inverter row (R1, R2) based on inverter_serial prefix
    rows = {"R1": [], "R2": []}
    for p in panels:
        row = p.inverter_serial[:2]  # e.g., "R1", "R2"
        rows[row].append(p)

    for row, plist in rows.items():
        if not plist:
            continue

        # Median AC power
        ac_values = [p.ac_power_kw or 0 for p in plist]
        ac_values_sorted = sorted(ac_values)
        median_ac = ac_values_sorted[len(ac_values_sorted) // 2]

        for p in plist:
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


    return panels

# Allow dashboard frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    from .queries import DB_PATH  # adjust if DB_PATH is defined elsewhere

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
    
@app.get("/api/panels", response_model=list[PanelSnapshot])
def api_panels():
    rows = get_latest_panels()
    panels = [PanelSnapshot(**dict(row)) for row in rows]

    # Add scoring
    panels = compute_panel_scores(panels)

    return panels
