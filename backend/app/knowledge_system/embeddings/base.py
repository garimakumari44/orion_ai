"""
Base interface for embedding models.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingModel(ABC):
    """
    Base class for embedding providers.

    Every provider must implement methods for embedding
    documents and user queries.
    """

    @property
    @abstractmethod
    def provider(self) -> str:
        """Unique provider name."""
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector dimension."""
        raise NotImplementedError

    @abstractmethod
    async def embed_documents(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """
        Embed multiple documents.

        Args:
            texts:
                List of document strings.

        Returns:
            List of embedding vectors.
        """
        raise NotImplementedError

    @abstractmethod
    async def embed_query(
        self,
        text: str,
    ) -> List[float]:
        """
        Embed a single search query.
        """
        raise NotImplementedError