from functools import lru_cache

from app.core.config import Settings, get_settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.factory import build_embedding_provider
from app.llm.base import LLMProvider
from app.llm.factory import build_llm_provider
from app.services.diagnosis_service import DiagnosisService
from app.services.ingestion_service import IngestionService
from app.services.operations_service import OperationsService
from app.services.rag_service import RagService
from app.vectorstore.base import VectorStore
from app.vectorstore.chroma_store import ChromaVectorStore


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    return build_embedding_provider(get_settings())


@lru_cache
def get_vector_store() -> VectorStore:
    settings = get_settings()
    return ChromaVectorStore(path=settings.chroma_path, collection_name=settings.chroma_collection)


@lru_cache
def get_llm_provider() -> LLMProvider:
    return build_llm_provider(get_settings())


@lru_cache
def get_operations_service() -> OperationsService:
    return OperationsService(get_settings().demo_operations_path)


def get_rag_service() -> RagService:
    settings: Settings = get_settings()
    return RagService(
        settings=settings,
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
        llm_provider=get_llm_provider(),
    )


def get_ingestion_service() -> IngestionService:
    return IngestionService(
        settings=get_settings(),
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
    )


def get_diagnosis_service() -> DiagnosisService:
    return DiagnosisService(operations_service=get_operations_service(), rag_service=get_rag_service())

