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
    # Group by row (R1, R2)
    rows = {"R1": [], "R2": []}
    for p in panels:
        row = p.physical_label[:2]  # "R1" or "R2"
        rows[row].append(p)

    for row, plist in rows.items():
        if not plist:
            continue

        # Median AC for the row
        ac_values = [p.ac_kw for p in plist]
        ac_values_sorted = sorted(ac_values)
        median_ac = ac_values_sorted[len(ac_values_sorted) // 2]

        for p in plist:
            # Health Score (relative)
            health_score = p.ac_kw / median_ac if median_ac > 0 else 0

            # Normalized Output (AC / V*I), but only when producing - this was not working it may have been a unit issue, removed for now 2026/3/31
            #if p.dc_kw > 0.1:
            #    denom = p.vdc * p.idc
            #    normalized = p.ac_kw / denom if denom > 0 else 0
            #else:
            #    normalized = 1.0

            # Combined Score
            #combined = 0.6 * health_score + 0.4 * normalized
            normalized = 1.0

            combined = 1 * health_score

            # Status color
            if combined >= 0.95:
                status = "green"
            elif combined >= 0.85:
                status = "yellow"
            elif combined >= 0.70:
                status = "orange"
            else:
                status = "red"

            # Attach to the object
            p.health_score = round(health_score, 3)
            p.normalized_output = round(normalized, 3)
            p.combined_score = round(combined, 3)
            p.status = status

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
