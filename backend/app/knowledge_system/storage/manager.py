"""
Storage manager.

Acts as the single entry point into the storage layer.

Instead of talking directly to Postgres, Neo4j,
Qdrant, etc., the rest of the application uses
StorageManager.
"""

from __future__ import annotations

from typing import Optional

from .stores.document_store import DocumentStore
from .stores.vector_store import VectorStore
from .stores.graph_store import GraphStore
from .stores.metadata_store import MetadataStore
from .stores.cache_store import CacheStore

from .transaction import StorageTransaction


class StorageManager:
    """
    Coordinates every storage backend.
    """

    def __init__(
        self,
        document_store: Optional[DocumentStore] = None,
        vector_store: Optional[VectorStore] = None,
        graph_store: Optional[GraphStore] = None,
        metadata_store: Optional[MetadataStore] = None,
        cache_store: Optional[CacheStore] = None,
    ):

        self.document_store = document_store
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.metadata_store = metadata_store
        self.cache_store = cache_store

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:

        for store in self._stores():
            if store:
                await store.initialize()

    async def close(self) -> None:

     for store in self._stores():

         if not store:
            continue

         close = getattr(
            store,
            "close",
            None,
        )

         if close:

            result = close()

            if hasattr(result, "__await__"):
                await result

    # ------------------------------------------------------------------
    # transactions
    # ------------------------------------------------------------------

    def transaction(self) -> StorageTransaction:
        """
        Return a generic transaction.

        Specific stores can override this
        with their own implementation.
        """
        return StorageTransaction()

    # ------------------------------------------------------------------
    # health
    # ------------------------------------------------------------------

    async def health(self) -> dict:

        report = {}

        for store in self._stores():

            if store is None:
                continue

            try:
                report[store.name] = await store.health()

            except Exception as e:
                report[store.name] = {
                    "status": "error",
                    "message": str(e),
                }

        return report

    # ------------------------------------------------------------------
    # utilities
    # ------------------------------------------------------------------

    def _stores(self):

        return (
            self.document_store,
            self.vector_store,
            self.graph_store,
            self.metadata_store,
            self.cache_store,
        )