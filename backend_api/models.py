from pydantic import BaseModel
from typing import List

class SystemSnapshot(BaseModel):
    timestamp: str
    production_kw: float
    consumption_kw: float
    grid_kw: float
    lifetime_solar_kwh: float
    lifetime_import_kwh: float
    lifetime_export_kwh: float
    panel_count: int


# MUST come before DayHistory
class PanelSnapshot(BaseModel):
    inverter_serial: str
    module_serial: str | None = None
    model: str | None = None
    state: str | None = None
    state_descr: str | None = None

    ac_power_kw: float | None = None
    dc_power_kw: float | None = None
    lifetime_ac_kwh: float | None = None

    ac_voltage_v: float | None = None
    ac_current_a: float | None = None
    dc_voltage_v: float | None = None
    dc_current_a: float | None = None

    heatsink_temp_c: float | None = None

    timestamp: int

    # scoring fields
    health_score: float | None = None
    normalized_output: float | None = None
    combined_score: float | None = None
    status: str | None = None

class DayHistory(BaseModel):
    date: str
    system: List[SystemSnapshot]
    panels: List[List[PanelSnapshot]]
