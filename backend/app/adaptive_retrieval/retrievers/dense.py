"""
Dense Vector Retriever
"""

from __future__ import annotations

from typing import List, Optional

from app.knowledge_system.models.chunk import Chunk
from app.knowledge_system.storage.stores.vector_store  import VectorStore

from .base import BaseRetriever


class DenseRetriever(BaseRetriever):
    """
    Semantic search using embeddings.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        top_k: int = 10,
    ):
        super().__init__(top_k)

        self.vector_store = vector_store

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[dict] = None,
    ) -> List[Chunk]:

        results = await self.vector_store.search(
            query=query,
            top_k=top_k or self.top_k,
            filters=filters,
        )

        return results