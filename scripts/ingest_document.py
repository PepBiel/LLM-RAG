import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402
from app.embeddings.factory import build_embedding_provider  # noqa: E402
from app.schemas.documents import DocumentIngestRequest  # noqa: E402
from app.services.ingestion_service import IngestionService  # noqa: E402
from app.vectorstore.chroma_store import ChromaVectorStore  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest one local document into the vector index.")
    parser.add_argument("local_path", help="Path to .md, .txt or .pdf file inside the project workspace.")
    parser.add_argument("--title", help="Document title. Defaults to filename stem.")
    parser.add_argument("--document-id", help="Stable document id.")
    parser.add_argument("--source-url", help="Source URL for traceability.")
    parser.add_argument("--publisher", help="Publisher or owner.")
    parser.add_argument("--topic", help="Topic metadata.")
    parser.add_argument("--crop", action="append", default=[], help="Crop metadata. Can be repeated.")
    parser.add_argument("--license-note", help="License or attribution note.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    embedding_provider = build_embedding_provider(settings)
    vector_store = ChromaVectorStore(path=settings.chroma_path, collection_name=settings.chroma_collection)
    ingestion_service = IngestionService(settings, embedding_provider, vector_store)

    local_path = Path(args.local_path)
    request = DocumentIngestRequest(
        title=args.title or local_path.stem.replace("_", " ").replace("-", " ").title(),
        local_path=str(local_path),
        document_id=args.document_id,
        source_url=args.source_url,
        publisher=args.publisher,
        topic=args.topic,
        crops=args.crop,
        license_note=args.license_note,
    )
    response = ingestion_service.ingest(request)
    print(json.dumps(response.model_dump(), indent=2))


if __name__ == "__main__":
    main()

