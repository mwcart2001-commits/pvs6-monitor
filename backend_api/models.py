from pydantic import BaseModel
from typing import List, Optional


class SystemSnapshot(BaseModel):
    timestamp: int
    production_kw: float
    consumption_kw: float
    grid_kw: float
    lifetime_solar_kwh: float
    lifetime_import_kwh: float
    lifetime_export_kwh: float
    panel_count: int


class PanelSnapshot(BaseModel):
    inverter_serial: str
    module_serial: Optional[str] = None
    model: Optional[str] = None
    state: Optional[str] = None
    state_descr: Optional[str] = None

    ac_power_kw: Optional[float] = None
    dc_power_kw: Optional[float] = None
    lifetime_ac_kwh: Optional[float] = None

    ac_voltage_v: Optional[float] = None
    ac_current_a: Optional[float] = None
    dc_voltage_v: Optional[float] = None
    dc_current_a: Optional[float] = None

    heatsink_temp_c: Optional[float] = None

    timestamp: int

    # Added fields
    physical_label: Optional[str] = None
    health_score: Optional[float] = None
    normalized_output: Optional[float] = None
    combined_score: Optional[float] = None
    status: Optional[str] = None

class DayHistory(BaseModel):
    date: str
    system: List[SystemSnapshot]
    panels: List[List[PanelSnapshot]]
