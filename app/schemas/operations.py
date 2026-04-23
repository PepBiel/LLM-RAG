from pydantic import BaseModel, Field


class Plot(BaseModel):
    plot_id: str
    name: str
    crop: str
    variety: str | None = None
    area_ha: float = Field(gt=0)
    soil_type: str
    irrigation_system: str
    latitude: float | None = None
    longitude: float | None = None


class SensorReading(BaseModel):
    sensor_id: str
    plot_id: str
    timestamp: str
    soil_moisture_pct: float
    air_temperature_c: float
    soil_temperature_c: float
    relative_humidity_pct: float
    battery_pct: float


class Incident(BaseModel):
    incident_id: str
    plot_id: str
    observed_at: str
    type: str
    severity: str
    status: str
    notes: str


class Alert(BaseModel):
    alert_id: str
    plot_id: str
    created_at: str
    type: str
    severity: str
    message: str


class PlotStatus(BaseModel):
    plot: Plot
    latest_sensor: SensorReading | None = None
    incidents: list[Incident] = Field(default_factory=list)
    alerts: list[Alert] = Field(default_factory=list)


class PlotsListResponse(BaseModel):
    plots: list[Plot]
    total: int

