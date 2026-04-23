from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_vector_store
from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse
from app.vectorstore.base import VectorStore

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(
    settings: Annotated[Settings, Depends(get_settings)],
    vector_store: Annotated[VectorStore, Depends(get_vector_store)],
) -> HealthResponse:
    checks = {
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "embedding_provider": settings.embedding_provider,
        "vector_collection": vector_store.collection_name,
        "indexed_chunks": vector_store.count_chunks(),
    }
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        app_version=settings.app_version,
        environment=settings.environment,
        checks=checks,
    )
