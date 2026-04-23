from pathlib import Path

from app.services.operations_service import OperationsService


def test_operations_service_loads_demo_plot_status() -> None:
    service = OperationsService(Path("app/data/demo_operations.json"))

    status = service.get_plot_status("plot-north-tomato-01")

    assert status.plot.crop == "tomato"
    assert status.latest_sensor is not None
    assert status.alerts
    assert "North Tomato Block" in service.format_operational_context("plot-north-tomato-01")

