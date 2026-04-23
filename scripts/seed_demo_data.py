import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402
from app.services.operations_service import OperationsService  # noqa: E402


def main() -> None:
    settings = get_settings()
    service = OperationsService(settings.demo_operations_path)
    payload = {
        "plots": [plot.model_dump() for plot in service.list_plots()],
        "total_plots": len(service.list_plots()),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

