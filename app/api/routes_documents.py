from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_ingestion_service, get_vector_store
from app.schemas.documents import DocumentIngestRequest, DocumentIngestResponse, DocumentsListResponse
from app.services.ingestion_service import IngestionService
from app.vectorstore.base import VectorStore

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/ingest", response_model=DocumentIngestResponse)
def ingest_document(
    request: DocumentIngestRequest,
    ingestion_service: Annotated[IngestionService, Depends(get_ingestion_service)],
) -> DocumentIngestResponse:
    try:
        return ingestion_service.ingest(request)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=DocumentsListResponse)
def list_documents(vector_store: Annotated[VectorStore, Depends(get_vector_store)]) -> DocumentsListResponse:
    documents, total_chunks = vector_store.list_documents()
    return DocumentsListResponse(
        documents=documents,
        total_documents=len(documents),
        total_chunks=total_chunks,
    )
