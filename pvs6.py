#!/usr/bin/env python3
# Copyright (c) 2026 Bret Woz. Licensed under the MIT License. See LICENSE for details.
# This file was created with the assistance of AI.
"""
pvs6.py - SunPower PVS6 Energy Monitor
Version 1.0 (2026-03-21)

Retrieves real-time and historical energy data from a SunPower PVS6 monitoring
unit on your local network. Supports both legacy firmware (< build 61840, no auth)
and new firmware (>= build 61840, requires HTTP Basic Auth).

Network access:
  - New firmware (61840+): PVS6 is accessible on your home LAN. Find its IP via
    your router's DHCP table, then use --host <IP>.
  - Old firmware: API is only reachable via the PVS6's own WiFi hotspot or the
    LAN1 installer Ethernet port (always at 172.27.153.1).
    Hotspot SSID:     SunPower + serial[4:6] + serial[-3:]
    Hotspot password: serial[2:6] + serial[-4:]

Usage:
  python pvs6.py status              # Show current readings
  python pvs6.py devices             # Dump raw device list (useful for setup)
  python pvs6.py collect             # Start polling daemon, stores data to SQLite
  python pvs6.py history             # Show hourly energy report (all collected data)
  python pvs6.py history --start 2025-01-01 --end 2025-01-31

Required for new firmware authentication (any of these):
  export PVS6_SERIAL=<your serial number>   # recommended for automation
  --serial <serial number>                  # command-line flag

Options:
  --host HOST         PVS6 IP address (default: 172.27.153.1)
  --serial SN         PVS6 serial number (last 5 chars used as password)
  --db FILE           SQLite database path (default: pvs6_data.db)
  --interval SECS     Polling interval for collect command (default: 60)
  --start YYYY-MM-DD  Start date for history command
  --end YYYY-MM-DD    End date for history command

Dependencies:
  pip install requests
"""

# import systemd.daemon
import argparse
import base64
import json
import os
import sqlite3
import sys
import time
import urllib3
from datetime import datetime
from typing import Optional

try:
    import requests
    from requests import Session
except ImportError:
    print("Error: 'requests' library is required.")
    print("Install it with: pip install requests")
    sys.exit(1)

# Suppress HTTPS certificate warnings (PVS6 uses a self-signed cert)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Constants ---

DEFAULT_HOST = "172.27.153.1"
DEFAULT_DB = "pvs6_data.db"
DEFAULT_INTERVAL = 60  # seconds
AUTH_USER = "ssm_owner"
NEW_FIRMWARE_BUILD = 61840

# Device type identifiers returned by the DeviceList API
DEVICE_TYPE_SUPERVISOR = "PVS"
DEVICE_TYPE_INVERTER = "SOLARBRIDGE"
DEVICE_TYPE_METER_PRODUCTION = "PVS5-METER-P"
DEVICE_TYPE_METER_CONSUMPTION = "PVS5-METER-C"


# --- Exceptions ---

class PVS6Error(Exception):
    pass


class PVS6AuthError(PVS6Error):
    pass


class PVS6ConnectionError(PVS6Error):
    pass


# --- Client ---

class PVS6Client:
    """
    HTTP client for the SunPower PVS6 local API.

    Handles firmware detection and authentication automatically. On new firmware,
    authentication uses HTTP Basic Auth against the /auth?login endpoint, which
    establishes a session cookie for subsequent requests.
    """

    def __init__(self, host: str, serial: Optional[str] = None, timeout: int = 30, debug: bool = False):
        self.host = host
        self.serial = serial
        self.timeout = timeout
        self.debug = debug
        self.session = Session()
        self.session.verify = False  # PVS6 uses self-signed TLS cert
        self.firmware_build = 0
        self.firmware_version = ""
        self.authenticated = False

    def _url(self, path: str, scheme: str = "http") -> str:
        return f"{scheme}://{self.host}{path}"

    def _derive_password(self) -> Optional[str]:
        """
        Derive the API password from the serial number.
        The password is the last 5 characters of the serial (uppercase).
        """
        if not self.serial:
            return None
        return self.serial.strip().upper()[-5:]

    def detect_firmware(self) -> int:
        """
        Query the PVS6 firmware build number.
        Returns the integer build number, or 0 if detection fails.
        """
        # Try the varserver endpoint (new firmware, may require auth)
        for scheme in ("https", "http"):
            try:
                resp = self.session.get(
                    self._url("/vars", scheme),
                    params={"name": "/sys/info/sw_rev"},
                    timeout=self.timeout,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    values = data.get("values", [])
                    if values:
                        sw_rev = values[0].get("value", "")
                        build = _parse_build_from_swver(sw_rev)
                        if build:
                            self.firmware_version = sw_rev.strip()
                            return build
            except requests.exceptions.RequestException:
                pass

        # Try the new authenticated device list endpoint (new firmware, HTTPS + auth)
        if self.authenticated:
            try:
                resp = self.session.get(
                    self._url("/cgi-bin/dl_cgi/devices/list", "https"),
                    timeout=self.timeout,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for device in data.get("devices", []):
                        if device.get("DEVICE_TYPE") == DEVICE_TYPE_SUPERVISOR:
                            swver = device.get("SWVER", "")
                            build = _parse_build_from_swver(swver)
                            if build:
                                self.firmware_version = swver.strip()
                                return build
            except requests.exceptions.RequestException:
                pass

        # Try the dl_cgi supervisor info as a fallback (old firmware, HTTP, no auth)
        try:
            resp = self.session.get(
                self._url("/cgi-bin/dl_cgi", "http"),
                params={"Command": "DeviceList"},
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                for device in data.get("devices", []):
                    if device.get("DEVICE_TYPE") == DEVICE_TYPE_SUPERVISOR:
                        swver = device.get("SWVER", "")
                        build = _parse_build_from_swver(swver)
                        if build:
                            self.firmware_version = swver.strip()
                            return build
        except requests.exceptions.RequestException:
            pass

        return 0

    def authenticate(self) -> None:
        """
        Authenticate with the PVS6 using HTTP Basic Auth.
        Required for firmware build >= 61840.
        """
        password = self._derive_password()
        if not password:
            raise PVS6AuthError(
                "Serial number is required for new firmware authentication.\n"
                "Provide it via --serial or the PVS6_SERIAL environment variable."
            )

        credentials = f"{AUTH_USER}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()

        try:
            resp = self.session.get(
                self._url("/auth?login", "https"),
                headers={"Authorization": f"Basic {encoded}"},
                timeout=self.timeout,
                allow_redirects=False,
            )
        except requests.exceptions.RequestException as e:
            raise PVS6ConnectionError(f"Authentication request failed: {e}")

        if self.debug:
            print(f"  [debug] auth response: HTTP {resp.status_code}")
            print(f"  [debug] session cookies after auth: {dict(self.session.cookies)}")

        if resp.status_code == 401:
            raise PVS6AuthError(
                "Authentication failed (401). Check that your serial number is correct.\n"
                f"Password used: last 5 chars of serial = '{password}'"
            )
        if resp.status_code not in (200, 302):
            raise PVS6AuthError(
                f"Unexpected authentication response: HTTP {resp.status_code}"
            )

        self.authenticated = True

    def connect(self) -> None:
        """
        Authenticate if possible, then detect firmware version.
        Authentication is attempted first (assuming newer firmware that requires auth).
        If authentication fails, falls back to unauthenticated access for legacy firmware.
        """
        print(f"Connecting to PVS6 at {self.host}...")

        if self.serial:
            print("Attempting authentication...")
            try:
                self.authenticate()
                print("Authenticated successfully.")
            except PVS6AuthError as e:
                print("Authentication failed — falling back to unauthenticated access (legacy firmware).")
                if self.debug:
                    print(f"  [debug] auth error: {e}")
            except PVS6ConnectionError as e:
                print("Authentication request failed — falling back to unauthenticated access.")
                if self.debug:
                    print(f"  [debug] connection error: {e}")

        build = self.detect_firmware()
        self.firmware_build = build

        if build:
            if self.firmware_version:
                print(f"Firmware: {self.firmware_version}")
            else:
                print(f"Firmware build: {build}")
        else:
            print("Could not detect firmware version (device may still be reachable).")

        if not self.authenticated:
            print("Proceeding without authentication (legacy firmware).")

    def get_device_list(self, debug: bool = False) -> list:
        """
        Fetch the raw device list from the PVS6.
        Returns a list of device dicts as returned by the API.
        """
        # New firmware (61840+) uses a RESTful path; old firmware uses query-string form.
        if self.firmware_build >= NEW_FIRMWARE_BUILD or self.authenticated:
            schemes = ["https"]
            path = "/cgi-bin/dl_cgi/devices/list"
            params = {}
        else:
            schemes = ["http"]
            path = "/cgi-bin/dl_cgi"
            params = {"Command": "DeviceList"}

        if debug:
            print(f"  [debug] session cookies: {dict(self.session.cookies)}")

        for scheme in schemes:
            url = self._url(path, scheme)
            if debug:
                print(f"  [debug] GET {url}" + (f"?Command=DeviceList" if params else ""))
            try:
                resp = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                )
            except requests.exceptions.RequestException as e:
                if scheme == schemes[-1]:
                    raise PVS6ConnectionError(f"Failed to reach PVS6 at {self.host}: {e}")
                if debug:
                    print(f"  [debug] request error on {scheme}: {e} — trying next scheme")
                continue

            if debug:
                print(f"  [debug] response: HTTP {resp.status_code}")

            if resp.status_code == 200:
                break

            if resp.status_code in (401, 403) and scheme != schemes[-1]:
                if debug:
                    print(f"  [debug] {resp.status_code} on {scheme} — trying next scheme")
                continue
            break

        if resp.status_code == 401:
            raise PVS6AuthError(
                "Authentication required or session expired. "
                "Re-run with authentication."
            )
        if resp.status_code == 403:
            raise PVS6AuthError(
                "Access forbidden (403). If you have new firmware, authentication is required."
            )
        resp.raise_for_status()

        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            raise PVS6Error(f"Invalid JSON response from PVS6: {e}")

        return data.get("devices", [])

    def get_readings(self) -> dict:
        """
        Fetch current readings from the PVS6.

        Returns:
            dict with keys:
                timestamp               Unix timestamp (float)
                production_kw           Solar production in kW
                grid_kw                 Grid power in kW (+ = importing, - = exporting)
                consumption_kw          Home consumption in kW
                production_lifetime_kwh Cumulative solar production (kWh)
                grid_imported_lifetime_kwh  Cumulative energy imported from grid (kWh)
                grid_exported_lifetime_kwh  Cumulative energy exported from grid (kWh)
                panels                  List of per-panel readings (dicts)
        """
        devices = self.get_device_list(debug=self.debug)

        production_kw = None
        grid_kw = None
        production_lifetime_kwh = None
        grid_imported_lifetime_kwh = None
        grid_exported_lifetime_kwh = None

        panels = []

        for device in devices:
            # New firmware puts meter subtype in "TYPE"; old firmware uses "DEVICE_TYPE"
            dtype = device.get("TYPE") or device.get("DEVICE_TYPE", "")

            # --- meters ---
            if dtype == DEVICE_TYPE_METER_PRODUCTION:
                production_kw = _float(device.get("p_3phsum_kw"))
                production_lifetime_kwh = (
                    _float(device.get("ltea_3phsum_kwh"))
                    or _float(device.get("net_ltea_3phsum_kwh"))
                )

            elif dtype == DEVICE_TYPE_METER_CONSUMPTION:
                grid_kw = _float(device.get("p_3phsum_kw"))
                grid_imported_lifetime_kwh = _float(device.get("pos_ltea_3phsum_kwh"))
                grid_exported_lifetime_kwh = _float(device.get("neg_ltea_3phsum_kwh"))

            # --- inverters / panels ---
            elif dtype == DEVICE_TYPE_INVERTER:
                panels.append({
                    "inverter_serial": device.get("SERIAL"),
                    "module_serial": device.get("module_serial") or device.get("MOD_SN"),
                    "model": device.get("MODEL"),
                    "state": device.get("STATE"),
                    "state_descr": device.get("STATEDESCR"),
                    "ac_power_kw": _float(device.get("p_3phsum_kw")),
                    "dc_power_kw": _float(device.get("p_mppt1_kw")),
                    "lifetime_ac_kwh": _float(device.get("ltea_3phsum_kwh")),
                    "ac_voltage_v": _float(device.get("vln_3phavg_v")),
                    "ac_current_a": _float(device.get("i_3phsum_a")),
                    "dc_voltage_v": _float(device.get("v_mppt1_v")),
                    "dc_current_a": _float(device.get("i_mppt1_a")),
                    "freq_hz": _float(device.get("freq_hz")),
                    "heatsink_temp_c": _float(device.get("t_htsnk_degc")),
                    "status_index": _float(device.get("stat_ind")),
                    "sw_version": device.get("SWVER"),
                    "hw_version": device.get("hw_version"),
                    "curtime_raw": device.get("CURTIME"),
                })

        # Fallback: no distinct meter types found, try any meter devices
        if production_kw is None and grid_kw is None:
            meters = [d for d in devices if "METER" in d.get("DEVICE_TYPE", "")]
            if len(meters) >= 2:
                meters_with_lte = [
                    (d, _float(d.get("ltea_3phsum_kwh")) or 0.0) for d in meters
                ]
                meters_with_lte.sort(key=lambda x: x[1], reverse=True)
                prod_dev = meters_with_lte[0][0]
                grid_dev = meters_with_lte[1][0]
                production_kw = _float(prod_dev.get("p_3phsum_kw"))
                production_lifetime_kwh = _float(prod_dev.get("ltea_3phsum_kwh"))
                grid_kw = _float(grid_dev.get("p_3phsum_kw"))
                grid_imported_lifetime_kwh = _float(grid_dev.get("pos_ltea_3phsum_kwh"))
                grid_exported_lifetime_kwh = _float(grid_dev.get("neg_ltea_3phsum_kwh"))
            elif len(meters) == 1:
                production_kw = _float(meters[0].get("p_3phsum_kw"))
                production_lifetime_kwh = _float(meters[0].get("ltea_3phsum_kwh"))

        # Derive home consumption: production + grid_import - grid_export
        # Equivalently: production_kw + grid_kw (grid_kw is negative when exporting)
        consumption_kw = None
        if production_kw is not None and grid_kw is not None:
            consumption_kw = production_kw + grid_kw

        return {
            "timestamp": time.time(),
            "production_kw": production_kw or 0.0,
            "grid_kw": grid_kw or 0.0,
            "consumption_kw": consumption_kw or 0.0,
            "production_lifetime_kwh": production_lifetime_kwh,
            "grid_imported_lifetime_kwh": grid_imported_lifetime_kwh,
            "grid_exported_lifetime_kwh": grid_exported_lifetime_kwh,
            "panels": panels,
        }


# --- Database ---

def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize the SQLite database and return a connection."""
    conn = sqlite3.connect(db_path)

    # System-level readings
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id                          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp                   INTEGER NOT NULL,
            production_kw               REAL,
            grid_kw                     REAL,
            consumption_kw              REAL,
            production_lifetime_kwh     REAL,
            grid_imported_lifetime_kwh  REAL,
            grid_exported_lifetime_kwh  REAL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings (timestamp)"
    )

    # Per-panel readings
    conn.execute("""
        CREATE TABLE IF NOT EXISTS panel_readings (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp           INTEGER NOT NULL,
            inverter_serial     TEXT NOT NULL,
            module_serial       TEXT,
            model               TEXT,
            state               TEXT,
            state_descr         TEXT,
            ac_power_kw         REAL,
            dc_power_kw         REAL,
            lifetime_ac_kwh     REAL,
            ac_voltage_v        REAL,
            ac_current_a        REAL,
            dc_voltage_v        REAL,
            dc_current_a        REAL,
            freq_hz             REAL,
            heatsink_temp_c     REAL,
            status_index        REAL,
            sw_version          TEXT,
            hw_version          TEXT,
            curtime_raw         TEXT
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_panel_readings_timestamp "
        "ON panel_readings (timestamp)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_panel_readings_inverter "
        "ON panel_readings (inverter_serial)"
    )

    conn.commit()
    return conn


def store_reading(conn: sqlite3.Connection, r: dict) -> None:
    """Insert a system-level reading dict into the database."""
    conn.execute(
        """
        INSERT INTO readings (
            timestamp, production_kw, grid_kw, consumption_kw,
            production_lifetime_kwh, grid_imported_lifetime_kwh,
            grid_exported_lifetime_kwh
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            int(r["timestamp"]),
            r.get("production_kw"),
            r.get("grid_kw"),
            r.get("consumption_kw"),
            r.get("production_lifetime_kwh"),
            r.get("grid_imported_lifetime_kwh"),
            r.get("grid_exported_lifetime_kwh"),
        ),
    )
    conn.commit()


def store_panel_readings(conn: sqlite3.Connection, timestamp: int, panels: list) -> None:
    """Insert per-panel readings into the database."""
    if not panels:
        return
    rows = []
    for p in panels:
        rows.append((
            timestamp,
            p.get("inverter_serial"),
            p.get("module_serial"),
            p.get("model"),
            p.get("state"),
            p.get("state_descr"),
            p.get("ac_power_kw"),
            p.get("dc_power_kw"),
            p.get("lifetime_ac_kwh"),
            p.get("ac_voltage_v"),
            p.get("ac_current_a"),
            p.get("dc_voltage_v"),
            p.get("dc_current_a"),
            p.get("freq_hz"),
            p.get("heatsink_temp_c"),
            p.get("status_index"),
            p.get("sw_version"),
            p.get("hw_version"),
            p.get("curtime_raw"),
        ))
    conn.executemany("""
        INSERT INTO panel_readings (
            timestamp, inverter_serial, module_serial, model,
            state, state_descr,
            ac_power_kw, dc_power_kw, lifetime_ac_kwh,
            ac_voltage_v, ac_current_a,
            dc_voltage_v, dc_current_a,
            freq_hz, heatsink_temp_c, status_index,
            sw_version, hw_version, curtime_raw
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()


def query_hourly(
    conn: sqlite3.Connection,
    start_ts: int,
    end_ts: int,
) -> list:
    """
    Return hourly energy buckets for the given time range.

    Energy (kWh) for each hour is computed as the difference between the
    first and last lifetime kWh reading within that hour. This is accurate
    even if polling is interrupted, as long as at least two readings exist
    per hour.

    Returns a list of dicts:
        hour_start          datetime (local time) of the hour
        production_kwh      Solar energy produced this hour
        grid_import_kwh     Energy imported from grid this hour
        grid_export_kwh     Energy exported from grid this hour
        consumption_kwh     Home energy consumed this hour (derived)
        avg_production_kw   Average solar power during this hour
        avg_grid_kw         Average grid power during this hour (+ import, - export)
        reading_count       Number of raw readings in this hour
    """
    cursor = conn.execute(
        """
        WITH bucketed AS (
            SELECT
                (timestamp / 3600) * 3600                      AS hour_ts,
                production_lifetime_kwh,
                grid_imported_lifetime_kwh,
                grid_exported_lifetime_kwh,
                production_kw,
                grid_kw,
                ROW_NUMBER() OVER (
                    PARTITION BY (timestamp / 3600)
                    ORDER BY timestamp ASC
                ) AS rn_asc,
                ROW_NUMBER() OVER (
                    PARTITION BY (timestamp / 3600)
                    ORDER BY timestamp DESC
                ) AS rn_desc,
                COUNT(*) OVER (PARTITION BY (timestamp / 3600)) AS cnt
            FROM readings
            WHERE timestamp >= ? AND timestamp < ?
              AND production_lifetime_kwh IS NOT NULL
        )
        SELECT
            hour_ts,
            MAX(CASE WHEN rn_asc  = 1 THEN production_lifetime_kwh    END) AS prod_start,
            MAX(CASE WHEN rn_desc = 1 THEN production_lifetime_kwh    END) AS prod_end,
            MAX(CASE WHEN rn_asc  = 1 THEN grid_imported_lifetime_kwh END) AS imp_start,
            MAX(CASE WHEN rn_desc = 1 THEN grid_imported_lifetime_kwh END) AS imp_end,
            MAX(CASE WHEN rn_asc  = 1 THEN grid_exported_lifetime_kwh END) AS exp_start,
            MAX(CASE WHEN rn_desc = 1 THEN grid_exported_lifetime_kwh END) AS exp_end,
            AVG(production_kw)  AS avg_production_kw,
            AVG(grid_kw)        AS avg_grid_kw,
            MAX(cnt)            AS reading_count
        FROM bucketed
        GROUP BY hour_ts
        ORDER BY hour_ts
        """,
        (start_ts, end_ts),
    )

    rows = []
    for row in cursor.fetchall():
        (
            hour_ts,
            prod_start, prod_end,
            imp_start, imp_end,
            exp_start, exp_end,
            avg_prod, avg_grid,
            count,
        ) = row

        prod_kwh = _delta(prod_start, prod_end)
        imp_kwh = _delta(imp_start, imp_end)
        exp_kwh = _delta(exp_start, exp_end)
        cons_kwh = (prod_kwh or 0.0) + (imp_kwh or 0.0) - (exp_kwh or 0.0)

        rows.append({
            "hour_start": datetime.fromtimestamp(hour_ts),
            "production_kwh": prod_kwh,
            "grid_import_kwh": imp_kwh,
            "grid_export_kwh": exp_kwh,
            "consumption_kwh": cons_kwh if (prod_kwh is not None) else None,
            "avg_production_kw": avg_prod,
            "avg_grid_kw": avg_grid,
            "reading_count": count,
        })
    return rows


# --- Commands ---

def cmd_status(client: PVS6Client) -> None:
    """Print current real-time readings."""
    client.connect()
    print()
    r = client.get_readings()

    ts = datetime.fromtimestamp(r["timestamp"])
    print(f"  Time:           {ts.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Production:     {r['production_kw']:+.3f} kW")
    print(f"  Grid:           {r['grid_kw']:+.3f} kW  "
          f"({'importing' if r['grid_kw'] > 0 else 'exporting' if r['grid_kw'] < 0 else 'balanced'})")
    print(f"  Consumption:    {r['consumption_kw']:+.3f} kW")
    if r.get("production_lifetime_kwh") is not None:
        print(f"  Lifetime Solar: {r['production_lifetime_kwh']:.1f} kWh")
    if r.get("grid_imported_lifetime_kwh") is not None:
        print(f"  Lifetime Import:{r['grid_imported_lifetime_kwh']:.1f} kWh")
    if r.get("grid_exported_lifetime_kwh") is not None:
        print(f"  Lifetime Export:{r['grid_exported_lifetime_kwh']:.1f} kWh")
    panels = r.get("panels") or []
    print(f"  Panels reported: {len(panels)}")


def cmd_devices(client: PVS6Client) -> None:
    """Print the raw device list (useful for debugging meter assignment)."""
    client.connect()
    devices = client.get_device_list()
    print(f"\nFound {len(devices)} device(s):\n")
    for i, dev in enumerate(devices, 1):
        print(f"  Device {i}: {dev.get('DEVICE_TYPE', '?')} — {dev.get('MODEL', '?')}")
        print(f"    Serial:      {dev.get('SERIAL', '?')}")
        print(f"    State:       {dev.get('STATEDESCR', dev.get('STATE', '?'))}")
        print(f"    SW version:  {dev.get('SWVER', '?')}")
        numeric_fields = [
            "p_3phsum_kw", "ltea_3phsum_kwh", "net_ltea_3phsum_kwh",
            "pos_ltea_3phsum_kwh", "neg_ltea_3phsum_kwh",
            "i_3phsum_a", "vln_3phavg_v", "freq_hz",
        ]
        for field in numeric_fields:
            val = dev.get(field)
            if val is not None:
                print(f"    {field:<30} {val}")
        print()


def cmd_collect(client: PVS6Client, db_path: str, interval: int) -> None:
    """
    Poll the PVS6 at the given interval and store readings to SQLite.

    Run this continuously (e.g., in a tmux session or as a systemd service)
    to build a local history that the 'history' command can query.
    """
    conn = init_db(db_path)
    client.connect()

    print(f"\nPolling every {interval}s. Storing to: {db_path}")
    print("Press Ctrl-C to stop.\n")

    consecutive_errors = 0
 
    while True:
        start_time = time.time()   # mark loop start
        
        # watchdog added 04/06/2026
        
        #systemd.daemon.notify("WATCHDOG=1")

        try:
            r = client.get_readings()
            store_reading(conn, r)
            ts_int = int(r["timestamp"])
            panels = r.get("panels") or []
            store_panel_readings(conn, ts_int, panels)

            ts = datetime.fromtimestamp(r["timestamp"])
            print(
                f"[{ts.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"Production: {r['production_kw']:+.3f} kW  "
                f"Grid: {r['grid_kw']:+.3f} kW  "
                f"Consumption: {r['consumption_kw']:+.3f} kW  "
                f"Panels: {len(panels)}"
            )
            consecutive_errors = 0

        except PVS6AuthError:
            print("Session expired. Re-authenticating...")
            try:
                client.authenticate()
                consecutive_errors = 0
            except PVS6Error as e:
                print(f"Re-authentication failed: {e}")
                consecutive_errors += 1

        except PVS6Error as e:
            consecutive_errors += 1
            print(f"Error reading PVS6 (attempt {consecutive_errors}): {e}")
            if consecutive_errors >= 5:
                print("Too many consecutive errors. Check PVS6 connectivity.")

        except KeyboardInterrupt:
            print("\nStopped.")
            break

        # --- Stable interval timing ---
        elapsed = time.time() - start_time
        sleep_time = max(0, interval - elapsed)
        
        print(f"Loop duration: {elapsed:.2f}s, sleeping {sleep_time:.2f}s")
        
        time.sleep(sleep_time)

    conn.close()
    
def cmd_panels(client: PVS6Client) -> None:
    """Print a live table of per-panel inverter readings."""
    client.connect()
    print()

    r = client.get_readings()
    panels = r.get("panels") or []

    if not panels:
        print("No panel data found.")
        return

    print(f"Found {len(panels)} panels:\n")

    # Header
    print(
        f"{'Inverter':<16} {'AC kW':>7} {'DC kW':>7} "
        f"{'Vdc':>7} {'Idc':>7} {'TempC':>7} {'Lifetime kWh':>14}"
    )
    print("-" * 72)

    for p in panels:
        print(
            f"{p['inverter_serial']:<16} "
            f"{(p['ac_power_kw'] or 0):>7.3f} "
            f"{(p['dc_power_kw'] or 0):>7.3f} "
            f"{(p['dc_voltage_v'] or 0):>7.1f} "
            f"{(p['dc_current_a'] or 0):>7.2f} "
            f"{(p['heatsink_temp_c'] or 0):>7.1f} "
            f"{(p['lifetime_ac_kwh'] or 0):>14.3f}"
        )

def cmd_history(
    conn: sqlite3.Connection,
    start: Optional[datetime],
    end: Optional[datetime],
) -> None:
    """Print hourly energy report from the local SQLite database."""
    if start is None:
        row = conn.execute("SELECT MIN(timestamp) FROM readings").fetchone()
        start_ts = row[0] if row[0] else 0
    else:
        start_ts = int(start.timestamp())

    if end is None:
        end_ts = int(time.time())
    else:
        end_of_day = end.replace(hour=23, minute=59, second=59)
        end_ts = int(end_of_day.timestamp())

    rows = query_hourly(conn, start_ts, end_ts)

    if not rows:
        print("No data found for the specified range.")
        print("Run 'pvs6.py collect' to start collecting data.")
        return

    print(
        f"\n{'Hour':<20}  {'Solar':>8}  {'Import':>8}  {'Export':>8}  {'Consumed':>8}  {'Readings':>8}"
    )
    print(
        f"{'':.<20}  {'kWh':>8}  {'kWh':>8}  {'kWh':>8}  {'kWh':>8}  {'count':>8}"
    )
    print("-" * 75)

    totals = {k: 0.0 for k in ("production_kwh", "grid_import_kwh", "grid_export_kwh", "consumption_kwh")}

    for r in rows:
        prod = r["production_kwh"]
        imp = r["grid_import_kwh"]
        exp = r["grid_export_kwh"]
        cons = r["consumption_kwh"]

        def fmt(v):
            return f"{v:.3f}" if v is not None else "  N/A  "

        print(
            f"{r['hour_start'].strftime('%Y-%m-%d %H:%M'):<20}  "
            f"{fmt(prod):>8}  "
            f"{fmt(imp):>8}  "
            f"{fmt(exp):>8}  "
            f"{fmt(cons):>8}  "
            f"{r['reading_count']:>8}"
        )

        for key, val in (
            ("production_kwh", prod),
            ("grid_import_kwh", imp),
            ("grid_export_kwh", exp),
            ("consumption_kwh", cons),
        ):
            if val is not None:
                totals[key] += val

    print("-" * 75)
    print(
        f"{'TOTAL':<20}  "
        f"{totals['production_kwh']:>8.3f}  "
        f"{totals['grid_import_kwh']:>8.3f}  "
        f"{totals['grid_export_kwh']:>8.3f}  "
        f"{totals['consumption_kwh']:>8.3f}"
    )
    print(f"\n{len(rows)} hour(s) shown.")


# --- Helpers ---

def _float(value) -> Optional[float]:
    """Safely convert a value to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _delta(start, end) -> Optional[float]:
    """
    Return end - start, or None if either value is missing.
    Clamps to 0.0 to handle minor counter resets or rounding.
    """
    if start is None or end is None:
        return None
    delta = float(end) - float(start)
    return max(0.0, delta)


def _parse_build_from_swver(swver: str) -> int:
    """
    Parse the integer build number from a version string.
    Handles formats like:
      '2025.09.04.61845'       (old firmware, dot-separated)
      '2025.10, Build 61846'   (new firmware, comma + Build label)
    Returns 0 if the string cannot be parsed.
    """
    if not swver:
        return 0
    lower = swver.lower()
    if "build" in lower:
        idx = lower.index("build")
        candidate = swver[idx + len("build"):].strip()
        try:
            return int(candidate)
        except ValueError:
            pass
    parts = swver.strip().split(".")
    if len(parts) >= 4:
        try:
            return int(parts[-1])
        except ValueError:
            pass
    if len(parts) >= 1:
        try:
            val = int(parts[-1])
            if val > 1000:
                return val
        except ValueError:
            pass
    return 0


# --- CLI ---

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SunPower PVS6 local energy monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("PVS6_HOST", DEFAULT_HOST),
        help=f"PVS6 IP address (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--serial",
        default=os.environ.get("PVS6_SERIAL"),
        help="PVS6 serial number (required for firmware >= build 61840)",
    )
    parser.add_argument(
        "--db",
        default=os.environ.get("PVS6_DB", DEFAULT_DB),
        help=f"SQLite database file (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Print debug info (requests, cookies, response codes)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show current real-time readings")
    subparsers.add_parser("devices", help="Dump raw device list")
    subparsers.add_parser("panels", help="Show live per-panel inverter readings")

    collect_parser = subparsers.add_parser(
        "collect",
        help="Poll continuously and store to SQLite"
    )

    collect_parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"PVS6 IP address (default: {DEFAULT_HOST})"
    )

    collect_parser.add_argument(
        "--serial",
        help="PVS6 serial number (required for new firmware authentication)"
    )

    collect_parser.add_argument(
        "--db",
        default=DEFAULT_DB,
        help=f"SQLite database file (default: {DEFAULT_DB})"
    )

    collect_parser.add_argument(
        "--interval",
        type=int,
        default=int(os.environ.get("PVS6_INTERVAL", DEFAULT_INTERVAL)),
        help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL})"
    )

    collect_parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug info"
    )

    history_parser = subparsers.add_parser("history", help="Show hourly energy report from collected data")
    history_parser.add_argument(
        "--start",
        help="Start date (YYYY-MM-DD)",
    )
    history_parser.add_argument(
        "--end",
        help="End date (YYYY-MM-DD, inclusive)",
    )

    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    client = PVS6Client(
        host=args.host,
        serial=args.serial,
        debug=args.debug,
    )

    if args.command == "status":
        cmd_status(client)
    elif args.command == "devices":
        cmd_devices(client)
    elif args.command == "collect":
        cmd_collect(client, db_path=args.db, interval=args.interval)
    elif args.command == "panels":
        cmd_panels(client)
    elif args.command == "history":
        conn = sqlite3.connect(args.db)
        start_dt = datetime.strptime(args.start, "%Y-%m-%d") if args.start else None
        end_dt = datetime.strptime(args.end, "%Y-%m-%d") if args.end else None
        cmd_history(conn, start=start_dt, end=end_dt)
        conn.close()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
