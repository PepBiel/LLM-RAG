import hashlib
import re
from typing import Any

from app.core.config import Settings
from app.embeddings.base import EmbeddingProvider
from app.schemas.documents import DocumentIngestRequest, DocumentIngestResponse
from app.services.chunking import chunk_text
from app.services.document_loader import load_text_from_file
from app.vectorstore.base import VectorStore

SLUG_RE = re.compile(r"[^a-z0-9]+")


def build_document_id(title: str, text: str) -> str:
    slug = SLUG_RE.sub("-", title.lower()).strip("-")[:80] or "document"
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return f"{slug}-{digest}"


class IngestionService:
    def __init__(
        self,
        settings: Settings,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self._settings = settings
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def ingest(self, request: DocumentIngestRequest) -> DocumentIngestResponse:
        text = request.text or load_text_from_file(request.local_path or "")
        document_id = request.document_id or build_document_id(request.title, text)
        chunks = chunk_text(text, self._settings.chunk_size, self._settings.chunk_overlap)
        if not chunks:
            raise ValueError("Document has no indexable text.")

        embeddings = self._embedding_provider.embed_texts(chunks)
        ids = [f"{document_id}:chunk:{index:04d}" for index in range(len(chunks))]
        metadatas = [
            self._build_chunk_metadata(request, document_id, index, len(chunks))
            for index in range(len(chunks))
        ]

        self._vector_store.upsert(ids=ids, texts=chunks, embeddings=embeddings, metadatas=metadatas)
        return DocumentIngestResponse(
            document_id=document_id,
            title=request.title,
            chunks_indexed=len(chunks),
            collection_name=self._vector_store.collection_name,
            metadata={
                "embedding_provider": self._embedding_provider.model_name,
                "source_url": request.source_url,
                "topic": request.topic,
            },
        )

    @staticmethod
    def _build_chunk_metadata(
        request: DocumentIngestRequest,
        document_id: str,
        chunk_index: int,
        total_chunks: int,
    ) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "document_id": document_id,
            "title": request.title,
            "source_url": request.source_url,
            "publisher": request.publisher,
            "topic": request.topic,
            "crops": request.crops,
            "license_note": request.license_note,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
        }
        metadata.update(request.extra_metadata)
        return metadata

