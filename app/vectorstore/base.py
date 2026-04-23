from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class VectorSearchResult:
    id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStore(Protocol):
    @property
    def collection_name(self) -> str:
        ...

    def upsert(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        ...

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        ...

    def list_documents(self) -> tuple[list[dict[str, Any]], int]:
        ...

    def count_chunks(self) -> int:
        ...

    def reset(self) -> None:
        ...

