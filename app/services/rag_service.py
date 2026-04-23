from typing import Any

from app.core.config import Settings
from app.core.timing import Timer
from app.embeddings.base import EmbeddingProvider
from app.llm.base import LLMMessage, LLMProvider
from app.schemas.ask import AskResponse, RetrievedContext, Source
from app.vectorstore.base import VectorSearchResult, VectorStore

SYSTEM_PROMPT = """Eres AgroOps Copilot, un asistente de IA para operaciones agricolas.
Usa el contexto agronomico recuperado y los datos operativos cuando esten disponibles.
Se practico, explicito con la incertidumbre y no finjas emitir un diagnostico agronomico certificado.
Si la evidencia es insuficiente, di que informacion falta y sugiere comprobaciones de campo.
Responde en el mismo idioma que la pregunta del usuario cuando sea posible."""


class RagService:
    def __init__(
        self,
        settings: Settings,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        llm_provider: LLMProvider,
    ) -> None:
        self._settings = settings
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._llm_provider = llm_provider

    def answer(
        self,
        question: str,
        top_k: int,
        include_context: bool,
        filters: dict[str, Any] | None = None,
        operational_context: str | None = None,
        search_query: str | None = None,
    ) -> AskResponse:
        timer = Timer()
        query_embedding = self._embedding_provider.embed_query(search_query or question)
        results = self._vector_store.search(query_embedding=query_embedding, top_k=top_k, filters=filters)
        prompt = self._build_user_prompt(question, results, operational_context)
        llm_response = self._llm_provider.generate(
            [
                LLMMessage(role="system", content=SYSTEM_PROMPT),
                LLMMessage(role="user", content=prompt),
            ]
        )

        contexts = [
            RetrievedContext(
                chunk_id=result.id,
                text=result.text,
                score=result.score,
                metadata=result.metadata,
            )
            for result in results
        ]
        return AskResponse(
            answer=llm_response.content,
            sources=[self._to_source(result) for result in results],
            metadata={
                "latency_ms": timer.elapsed_ms,
                "llm_provider": llm_response.provider,
                "llm_model": llm_response.model,
                "embedding_model": self._embedding_provider.model_name,
                "collection": self._vector_store.collection_name,
                "top_k": top_k,
                "retrieved_chunks": len(results),
                "used_operational_context": operational_context is not None,
                "input_tokens": llm_response.input_tokens,
                "output_tokens": llm_response.output_tokens,
            },
            contexts=contexts if include_context else None,
        )

    def _build_user_prompt(
        self,
        question: str,
        results: list[VectorSearchResult],
        operational_context: str | None,
    ) -> str:
        context_blocks: list[str] = []
        used_chars = 0
        for index, result in enumerate(results, start=1):
            title = result.metadata.get("title", "Untitled")
            source_url = result.metadata.get("source_url", "n/a")
            block = (
                f"[S{index}] title={title}; source_url={source_url}; score={result.score}\n"
                f"{result.text}"
            )
            if used_chars + len(block) > self._settings.max_context_chars:
                break
            context_blocks.append(block)
            used_chars += len(block)

        docs_context = "\n\n".join(context_blocks) or "No document context retrieved."
        ops_context = operational_context or "No operational context provided."
        return f"""PREGUNTA
{question}

DATOS OPERATIVOS
{ops_context}

CONTEXTO DOCUMENTAL
{docs_context}

INSTRUCCIONES
- Responde con recomendaciones operativas priorizadas.
- Cita los titulos de las fuentes usadas cuando sean relevantes.
- No inventes valores que no esten en datos operativos o documentos.
- Si falta informacion, di que dato revisarias despues."""

    @staticmethod
    def _to_source(result: VectorSearchResult) -> Source:
        metadata = result.metadata
        return Source(
            document_id=str(metadata.get("document_id", "unknown")),
            chunk_id=result.id,
            title=str(metadata.get("title", "Untitled")),
            source_url=metadata.get("source_url"),
            score=result.score,
            metadata={
                "publisher": metadata.get("publisher"),
                "topic": metadata.get("topic"),
                "crops": metadata.get("crops", []),
                "chunk_index": metadata.get("chunk_index"),
                "license_note": metadata.get("license_note"),
            },
        )
