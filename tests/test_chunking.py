from app.services.chunking import chunk_text, normalize_text


def test_normalize_text_collapses_whitespace() -> None:
    assert normalize_text("a\n\n  b\tc") == "a b c"


def test_chunk_text_creates_overlapping_chunks() -> None:
    text = " ".join(f"word-{index}." for index in range(120))
    chunks = chunk_text(text, chunk_size=120, chunk_overlap=20)

    assert len(chunks) > 1
    assert all(len(chunk) <= 140 for chunk in chunks)
    assert chunks[0] != chunks[1]

