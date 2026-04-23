from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AgroOps Copilot API"
    app_version: str = "0.1.0"
    environment: str = "local"

    llm_provider: str = Field(default="mock", description="mock, openrouter, openai or groq")
    llm_model: str = "mock-agronomy-advisor"
    llm_temperature: float = 0.2
    llm_timeout_seconds: float = 30.0

    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_site_url: str | None = None
    openrouter_app_name: str = "AgroOps Copilot API"

    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"

    groq_api_key: str | None = None
    groq_base_url: str = "https://api.groq.com/openai/v1"

    embedding_provider: str = Field(default="hash", description="hash or sentence-transformers")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimensions: int = 384

    chroma_path: Path = Path("data/chroma")
    chroma_collection: str = "agroops_documents"

    demo_operations_path: Path = Path("app/data/demo_operations.json")
    corpus_manifest_path: Path = Path("app/data/corpus_manifest.yml")

    rag_top_k: int = 5
    chunk_size: int = 900
    chunk_overlap: int = 150
    max_context_chars: int = 7_000


@lru_cache
def get_settings() -> Settings:
    return Settings()

