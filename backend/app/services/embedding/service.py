"""
Embedding Service.

High-level service responsible for generating embeddings.
"""

from __future__ import annotations

from typing import List

from app.knowledge_system.embeddings.cache import EmbeddingCache
from app.knowledge_system.embeddings.manager import EmbeddingManager
from .exceptions import (
    EmbeddingGenerationError,
    EmbeddingProviderNotFoundError,
)


class EmbeddingService:
    """
    High-level embedding service.

    Coordinates:
    - provider lookup
    - caching
    - embedding generation
    """

    def __init__(
        self,
        manager: EmbeddingManager,
        cache: EmbeddingCache | None = None,
    ) -> None:
        self.manager = manager
        self.cache = cache or EmbeddingCache()

    async def embed_query(
        self,
        text: str,
        provider: str,
    ) -> List[float]:
        """
        Generate an embedding for a single query.
        """
        cached = self.cache.get(text)
        if cached is not None:
            return cached

        try:
            model = self.manager.get(provider)
        except ValueError as exc:
            raise EmbeddingProviderNotFoundError(str(exc)) from exc

        try:
            embedding = await model.embed_query(text)
        except Exception as exc:
            raise EmbeddingGenerationError(
                f"Failed to embed query using '{provider}'."
            ) from exc

        self.cache.set(text, embedding)
        return embedding

    async def embed_documents(
        self,
        texts: List[str],
        provider: str,
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        """
        try:
            model = self.manager.get(provider)
        except ValueError as exc:
            raise EmbeddingProviderNotFoundError(str(exc)) from exc

        embeddings: List[List[float]] = []

        missing_texts: List[str] = []
        missing_indices: List[int] = []

        for index, text in enumerate(texts):
            cached = self.cache.get(text)

            if cached is None:
                missing_texts.append(text)
                missing_indices.append(index)
                embeddings.append([])
            else:
                embeddings.append(cached)

        if missing_texts:
            try:
                new_embeddings = await model.embed_documents(
                    missing_texts
                )
            except Exception as exc:
                raise EmbeddingGenerationError(
                    f"Failed to embed documents using '{provider}'."
                ) from exc

            for index, text, vector in zip(
                missing_indices,
                missing_texts,
                new_embeddings,
            ):
                embeddings[index] = vector
                self.cache.set(text, vector)

        return embeddings

    def clear_cache(self) -> None:
        """
        Clear cached embeddings.
        """
        self.cache.clear()