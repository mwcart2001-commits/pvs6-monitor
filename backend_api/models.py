from pydantic import BaseModel
from typing import List
from pydantic import BaseModel

class SystemSnapshot(BaseModel):
    timestamp: str
    production_kw: float
    consumption_kw: float
    grid_kw: float
    lifetime_solar_kwh: float
    lifetime_import_kwh: float
    lifetime_export_kwh: float
    panel_count: int

class DayHistory(BaseModel):
    date: str
    system: List[SystemSnapshot]
    panels: List[List[PanelSnapshot]]

class PanelSnapshot(BaseModel):
    physical_label: str
    inverter_serial: str
    install_group: str

    # electrical metrics
    ac_power_kw: float | None
    dc_power_kw: float | None
    voltage_v: float | None
    temperature_c: float | None
    lifetime_ac_kwh: float | None

    # health scoring (optional)
    health_score: float | None = None
    normalized_output: float | None = None
    combined_score: float | None = None
    status: str | None = None

    # timestamp
    timestamp: int
