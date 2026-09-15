"""
app/knowledge_system/manager.py

Knowledge System Manager

Central facade for the Orion AI Research Intelligence System.

Used by:
- Research Planner
- Fundamental Agent
- Valuation Agent
- Macro Agent
- Risk Agent
- Investment Committee Agent

Responsibilities:
- Manage knowledge lifecycle
- Build research intelligence
- Expose storage/index access
- Provide a simple retrieval hook
- Coordinate knowledge services

The KnowledgeSystem does NOT own AdaptiveRetrievalManager.

Adaptive retrieval is a higher-level retrieval orchestration layer.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, TYPE_CHECKING

from app.knowledge_system.knowledge_builder import KnowledgeBuilder
from app.knowledge_system.connectors.manager import ConnectorManager
from app.knowledge_system.enrichment.manager import EnrichmentManager
from app.knowledge_system.indexing.manager import IndexManager
from app.knowledge_system.ingestion.manager import IngestionManager
from app.knowledge_system.storage.manager import StorageManager

if TYPE_CHECKING:
    from app.knowledge_system.types import (
        RetrievedDocument,
    )


logger = logging.getLogger(__name__)


class KnowledgeSystem:
    """
    Main Knowledge Intelligence Facade.

    Agents should interact with the knowledge infrastructure
    through this class rather than directly accessing internal
    managers.
    """

    def __init__(
        self,
        *,
        connectors: Optional[ConnectorManager] = None,
        ingestion: Optional[IngestionManager] = None,
        enrichment: Optional[EnrichmentManager] = None,
        storage: Optional[StorageManager] = None,
        indexing: Optional[IndexManager] = None,
        builder: Optional[KnowledgeBuilder] = None,
    ) -> None:

        # ---------------------------------------------------------
        # Core services
        # ---------------------------------------------------------

        self.connectors = (
            connectors
            if connectors is not None
            else ConnectorManager()
        )

        self.ingestion = (
            ingestion
            if ingestion is not None
            else IngestionManager()
        )

        self.enrichment = (
            enrichment
            if enrichment is not None
            else EnrichmentManager()
        )

        self.storage = (
            storage
            if storage is not None
            else StorageManager()
        )

        self.indexing = (
            indexing
            if indexing is not None
            else IndexManager()
        )

        # ---------------------------------------------------------
        # Knowledge builder
        # ---------------------------------------------------------

        self.builder = (
            builder
            if builder is not None
            else KnowledgeBuilder(
                connectors=self.connectors,
                ingestion=self.ingestion,
                enrichment=self.enrichment,
                storage=self.storage,
                indexing=self.indexing,
            )
        )

        # ---------------------------------------------------------
        # Lifecycle
        # ---------------------------------------------------------

        self._initialized = False

    # =========================================================
    # Lifecycle
    # =========================================================

    async def initialize(self) -> None:
        """
        Initialize all knowledge system components.
        """

        if self._initialized:
            return

        logger.info(
            "Initializing Research Knowledge System..."
        )

        try:
            await self.connectors.initialize()
            await self.ingestion.initialize()
            await self.enrichment.initialize()
            await self.storage.initialize()
            await self.indexing.initialize()

            self._initialized = True

            logger.info(
                "Research Knowledge System Ready."
            )

        except Exception:
            logger.exception(
                "Knowledge System initialization failed."
            )

            # Attempt partial cleanup.
            await self.shutdown()

            raise

    async def shutdown(self) -> None:
        """
        Shutdown all knowledge system components.
        """

        if not self._initialized:
            return

        logger.info(
            "Stopping Research Knowledge System..."
        )

        # Shutdown in reverse dependency order.

        try:
            if hasattr(self.indexing, "shutdown"):
                await self.indexing.shutdown()
        except Exception:
            logger.exception(
                "Failed to shutdown indexing."
            )

        try:
            if hasattr(self.storage, "close"):
                await self.storage.close()
            elif hasattr(self.storage, "shutdown"):
                await self.storage.shutdown()
        except Exception:
            logger.exception(
                "Failed to shutdown storage."
            )

        try:
            if hasattr(self.enrichment, "shutdown"):
                await self.enrichment.shutdown()
        except Exception:
            logger.exception(
                "Failed to shutdown enrichment."
            )

        try:
            if hasattr(self.ingestion, "shutdown"):
                await self.ingestion.shutdown()
        except Exception:
            logger.exception(
                "Failed to shutdown ingestion."
            )

        try:
            if hasattr(self.connectors, "shutdown"):
                await self.connectors.shutdown()
        except Exception:
            logger.exception(
                "Failed to shutdown connectors."
            )

        self._initialized = False

        logger.info(
            "Research Knowledge System stopped."
        )

    # =========================================================
    # Properties
    # =========================================================

    @property
    def initialized(self) -> bool:
        """
        Return whether the knowledge system is initialized.
        """

        return self._initialized

    # =========================================================
    # Research Building
    # =========================================================

    async def build_company(
        self,
        company: str,
        connector_name: str,
        config: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Build complete company intelligence.
        """

        if not self._initialized:
            await self.initialize()

        return await self.builder.build_company_research(
            company=company,
            connector_name=connector_name,
            config=config,
            **kwargs,
        )

    # =========================================================
    # Direct Storage Access
    # =========================================================

    @property
    def document_store(self):
        return getattr(
            self.storage,
            "document_store",
            None,
        )

    @property
    def vector_store(self):
        return getattr(
            self.storage,
            "vector_store",
            None,
        )

    @property
    def metadata_store(self):
        return getattr(
            self.storage,
            "metadata_store",
            None,
        )

    @property
    def cache_store(self):
        return getattr(
            self.storage,
            "cache_store",
            None,
        )

    # =========================================================
    # Index Access
    # =========================================================

    @property
    def keyword_index(self):
        return getattr(
            self.indexing,
            "keyword_index",
            None,
        )

    @property
    def vector_index(self):
        return getattr(
            self.indexing,
            "vector_index",
            None,
        )

    # =========================================================
    # Basic Knowledge Retrieval
    # =========================================================

    async def search_documents(
        self,
        query: str,
        *,
        company: Optional[str] = None,
        limit: int = 10,
    ) -> list:
        """
        Low-level document search.

        This is intentionally NOT the adaptive retrieval pipeline.

        AdaptiveRetrievalManager should orchestrate:
            analysis
            planning
            routing
            retrieval
            merging
            reranking
            compression
            context building
        """

        if not self._initialized:
            await self.initialize()

        results = []

        # ---------------------------------------------------------
        # Vector search
        # ---------------------------------------------------------

        vector_store = self.vector_store

        if vector_store is not None:

            try:

                if hasattr(vector_store, "search"):

                    vector_results = await _maybe_await(
                        vector_store.search(
                            query=query,
                            limit=limit,
                            company=company,
                        )
                    )

                    if vector_results:
                        results.extend(vector_results)

            except TypeError:

                # Fallback for simpler store APIs.
                try:

                    vector_results = await _maybe_await(
                        vector_store.search(
                            query=query,
                            limit=limit,
                        )
                    )

                    if vector_results:
                        results.extend(vector_results)

                except Exception:
                    logger.exception(
                        "Vector document search failed."
                    )

            except Exception:
                logger.exception(
                    "Vector document search failed."
                )

        # ---------------------------------------------------------
        # Keyword search
        # ---------------------------------------------------------

        keyword_index = self.keyword_index

        if keyword_index is not None:

            try:

                if hasattr(keyword_index, "search"):

                    keyword_results = await _maybe_await(
                        keyword_index.search(
                            query=query,
                            limit=limit,
                        )
                    )

                    if keyword_results:
                        results.extend(keyword_results)

            except Exception:
                logger.exception(
                    "Keyword document search failed."
                )

        return results[:limit]

    # Backwards-compatible API.

    async def research(
        self,
        query: str,
        company: Optional[str] = None,
        limit: int = 10,
    ) -> list:
        """
        Basic knowledge retrieval API.

        For full adaptive retrieval use:

            AdaptiveRetrievalManager.retrieve(...)
        """

        return await self.search_documents(
            query=query,
            company=company,
            limit=limit,
        )

    # =========================================================
    # Health
    # =========================================================

    async def health(self) -> dict[str, Any]:
        """
        Return knowledge system health information.
        """

        storage_health: dict[str, Any] = {}

        if hasattr(self.storage, "health"):

            try:

                storage_health = await _maybe_await(
                    self.storage.health()
                )

            except Exception:
                logger.exception(
                    "Storage health check failed."
                )

                storage_health = {
                    "healthy": False,
                }

        return {
            "system": "research_intelligence",
            "initialized": self._initialized,
            "services": {
                "connectors": True,
                "ingestion": True,
                "enrichment": True,
                "storage": True,
                "indexing": True,
            },
            "storage": storage_health,
        }


async def _maybe_await(value):
    """
    Support both synchronous and asynchronous service methods.
    """

    import inspect

    if inspect.isawaitable(value):
        return await value

    return value