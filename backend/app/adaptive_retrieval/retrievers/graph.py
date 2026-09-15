"""
Knowledge Graph Retriever

Retrieves information by traversing entity relationships.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional

from .base import BaseRetriever



from app.knowledge_system.models.chunk  import Chunk
from app.knowledge_system.storage.stores.document_store import DocumentStore
from app.knowledge_system.storage.stores.graph_store import  GraphStore


class GraphRetriever(BaseRetriever):

    def __init__(
        self,
        graph_store: GraphStore,
        document_store: DocumentStore,
    ):
        self.graph_store = graph_store
        self.document_store = document_store

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        hops: int = 2,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:

        entities = await self.graph_store.extract_entities(query)

        visited_chunks = set()

        for entity in entities:

            chunk_ids = await self.graph_store.traverse(
                entity=entity,
                hops=hops,
            )

            visited_chunks.update(chunk_ids)

        results = []

        for cid in list(visited_chunks)[:top_k]:

            chunk = await self.document_store.get_chunk(cid)

            if chunk:
                results.append(chunk)

        return results

    async def neighbors(
        self,
        entity: str,
        hops: int = 1,
    ):

        return await self.graph_store.get_neighbors(
            entity,
            hops,
        )

    async def shortest_path(
        self,
        source: str,
        target: str,
    ):

        return await self.graph_store.shortest_path(
            source,
            target,
        )