"""
Main embedding interface.

All application code should use EmbeddingClient instead of talking
directly to any provider.
"""

from __future__ import annotations

from typing import List, Sequence

from .providers import EmbeddingProvider


class EmbeddingClient:
    """
    High-level embedding client.

    Example:
        client = EmbeddingClient(provider)

        vector = client.embed_text("Hello")

        vectors = client.embed_documents(
            ["doc1", "doc2", "doc3"]
        )
    """

    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single piece of text.
        """
        return self.provider.embed(text)

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> List[List[float]]:
        """
        Embed multiple documents.
        """
        return self.provider.embed_batch(list(texts))

    def dimensions(self) -> int:
        """
        Return embedding dimension.
        """
        return self.provider.dimension

    @property
    def model_name(self) -> str:
        return self.provider.model_name