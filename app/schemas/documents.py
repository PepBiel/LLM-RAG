from typing import Any

from pydantic import BaseModel, Field, model_validator


class DocumentIngestRequest(BaseModel):
    title: str = Field(min_length=2, max_length=240)
    text: str | None = Field(default=None, min_length=20)
    local_path: str | None = Field(default=None, description="Path to a local .txt, .md or .pdf file")
    document_id: str | None = Field(default=None, max_length=120)
    source_url: str | None = None
    publisher: str | None = None
    topic: str | None = None
    crops: list[str] = Field(default_factory=list)
    license_note: str | None = None
    extra_metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_text_or_path(self) -> "DocumentIngestRequest":
        if not self.text and not self.local_path:
            raise ValueError("Either text or local_path must be provided.")
        return self


class DocumentIngestResponse(BaseModel):
    document_id: str
    title: str
    chunks_indexed: int
    collection_name: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentSummary(BaseModel):
    document_id: str
    title: str
    source_url: str | None = None
    publisher: str | None = None
    topic: str | None = None
    crops: list[str] = Field(default_factory=list)
    chunks: int = 0
    license_note: str | None = None


class DocumentsListResponse(BaseModel):
    documents: list[DocumentSummary]
    total_documents: int
    total_chunks: int

