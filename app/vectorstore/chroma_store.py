import json
from pathlib import Path
from typing import Any

from app.vectorstore.base import VectorSearchResult


def _clean_metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool | None]:
    cleaned: dict[str, str | int | float | bool | None] = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            cleaned[key] = value
        else:
            cleaned[key] = json.dumps(value, ensure_ascii=False)
    return cleaned


def _parse_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for key, value in metadata.items():
        if isinstance(value, str) and value.startswith(("[", "{")):
            try:
                parsed[key] = json.loads(value)
                continue
            except json.JSONDecodeError:
                pass
        parsed[key] = value
    return parsed


class ChromaVectorStore:
    def __init__(self, path: Path, collection_name: str) -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("chromadb is not installed. Run `pip install -e .`.") from exc

        self._path = path
        self._collection_name = collection_name
        self._path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self._path))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def collection_name(self) -> str:
        return self._collection_name

    def upsert(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self._collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=[_clean_metadata(metadata) for metadata in metadatas],
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        where = _clean_metadata(filters) if filters else None
        result = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        results: list[VectorSearchResult] = []
        for item_id, document, metadata, distance in zip(ids, documents, metadatas, distances, strict=False):
            score = max(0.0, 1.0 - float(distance))
            results.append(
                VectorSearchResult(
                    id=item_id,
                    text=document or "",
                    score=round(score, 4),
                    metadata=_parse_metadata(metadata or {}),
                )
            )
        return results

    def list_documents(self) -> tuple[list[dict[str, Any]], int]:
        total_chunks = self.count_chunks()
        if total_chunks == 0:
            return [], 0

        raw = self._collection.get(include=["metadatas"], limit=total_chunks)
        documents: dict[str, dict[str, Any]] = {}
        for metadata in raw.get("metadatas", []):
            parsed = _parse_metadata(metadata or {})
            document_id = str(parsed.get("document_id", "unknown"))
            existing = documents.setdefault(
                document_id,
                {
                    "document_id": document_id,
                    "title": parsed.get("title", "Untitled"),
                    "source_url": parsed.get("source_url"),
                    "publisher": parsed.get("publisher"),
                    "topic": parsed.get("topic"),
                    "crops": parsed.get("crops", []),
                    "license_note": parsed.get("license_note"),
                    "chunks": 0,
                },
            )
            existing["chunks"] += 1
        return sorted(documents.values(), key=lambda item: item["document_id"]), total_chunks

    def count_chunks(self) -> int:
        return int(self._collection.count())

    def reset(self) -> None:
        self._client.delete_collection(self._collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
