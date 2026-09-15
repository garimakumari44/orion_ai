"""
Embedding cache.

Caches embeddings by text to avoid repeated computation.
"""

from __future__ import annotations

import hashlib
from typing import Dict, List


class EmbeddingCache:
    """
    Simple in-memory cache for embeddings.

    Can later be replaced with Redis, SQLite,
    or another persistent backend.
    """

    def __init__(self) -> None:
        self._cache: Dict[str, List[float]] = {}

    @staticmethod
    def _key(text: str) -> str:
        """
        Generate a stable cache key.
        """
        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    def get(
        self,
        text: str,
    ) -> List[float] | None:
        """
        Retrieve a cached embedding.
        """
        return self._cache.get(self._key(text))

    def set(
        self,
        text: str,
        embedding: List[float],
    ) -> None:
        """
        Store an embedding.
        """
        self._cache[self._key(text)] = embedding

    def contains(
        self,
        text: str,
    ) -> bool:
        """
        Check whether an embedding exists.
        """
        return self._key(text) in self._cache

    def remove(
        self,
        text: str,
    ) -> None:
        """
        Remove an embedding.
        """
        self._cache.pop(self._key(text), None)

    def clear(self) -> None:
        """
        Clear the cache.
        """
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)