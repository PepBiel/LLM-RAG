import hashlib
import math
import re

TOKEN_RE = re.compile(r"\w+", re.UNICODE)


class HashEmbeddingProvider:
    """Deterministic offline embeddings for local demos and tests.

    This is not a semantic model. It keeps the system runnable without API keys
    or model downloads. For stronger retrieval, set EMBEDDING_PROVIDER to
    sentence-transformers.
    """

    def __init__(self, dimensions: int = 384) -> None:
        self._dimensions = dimensions

    @property
    def model_name(self) -> str:
        return f"hashing-{self._dimensions}"

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        vector = [0.0] * self._dimensions
        tokens = [token.lower() for token in TOKEN_RE.findall(text)]
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "big") % self._dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
