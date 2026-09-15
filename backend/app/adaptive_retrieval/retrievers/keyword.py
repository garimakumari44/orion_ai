"""
Keyword Retriever

Supports:
- BM25
- Boolean search
- Metadata filtering
- Exact phrase search
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional

from .base import BaseRetriever
from app.knowledge_system.models.chunk  import Chunk
from app.knowledge_system.storage.stores.document_store import DocumentStore
from app.knowledge_system.indexing.keyword_index import KeywordIndex


class KeywordRetriever(BaseRetriever):
    """
    Keyword based retrieval.

    Uses inverted indexes instead of embeddings.
    """

    def __init__(
        self,
        keyword_index: KeywordIndex,
        document_store: DocumentStore,
    ):
        self.keyword_index = keyword_index
        self.document_store = document_store

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:

        chunk_ids = await self.keyword_index.search(
            query=query,
            top_k=top_k,
            filters=filters,
        )

        chunks = []

        for cid in chunk_ids:
            chunk = await self.document_store.get_chunk(cid)
            if chunk:
                chunks.append(chunk)

        return chunks

    async def phrase_search(
        self,
        phrase: str,
        top_k: int = 10,
    ) -> List[Chunk]:

        ids = await self.keyword_index.search_phrase(
            phrase,
            top_k,
        )

        return [
            await self.document_store.get_chunk(i)
            for i in ids
            if await self.document_store.get_chunk(i)
        ]

    async def boolean_search(
        self,
        expression: str,
        top_k: int = 10,
    ) -> List[Chunk]:

        ids = await self.keyword_index.boolean_search(
            expression,
            top_k,
        )

        return [
            await self.document_store.get_chunk(i)
            for i in ids
            if await self.document_store.get_chunk(i)
        ]