from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_diagnosis_service, get_rag_service
from app.schemas.ask import AskRequest, AskResponse, DiagnoseRequest
from app.services.diagnosis_service import DiagnosisService
from app.services.rag_service import RagService

router = APIRouter(tags=["rag"])


@router.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    rag_service: Annotated[RagService, Depends(get_rag_service)],
) -> AskResponse:
    try:
        return rag_service.answer(
            question=request.question,
            top_k=request.top_k,
            include_context=request.include_context,
            filters=request.filters,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/diagnose", response_model=AskResponse)
def diagnose(
    request: DiagnoseRequest,
    diagnosis_service: Annotated[DiagnosisService, Depends(get_diagnosis_service)],
) -> AskResponse:
    try:
        return diagnosis_service.diagnose(
            plot_id=request.plot_id,
            question=request.question,
            top_k=request.top_k,
            include_context=request.include_context,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
