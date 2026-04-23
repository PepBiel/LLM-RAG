import json
from pathlib import Path

from app.schemas.operations import Alert, Incident, Plot, PlotStatus, SensorReading


class OperationsService:
    def __init__(self, data_path: Path) -> None:
        self._data_path = data_path
        self._raw = self._load()
        self._plots = [Plot(**plot) for plot in self._raw.get("plots", [])]
        self._sensors = [SensorReading(**sensor) for sensor in self._raw.get("sensor_readings", [])]
        self._incidents = [Incident(**incident) for incident in self._raw.get("incidents", [])]
        self._alerts = [Alert(**alert) for alert in self._raw.get("alerts", [])]

    def _load(self) -> dict:
        if not self._data_path.exists():
            raise FileNotFoundError(f"Operations data not found: {self._data_path}")
        return json.loads(self._data_path.read_text(encoding="utf-8"))

    def list_plots(self) -> list[Plot]:
        return self._plots

    def get_plot_status(self, plot_id: str) -> PlotStatus:
        plot = next((item for item in self._plots if item.plot_id == plot_id), None)
        if plot is None:
            raise KeyError(f"Plot not found: {plot_id}")

        sensors = [item for item in self._sensors if item.plot_id == plot_id]
        latest_sensor = sorted(sensors, key=lambda item: item.timestamp, reverse=True)[0] if sensors else None
        incidents = [item for item in self._incidents if item.plot_id == plot_id]
        alerts = [item for item in self._alerts if item.plot_id == plot_id]
        return PlotStatus(plot=plot, latest_sensor=latest_sensor, incidents=incidents, alerts=alerts)

    def format_operational_context(self, plot_id: str) -> str:
        status = self.get_plot_status(plot_id)
        plot = status.plot
        lines = [
            f"Parcela: {plot.name} ({plot.plot_id})",
            f"Cultivo: {plot.crop}; variedad: {plot.variety or 'n/a'}; area_ha: {plot.area_ha}",
            f"Suelo: {plot.soil_type}; riego: {plot.irrigation_system}",
        ]

        if status.latest_sensor:
            sensor = status.latest_sensor
            lines.append(
                "Ultimo sensor: "
                f"humedad_suelo={sensor.soil_moisture_pct}%, "
                f"temp_aire={sensor.air_temperature_c}C, "
                f"temp_suelo={sensor.soil_temperature_c}C, "
                f"humedad_relativa={sensor.relative_humidity_pct}%, "
                f"timestamp={sensor.timestamp}"
            )

        if status.alerts:
            lines.append("Alertas abiertas:")
            lines.extend(f"- {alert.severity}: {alert.type} - {alert.message}" for alert in status.alerts)

        if status.incidents:
            lines.append("Incidencias:")
            lines.extend(
                f"- {incident.severity}: {incident.type} ({incident.status}) - {incident.notes}"
                for incident in status.incidents
            )

        return "\n".join(lines)

