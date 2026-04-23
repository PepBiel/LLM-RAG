from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_operations_service
from app.schemas.operations import PlotsListResponse, PlotStatus
from app.services.operations_service import OperationsService

router = APIRouter(prefix="/operations", tags=["operations"])


@router.get("/plots", response_model=PlotsListResponse)
def list_plots(
    operations_service: Annotated[OperationsService, Depends(get_operations_service)],
) -> PlotsListResponse:
    plots = operations_service.list_plots()
    return PlotsListResponse(plots=plots, total=len(plots))


@router.get("/plots/{plot_id}/status", response_model=PlotStatus)
def get_plot_status(
    plot_id: str,
    operations_service: Annotated[OperationsService, Depends(get_operations_service)],
) -> PlotStatus:
    try:
        return operations_service.get_plot_status(plot_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
