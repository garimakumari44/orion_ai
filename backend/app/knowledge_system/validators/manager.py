from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from knowledge_system.connectors.manager import ConnectorManager
from knowledge_system.ingestion.pipeline import ProcessingPipeline
from knowledge_system.storage.stores.document_store import DocumentStore
from knowledge_system.storage.stores.vector_store import VectorStore
from knowledge_system.storage.stores.graph_store import GraphStore
from knowledge_system.indexing.hybrid_index import HybridIndex
from knowledge_system.models.document import Document


class KnowledgeManager:
    """
    High-level entry point for the knowledge system.

    Responsibilities:
        • Import data from connectors
        • Run ingestion pipeline
        • Store processed documents
        • Build indexes
        • Search knowledge
    """

    def __init__(
        self,
        connector_manager: ConnectorManager,
        ingestion_pipeline: ProcessingPipeline,
        document_store: DocumentStore,
        vector_store: VectorStore,
        graph_store: GraphStore,
        hybrid_index: HybridIndex,
    ) -> None:

        self.connectors = connector_manager
        self.pipeline = ingestion_pipeline

        self.document_store = document_store
        self.vector_store = vector_store
        self.graph_store = graph_store

        self.index = hybrid_index

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    async def ingest_path(self, path: str | Path) -> List[Document]:
        """
        Load documents from a filesystem path.
        """

        documents = await self.connectors.load_path(path)

        processed = []

        for doc in documents:
            result = await self.pipeline.run(doc)

            await self.document_store.save(result)

            processed.append(result)

        return processed

    async def ingest_connector(
        self,
        connector_name: str,
        **kwargs,
    ) -> List[Document]:
        """
        Import from GitHub, Notion, Jira, etc.
        """

        documents = await self.connectors.load(
            connector_name,
            **kwargs,
        )

        processed = []

        for doc in documents:

            result = await self.pipeline.run(doc)

            await self.document_store.save(result)

            processed.append(result)

        return processed

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    async def rebuild_indexes(self) -> None:
        """
        Rebuild all search indexes.
        """

        documents = await self.document_store.list()

        await self.index.build(documents)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        top_k: int = 10,
    ):
        """
        Hybrid search.
        """

        return await self.index.search(
            query=query,
            top_k=top_k,
        )

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    async def get_document(
        self,
        document_id,
    ) -> Optional[Document]:
        return await self.document_store.get(document_id)

    async def delete_document(
        self,
        document_id,
    ) -> None:

        await self.document_store.delete(document_id)

    async def list_documents(self):
        return await self.document_store.list()

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    async def stats(self):

        return {
            "documents": await self.document_store.count(),
            "vectors": await self.vector_store.count(),
            "graph_nodes": await self.graph_store.node_count(),
            "graph_edges": await self.graph_store.edge_count(),
        }