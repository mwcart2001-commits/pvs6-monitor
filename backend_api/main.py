from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .queries import (
    get_latest_system,
    get_latest_panels,
    get_day_history,
    get_hourly_history,
)

from .models import SystemSnapshot, PanelSnapshot
from .health import router as health_router

from fastapi import HTTPException
from datetime import datetime
from .health import get_backend_health, get_collector_health

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

@app.get("/api/panels", response_model=list[PanelSnapshot])
def api_panels():
    rows = get_latest_panels()
    panels = [PanelSnapshot(**dict(row)) for row in rows]

    # Add scoring
    panels = compute_panel_scores(panels)

    return panels

@app.get("/api/history/day")
def api_history_day(date: str):
    return get_day_history(date)

@app.get("/api/history/day/hourly")
def api_history_day_hourly(date: str):
    return get_hourly_history(date)

# Added 4/26/2-026 to support new feature Current System Page

@app.get("/api/system/current")
def api_system_current():
    try:
        system = get_latest_system()
        panels_raw = get_latest_panels()

        if system is None:
            raise HTTPException(status_code=500, detail="No system data available")

        panels = [PanelSnapshot(**dict(row)) for row in panels_raw]

        snapshot = {
            "system": {
                "production_kw": system.production_kw,
                "consumption_kw": system.consumption_kw,
                "grid_kw": system.grid_kw,
                "timestamp": datetime.utcnow().isoformat()
            },
            "panels": [
                {
                    "serial": p.inverter_serial,
                    "ac_kw": p.ac_kw,
                    "temp_c": p.temp_c,
                    "lifetime_kwh": p.lifetime_kwh,
                    "status": getattr(p, "status", None),
                    "combined_score": getattr(p, "combined_score", None)
                }
                for p in panels
            ],
            "status": {
                "backend": get_backend_health(),
                "collector": get_collector_health(),
                "panel_count": len(panels)
            }
        }

        return snapshot

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build system snapshot: {e}")

@app.get("/mode")
def get_mode():
    try:
        with open("/home/pi/pvs6-monitor/mode", "r") as f:
            return {"mode": f.read().strip()}
    except (FileNotFoundError, OSError):
        return {"mode": "unknown"}

