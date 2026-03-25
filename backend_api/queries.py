import sqlite3
from .models import SystemSnapshot, PanelSnapshot

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
