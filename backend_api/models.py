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
    physical_label: str
    inverter_serial: str
    install_group: str

    # electrical metrics
    ac_kw: float | None = None
    dc_kw: float | None = None
    vdc: float | None = None
    idc: float | None = None
    temp_c: float | None = None
    lifetime_kwh: float | None = None

    # scoring fields
    health_score: float | None = None
    normalized_output: float | None = None
    combined_score: float | None = None
    status: str | None = None

    # timestamp
    timestamp: int


class DayHistory(BaseModel):
    date: str
    system: List[SystemSnapshot]
    panels: List[List[PanelSnapshot]]
