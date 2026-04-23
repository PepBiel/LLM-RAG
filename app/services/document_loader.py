from pathlib import Path

SUPPORTED_TEXT_SUFFIXES = {".txt", ".md"}


def load_text_from_file(local_path: str) -> str:
    path = Path(local_path).expanduser().resolve()
    workspace = Path.cwd().resolve()
    if not path.is_relative_to(workspace):
        raise ValueError("local_path must be inside the project workspace.")
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Document not found: {local_path}")

    suffix = path.suffix.lower()
    if suffix in SUPPORTED_TEXT_SUFFIXES:
        return path.read_text(encoding="utf-8")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("pypdf is required to ingest PDF files.") from exc

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)

    raise ValueError(f"Unsupported document type: {suffix}. Use .txt, .md or .pdf.")

