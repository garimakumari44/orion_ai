"""
app/adaptive_retrieval/manager.py

Main orchestration layer for adaptive retrieval.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.knowledge_system.manager import KnowledgeSystem
from app.knowledge_system.types import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedDocument,
    RetrievalStrategy,
)

from .config import AdaptiveRetrievalConfig
from .router import QueryRouter
from .planner.query_analyzer import QueryAnalyzer
from .planner.retrieval_planner import RetrievalPlanner
from .ranking.reranker import ResultReranker
from .ranking.result_merger import ResultMerger
from .retrievers.manager import RetrievalManager
from .compression.contextual import ContextualCompressor
from .context.builder import ContextBuilder


logger = logging.getLogger(__name__)


class AdaptiveRetrievalManager:
    """
    Central orchestration layer for adaptive retrieval.

    Pipeline

        Query
          |
          v
    Query Analyzer
          |
          v
    Retrieval Planner
          |
          v
    Query Router
          |
          v
    Retrieval Manager
          |
          v
    Result Merger
          |
          v
    Reranker
          |
          v
    Compressor
          |
          v
    Context Builder
          |
          v
    RetrievalResponse
    """

    def __init__(
        self,
        config: Optional[AdaptiveRetrievalConfig] = None,
        knowledge_system: Optional[KnowledgeSystem] = None,
        router: Optional[QueryRouter] = None,
        analyzer: Optional[QueryAnalyzer] = None,
        planner: Optional[RetrievalPlanner] = None,
        retriever: Optional[RetrievalManager] = None,
        merger: Optional[ResultMerger] = None,
        reranker: Optional[ResultReranker] = None,
        compressor: Optional[ContextualCompressor] = None,
        context_builder: Optional[ContextBuilder] = None,
    ) -> None:

        self.config = (
            config
            if config is not None
            else AdaptiveRetrievalConfig()
        )

        self.knowledge_system = (
            knowledge_system
            if knowledge_system is not None
            else KnowledgeSystem()
        )

        self.router = (
            router
            if router is not None
            else QueryRouter()
        )

        self.analyzer = (
            analyzer
            if analyzer is not None
            else QueryAnalyzer()
        )

        self.planner = (
            planner
            if planner is not None
            else RetrievalPlanner()
        )

        self.retriever = (
            retriever
            if retriever is not None
            else RetrievalManager(
                knowledge_system=self.knowledge_system,
            )
        )

        self.merger = (
            merger
            if merger is not None
            else ResultMerger()
        )

        self.reranker = (
            reranker
            if reranker is not None
            else ResultReranker()
        )

        self.compressor = (
            compressor
            if compressor is not None
            else ContextualCompressor(
                self.config
            )
        )

        self.context_builder = (
            context_builder
            if context_builder is not None
            else ContextBuilder(
                self.config
            )
        )

        self._initialized = False

    # =========================================================
    # Lifecycle
    # =========================================================

    async def initialize(self) -> None:
        """
        Initialize retrieval dependencies.
        """

        if self._initialized:
            return

        await self.knowledge_system.initialize()

        for component in (
            self.router,
            self.analyzer,
            self.planner,
            self.retriever,
            self.merger,
            self.reranker,
            self.compressor,
            self.context_builder,
        ):

            initialize = getattr(
                component,
                "initialize",
                None,
            )

            if initialize is not None:
                result = initialize()

                if hasattr(result, "__await__"):
                    await result

        self._initialized = True

        logger.info(
            "Adaptive Retrieval Manager initialized."
        )

    # =========================================================
    # Public API
    # =========================================================

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:
        """
        Execute complete adaptive retrieval pipeline.
        """

        if not self._initialized:
            await self.initialize()

        # -----------------------------------------------------
        # Query Analysis
        # -----------------------------------------------------

        analysis = await self.analyzer.analyze(
            request.query
        )

        # -----------------------------------------------------
        # Retrieval Planning
        # -----------------------------------------------------

        retrieval_plan = await self.planner.plan(
            request=request,
            analysis=analysis,
        )

        # -----------------------------------------------------
        # Strategy Routing
        # -----------------------------------------------------

        strategy = self.router.route(
            analysis=analysis,
            request=request,
        )

        # -----------------------------------------------------
        # Retrieval
        # -----------------------------------------------------

        retrieved_documents = await self.retriever.retrieve(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
            use_hybrid=retrieval_plan.use_hybrid,
            use_memory=retrieval_plan.use_memory,
            use_graph=retrieval_plan.use_graph,
            use_metadata=retrieval_plan.use_metadata,
            use_temporal=retrieval_plan.use_temporal,
        )

        # -----------------------------------------------------
        # Merge
        # -----------------------------------------------------

        merged = await self.merger.merge(
            retrieved_documents
        )

        # -----------------------------------------------------
        # Rerank
        # -----------------------------------------------------

        ranked = await self.reranker.rerank(
            query=request.query,
            documents=merged,
        )

        # -----------------------------------------------------
        # Compress
        # -----------------------------------------------------

        compressed = await self.compressor.compress(
            query=request.query,
            documents=ranked,
        )

        # -----------------------------------------------------
        # Build final context
        # -----------------------------------------------------

        final_documents = await self.context_builder.build(
            query=request.query,
            documents=compressed,
        )

        return RetrievalResponse(
            query=request.query,
            strategy=strategy,
            documents=final_documents,
            metadata={
                "analysis": analysis,
                "strategy": str(strategy),
                "retrieval_plan": retrieval_plan.to_dict(),
                "retrieved_documents": len(
                    retrieved_documents
                ),
                "merged_documents": len(merged),
                "returned_documents": len(
                    final_documents
                ),
            },
        )

    # =========================================================
    # Simple Search API
    # =========================================================

    async def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[RetrievedDocument]:
        """
        Simple retrieval API.
        """

        response = await self.retrieve(
            RetrievalRequest(
                query=query,
                top_k=top_k,
            )
        )

        return response.documents

    # =========================================================
    # Explicit Strategy
    # =========================================================

    async def retrieve_with_strategy(
        self,
        query: str,
        strategy: RetrievalStrategy,
        top_k: int = 10,
    ) -> List[RetrievedDocument]:
        """
        Execute retrieval using an explicitly selected strategy.
        """

        if not self._initialized:
            await self.initialize()

        docs = await self.retriever.retrieve(
            query=query,
            top_k=top_k,
            use_hybrid=(
                strategy == RetrievalStrategy.HYBRID
            ),
            use_graph=(
                strategy == RetrievalStrategy.GRAPH
            ),
            use_memory=(
                strategy == RetrievalStrategy.MEMORY
            ),
            use_metadata=(
                strategy == RetrievalStrategy.METADATA
            ),
            use_temporal=(
                strategy == RetrievalStrategy.TEMPORAL
            ),
        )

        merged = await self.merger.merge(
            docs
        )

        ranked = await self.reranker.rerank(
            query=query,
            documents=merged,
        )

        compressed = await self.compressor.compress(
            query=query,
            documents=ranked,
        )

        return await self.context_builder.build(
            query=query,
            documents=compressed,
        )

    # =========================================================
    # Health
    # =========================================================

    async def health(self) -> Dict[str, Any]:
        """
        Return health of complete retrieval pipeline.
        """

        return {
            "initialized": self._initialized,
            "knowledge_system":
                await self.knowledge_system.health(),

            "router":
                await _health(self.router),

            "planner":
                await _health(self.planner),

            "retriever":
                await _health(self.retriever),

            "merger":
                await _health(self.merger),

            "reranker":
                await _health(self.reranker),

            "compressor":
                await _health(self.compressor),

            "context_builder":
                await _health(self.context_builder),

            "analyzer":
                await _health(self.analyzer),
        }

    # =========================================================
    # Cleanup
    # =========================================================

    async def close(self) -> None:
        """
        Shutdown retrieval pipeline.
        """

        components = (
            self.context_builder,
            self.compressor,
            self.reranker,
            self.merger,
            self.retriever,
            self.planner,
            self.analyzer,
            self.router,
        )

        for component in components:

            close = getattr(
                component,
                "close",
                None,
            )

            if close is None:
                continue

            try:

                result = close()

                if hasattr(result, "__await__"):
                    await result

            except Exception:

                logger.exception(
                    "Failed to close %s",
                    component.__class__.__name__,
                )

        await self.knowledge_system.shutdown()

        self._initialized = False


async def _health(component: Any) -> Dict[str, Any]:
    """
    Safely call component health().
    """

    health = getattr(
        component,
        "health",
        None,
    )

    if health is None:
        return {
            "available": True,
        }

    try:

        result = health()

        if hasattr(result, "__await__"):
            result = await result

        if isinstance(result, dict):
            return result

        return {
            "healthy": bool(result),
        }

    except Exception as exc:

        logger.exception(
            "Health check failed for %s",
            component.__class__.__name__,
        )

        return {
            "healthy": False,
            "error": str(exc),
        }