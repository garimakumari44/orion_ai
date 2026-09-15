"""
Sparse Keyword Retriever

Supports BM25 / Elasticsearch / OpenSearch.
"""

from __future__ import annotations

from typing import List, Optional

from app.knowledge_system.models.chunk import Chunk
from app.knowledge_system.storage.stores.document_store import DocumentStore

from .base import BaseRetriever


class SparseRetriever(BaseRetriever):
    """
    Keyword retrieval.
    """

    def __init__(
        self,
        document_store: DocumentStore,
        top_k: int = 10,
    ):
        super().__init__(top_k)

        self.document_store = document_store

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[dict] = None,
    ) -> List[Chunk]:

        return await self.document_store.keyword_search(
            query=query,
            top_k=top_k or self.top_k,
            filters=filters,
        )