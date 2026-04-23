from app.embeddings.hash_provider import HashEmbeddingProvider


def test_hash_embeddings_are_deterministic() -> None:
    provider = HashEmbeddingProvider(dimensions=32)

    first = provider.embed_query("soil moisture tomato")
    second = provider.embed_query("soil moisture tomato")

    assert first == second
    assert len(first) == 32
    assert any(value != 0 for value in first)

