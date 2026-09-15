"""
Retrieval Manager

Coordinates all retrieval strategies using the Knowledge System
and the long-term Memory System.
"""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from app.knowledge_system.manager import KnowledgeSystem
from app.knowledge_system.models.chunk import Chunk

# Memory
from app.memory.manager import MemoryManager

from .bm25 import BM25Retriever
from .dense import DenseRetriever
from .graph import GraphRetriever
from .hybrid import HybridRetriever
from .keyword import KeywordRetriever
from .memory import MemoryRetriever
from .metadata import MetadataRetriever
from .multi_source import MultiSourceRetriever
from .sparse import SparseRetriever
from .temporal import TemporalRetriever


class RetrievalManager:
    """
    Central orchestration layer for every retrieval strategy.

    Responsibilities
    ----------------
    • Dense retrieval
    • Sparse retrieval
    • Keyword retrieval
    • Graph retrieval
    • Memory retrieval
    • Hybrid fusion
    • Metadata filtering
    • Temporal ranking
    """

    def __init__(
        self,
        knowledge_system: Optional[KnowledgeSystem] = None,
        memory_manager: Optional[MemoryManager] = None,
    ) -> None:

        self.knowledge_system = knowledge_system or KnowledgeSystem()
        self.memory_manager = memory_manager or MemoryManager()

        storage = self.knowledge_system.storage
        indexing = self.knowledge_system.indexing

        # ---------------------------------------------------------
        # Base Retrievers
        # ---------------------------------------------------------

        self.dense = DenseRetriever(
            vector_store=storage.vector_store,
        )

        self.sparse = SparseRetriever(
            document_store=storage.document_store,
        )

        self.keyword = KeywordRetriever(
            keyword_index=indexing.keyword_index,
            document_store=storage.document_store,
        )

        self.graph = GraphRetriever(
            graph_store=storage.graph_store,
            document_store=storage.document_store,
        )

        self.bm25 = BM25Retriever()

        self.metadata = MetadataRetriever()

        self.temporal = TemporalRetriever()

        self.memory = MemoryRetriever(
            memory_manager=self.memory_manager,
        )

        self.multi_source = MultiSourceRetriever()

        self.hybrid = HybridRetriever(
            dense=self.dense,
            sparse=self.sparse,
            keyword=self.keyword,
            graph=self.graph,
        )

    # ============================================================
    # Retrieval
    # ============================================================

    async def retrieve(
        self,
        query: str,
        *,
        use_memory: bool = True,
        use_hybrid: bool = True,
        use_graph: bool = False,
        use_metadata: bool = False,
        use_temporal: bool = False,
        top_k: int = 10,
        filters: Optional[dict] = None,
        memory_types: Optional[List[str]] = None,
    ) -> List[Chunk]:
        """
        Execute retrieval pipeline.

        Pipeline

        1. Memory
        2. Hybrid
        3. Graph
        4. Merge
        5. Metadata filter
        6. Temporal rerank
        7. Store interaction into memory
        """

        retrievals: Dict[str, List[Chunk]] = {}

        tasks = []

        # ---------------------------------------------------------
        # Memory Retrieval
        # ---------------------------------------------------------

        if use_memory:

            tasks.append(
                asyncio.create_task(
                    self.memory.retrieve(
                        query=query,
                        top_k=top_k,
                        memory_types=memory_types,
                    )
                )
            )

        # ---------------------------------------------------------
        # Hybrid Retrieval
        # ---------------------------------------------------------

        if use_hybrid:

            tasks.append(
                asyncio.create_task(
                    self.hybrid.retrieve(
                        query=query,
                        top_k=top_k,
                    )
                )
            )

        # ---------------------------------------------------------
        # Graph Retrieval
        # ---------------------------------------------------------

        if use_graph:

            tasks.append(
                asyncio.create_task(
                    self.graph.retrieve(
                        query=query,
                        top_k=top_k,
                        filters=filters,
                    )
                )
            )

        # ---------------------------------------------------------
        # Execute Concurrent Retrieval
        # ---------------------------------------------------------

        results = await asyncio.gather(
            *tasks,
            return_exceptions=False,
        )

        index = 0

        if use_memory:
            retrievals["memory"] = results[index]
            index += 1

        if use_hybrid:
            retrievals["hybrid"] = results[index]
            index += 1

        if use_graph:
            retrievals["graph"] = results[index]

        # ---------------------------------------------------------
        # Merge
        # ---------------------------------------------------------

        merged = self.multi_source.merge(retrievals)

        # ---------------------------------------------------------
        # Metadata filtering
        # ---------------------------------------------------------

        if use_metadata:

            merged = self.metadata.retrieve(
                merged,
                filters=filters,
            )

        # ---------------------------------------------------------
        # Temporal reranking
        # ---------------------------------------------------------

        if use_temporal:

            merged = self.temporal.retrieve_latest(
                merged,
                limit=top_k,
            )

        merged = merged[:top_k]

        # ---------------------------------------------------------
        # Store successful retrieval in memory
        # ---------------------------------------------------------

        if use_memory:

            await self.memory.store_interaction(
                query=query,
                retrieved_chunks=merged,
            )

        return merged

    # ============================================================
    # Memory
    # ============================================================

    async def clear_memory(self) -> None:
        """
        Clears every memory store.
        """
        await self.memory.clear()

    # ============================================================
    # Health
    # ============================================================

    async def health(self) -> dict:

        return {
            "knowledge_system": self.knowledge_system.initialized,
            "memory_system": await self.memory.health(),
            "vector_store": self.knowledge_system.storage.vector_store is not None,
            "document_store": self.knowledge_system.storage.document_store is not None,
            "graph_store": self.knowledge_system.storage.graph_store is not None,
            "keyword_index": self.knowledge_system.indexing.keyword_index is not None,
        }

    # ============================================================
    # Shutdown
    # ============================================================

    async def close(self) -> None:

        await self.memory.close()