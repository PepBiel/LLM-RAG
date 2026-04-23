from typing import Any

from fastapi.testclient import TestClient

from app.api import dependencies
from app.main import app
from app.schemas.ask import AskResponse
from app.vectorstore.base import VectorSearchResult


class FakeVectorStore:
    collection_name = "test_collection"

    def count_chunks(self) -> int:
        return 3

    def list_documents(self) -> tuple[list[dict[str, Any]], int]:
        return (
            [
                {
                    "document_id": "doc-1",
                    "title": "Demo doc",
                    "source_url": None,
                    "publisher": "test",
                    "topic": "irrigation",
                    "crops": [],
                    "chunks": 3,
                    "license_note": None,
                }
            ],
            3,
        )

    def upsert(self, ids, texts, embeddings, metadatas) -> None:  # type: ignore[no-untyped-def]
        return None

    def search(self, query_embedding, top_k, filters=None):  # type: ignore[no-untyped-def]
        return [
            VectorSearchResult(
                id="doc-1:chunk:0000",
                text="Irrigation context",
                score=0.9,
                metadata={"document_id": "doc-1", "title": "Demo doc"},
            )
        ]

    def reset(self) -> None:
        return None


class FakeRagService:
    def answer(self, question: str, top_k: int, include_context: bool, filters=None, **kwargs):  # type: ignore[no-untyped-def]
        return AskResponse(answer=f"answered: {question}", sources=[], metadata={"top_k": top_k})


def test_health_endpoint_contract() -> None:
    app.dependency_overrides[dependencies.get_vector_store] = lambda: FakeVectorStore()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["checks"]["indexed_chunks"] == 3
    app.dependency_overrides.clear()


def test_ask_endpoint_contract() -> None:
    app.dependency_overrides[dependencies.get_rag_service] = lambda: FakeRagService()
    client = TestClient(app)

    response = client.post("/ask", json={"question": "How should I inspect irrigation?", "top_k": 3})

    assert response.status_code == 200
    assert response.json()["answer"].startswith("answered:")
    app.dependency_overrides.clear()

