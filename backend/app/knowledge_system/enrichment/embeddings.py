"""
Embedding generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class DummyEmbeddingProvider(EmbeddingProvider):
    """
    Useful for testing.
    """

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        return [
            [0.0] * 384
            for _ in texts
        ]


class EmbeddingService:

    def __init__(
        self,
        provider: EmbeddingProvider,
    ) -> None:

        self.provider = provider

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.provider.embed(texts)