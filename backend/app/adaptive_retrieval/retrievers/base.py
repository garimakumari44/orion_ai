"""
Base Retriever Interface

Every retriever should inherit from BaseRetriever.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
from app.knowledge_system.models.chunk  import Chunk


class BaseRetriever(ABC):
    """
    Abstract retrieval interface.
    """

    def __init__(self, top_k: int = 10):
        self.top_k = top_k

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        **kwargs,
    ) -> List[Chunk]:
        """
        Retrieve relevant chunks.
        """
        raise NotImplementedError

    async def __call__(
        self,
        query: str,
        top_k: Optional[int] = None,
        **kwargs,
    ) -> List[Chunk]:
        return await self.retrieve(
            query=query,
            top_k=top_k,
            **kwargs,
        )