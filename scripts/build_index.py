import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402
from app.embeddings.factory import build_embedding_provider  # noqa: E402
from app.schemas.documents import DocumentIngestRequest  # noqa: E402
from app.services.ingestion_service import IngestionService  # noqa: E402
from app.vectorstore.chroma_store import ChromaVectorStore  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the persistent vector index from the demo corpus.")
    parser.add_argument("--manifest", default="app/data/corpus_manifest.yml", help="Path to corpus manifest YAML.")
    parser.add_argument("--reset", action="store_true", help="Delete and rebuild the Chroma collection.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    manifest_path = (ROOT / args.manifest).resolve()
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    embedding_provider = build_embedding_provider(settings)
    vector_store = ChromaVectorStore(path=settings.chroma_path, collection_name=settings.chroma_collection)
    if args.reset:
        vector_store.reset()

    ingestion_service = IngestionService(settings, embedding_provider, vector_store)
    indexed = []
    for document in manifest.get("documents", []):
        request = DocumentIngestRequest(**document)
        response = ingestion_service.ingest(request)
        indexed.append(response.model_dump())
        print(f"Indexed {response.document_id}: {response.chunks_indexed} chunks")

    print(
        json.dumps(
            {
                "documents_indexed": len(indexed),
                "total_chunks": vector_store.count_chunks(),
                "collection": vector_store.collection_name,
                "embedding_model": embedding_provider.model_name,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

