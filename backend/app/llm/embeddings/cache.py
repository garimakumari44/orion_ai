"""
Embedding cache.

Provides a backend-agnostic cache interface.

Current implementation:
    • In-memory dictionary

Future replacements:
    • Redis
    • SQLite
    • DiskCache
    • DynamoDB
"""

from __future__ import annotations

import hashlib
from threading import Lock
from typing import Dict, List, Optional


class EmbeddingCache:
    """
    Thread-safe in-memory cache for embeddings.
    """

    def __init__(self):
        self._cache: Dict[str, List[float]] = {}
        self._lock = Lock()

    @staticmethod
    def _make_key(
        text: str,
        model: str,
    ) -> str:
        """
        Create a deterministic cache key from model + text.
        """

        key = f"{model}:{text}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def get(
        self,
        text: str,
        model: str,
    ) -> Optional[List[float]]:
        """
        Retrieve an embedding if present.
        """

        key = self._make_key(text, model)

        with self._lock:
            return self._cache.get(key)

    def set(
        self,
        text: str,
        model: str,
        embedding: List[float],
    ) -> None:
        """
        Store an embedding.
        """

        key = self._make_key(text, model)

        with self._lock:
            self._cache[key] = embedding

    def contains(
        self,
        text: str,
        model: str,
    ) -> bool:
        """
        Check whether an embedding is cached.
        """

        key = self._make_key(text, model)

        with self._lock:
            return key in self._cache

    def delete(
        self,
        text: str,
        model: str,
    ) -> None:
        """
        Remove one cached embedding.
        """

        key = self._make_key(text, model)

        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        """
        Remove all cached embeddings.
        """

        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """
        Number of cached embeddings.
        """

        with self._lock:
            return len(self._cache)