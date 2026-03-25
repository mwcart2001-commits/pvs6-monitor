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

class PanelSnapshot(BaseModel):
    inverter_serial: str
    physical_label: str
    install_group: str
    ac_kw: float
    dc_kw: float
    vdc: float
    idc: float
    temp_c: float
    lifetime_kwh: float
    #added for panel health stats
    health_score: float | None = None
    normalized_output: float | None = None
    combined_score: float | None = None
    status: str | None = None


class DayHistory(BaseModel):
    date: str
    system: List[SystemSnapshot]
    panels: List[List[PanelSnapshot]]
