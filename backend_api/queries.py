import sqlite3
from .models import SystemSnapshot
from datetime import datetime, timedelta


DB_PATH = "/home/pi/pvs6-monitor/pvs6_data.db"

def get_latest_system():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    row = cur.execute("""
        SELECT timestamp,
               production_kw,
               consumption_kw,
               grid_kw,
               production_lifetime_kwh,
               grid_imported_lifetime_kwh,
               grid_exported_lifetime_kwh
        FROM readings
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()

    conn.close()

    if row is None:
        return SystemSnapshot(
            timestamp="N/A",
            production_kw=0,
            consumption_kw=0,
            grid_kw=0,
            lifetime_solar_kwh=0,
            lifetime_import_kwh=0,
            lifetime_export_kwh=0,
            panel_count=0
        )

    return SystemSnapshot(
        timestamp=str(row[0]),
        production_kw=row[1],
        consumption_kw=row[2],
        grid_kw=row[3],
        lifetime_solar_kwh=row[4],
        lifetime_import_kwh=row[5],
        lifetime_export_kwh=row[6],
        panel_count=_get_latest_panel_count()
    )


def _get_latest_panel_count():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    row = cur.execute("""
        SELECT COUNT(*)
        FROM panel_readings
        WHERE timestamp = (SELECT MAX(timestamp) FROM panel_readings)
    """).fetchone()

    conn.close()
    return row[0] if row and row[0] is not None else 0

def get_latest_panels():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT 
            pr.inverter_serial,
            pi.physical_label,
            pi.install_group,
            pr.ac_power_kw AS ac_kw,
            pr.dc_power_kw AS dc_kw,
            pr.dc_voltage_v AS vdc,
            pr.dc_current_a AS idc,
            pr.heatsink_temp_c AS temp_c,
            pr.lifetime_ac_kwh AS lifetime_kwh
        FROM panel_readings pr
        LEFT JOIN panel_identity pi
            ON pr.inverter_serial = pi.inverter_id
        WHERE pr.timestamp = (
            SELECT MAX(timestamp) FROM panel_readings
        )
        ORDER BY pi.physical_label;
    """).fetchall()

    conn.close()
    return rows

def get_day_history(date_str: str):
    day_start = datetime.fromisoformat(date_str)
    day_end = day_start + timedelta(days=1)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT timestamp, production_kw, consumption_kw, grid_kw
        FROM readings
        WHERE timestamp >= ? AND timestamp < ?
        ORDER BY timestamp ASC
    """, (day_start.timestamp(), day_end.timestamp()))

    rows = cur.fetchall()
    conn.close()

    timestamps = []
    production = []
    consumption = []
    grid = []

    for ts, prod, cons, grd in rows:
        timestamps.append(ts)
        production.append(prod)
        consumption.append(cons)
        grid.append(grd)

    # --- Energy calculations ---
    interval_hours = 20 / 3600  # 20-second collector interval

    total_production_kwh = sum(p * interval_hours for p in production)
    total_consumption_kwh = sum(c * interval_hours for c in consumption)
    total_grid_kwh = sum(g * interval_hours for g in grid)

    peak_production_kw = max(production) if production else 0
    peak_consumption_kw = max(consumption) if consumption else 0

    return {
        "timestamps": timestamps,
        "production": production,
        "consumption": consumption,
        "grid": grid,
        "summary": {
            "total_production_kwh": round(total_production_kwh, 3),
            "total_consumption_kwh": round(total_consumption_kwh, 3),
            "total_grid_kwh": round(total_grid_kwh, 3),
            "peak_production_kw": round(peak_production_kw, 3),
            "peak_consumption_kw": round(peak_consumption_kw, 3),
        }
    }

def get_hourly_history(date_str: str):
    day_start = datetime.fromisoformat(date_str)
    day_end = day_start + timedelta(days=1)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT timestamp, production_kw, consumption_kw, grid_kw
        FROM readings
        WHERE timestamp >= ? AND timestamp < ?
        ORDER BY timestamp ASC
    """, (day_start.timestamp(), day_end.timestamp()))

    rows = cur.fetchall()
    conn.close()

    # 24 buckets
    hourly_prod = [0] * 24
    hourly_cons = [0] * 24
    hourly_net  = [0] * 24

    interval_hours = 20 / 3600  # 20-second samples

    for ts, prod, cons, grid in rows:
        hour = datetime.fromtimestamp(ts).hour

        hourly_prod[hour] += prod * interval_hours
        hourly_cons[hour] += cons * interval_hours
        hourly_net[hour]  += (prod - cons) * interval_hours

    return {
        "hours": [f"{h:02d}" for h in range(24)],
        "production_kwh": [round(v, 3) for v in hourly_prod],
        "consumption_kwh": [round(v, 3) for v in hourly_cons],
        "net_kwh": [round(v, 3) for v in hourly_net]
    }
