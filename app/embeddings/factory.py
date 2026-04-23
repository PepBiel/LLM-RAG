from app.core.config import Settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.hash_provider import HashEmbeddingProvider
from app.embeddings.sentence_transformers_provider import SentenceTransformersEmbeddingProvider


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    provider = settings.embedding_provider.lower()
    if provider in {"hash", "hashing"}:
        return HashEmbeddingProvider(dimensions=settings.embedding_dimensions)
    if provider in {"sentence-transformers", "sentence_transformers", "sbert"}:
        return SentenceTransformersEmbeddingProvider(settings.embedding_model)
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")

