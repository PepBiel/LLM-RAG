from typing import Any

from pydantic import BaseModel, Field


class Source(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    source_url: str | None = None
    score: float = Field(ge=0.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievedContext(BaseModel):
    chunk_id: str
    text: str
    score: float = Field(ge=0.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=12)
    include_context: bool = False
    filters: dict[str, Any] | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    metadata: dict[str, Any] = Field(default_factory=dict)
    contexts: list[RetrievedContext] | None = None


class DiagnoseRequest(BaseModel):
    plot_id: str = Field(min_length=1)
    question: str = Field(
        default="Evalua el estado de la parcela y sugiere los primeros pasos operativos.",
        min_length=3,
        max_length=2_000,
    )
    top_k: int = Field(default=5, ge=1, le=12)
    include_context: bool = False

