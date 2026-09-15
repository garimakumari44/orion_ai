"""
app/memory/manager.py

Central Memory Manager.

Responsibilities:
- Own all memory stores
- Provide unified memory API
- Route memories to correct stores
- Manage memory CRUD operations
- Provide retrieval abstraction

Higher-level conversation/session/consolidation
logic belongs to MemoryService.
"""

from __future__ import annotations

import logging

from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
)

from .models.memory import (
    Memory,
    MemoryType,
)

from .stores.working import WorkingMemoryStore
from .stores.semantic import SemanticMemoryStore
from .stores.episodic import EpisodicMemoryStore
from .stores.procedural import ProceduralMemoryStore
from .stores.research import ResearchMemoryStore


logger = logging.getLogger(__name__)


class MemoryManager:

    def __init__(
        self,
        working_memory: Optional[WorkingMemoryStore] = None,
        semantic_memory: Optional[SemanticMemoryStore] = None,
        episodic_memory: Optional[EpisodicMemoryStore] = None,
        procedural_memory: Optional[ProceduralMemoryStore] = None,
        research_memory: Optional[ResearchMemoryStore] = None,
    ) -> None:

        self.working_memory = (
            working_memory
            if working_memory is not None
            else WorkingMemoryStore()
        )

        self.semantic_memory = (
            semantic_memory
            if semantic_memory is not None
            else SemanticMemoryStore()
        )

        self.episodic_memory = (
            episodic_memory
            if episodic_memory is not None
            else EpisodicMemoryStore()
        )

        self.procedural_memory = (
            procedural_memory
            if procedural_memory is not None
            else ProceduralMemoryStore()
        )

        self.research_memory = (
            research_memory
            if research_memory is not None
            else ResearchMemoryStore()
        )

        self._stores: Dict[
            MemoryType,
            object,
        ] = {}

        self._register_default_stores()

        logger.info(
            "Memory Manager initialized with %d stores",
            len(self._stores),
        )

    # =========================================================
    # Registration
    # =========================================================

    def _register_default_stores(self) -> None:

        self.register_store(
            MemoryType.WORKING,
            self.working_memory,
        )

        self.register_store(
            MemoryType.SEMANTIC,
            self.semantic_memory,
        )

        self.register_store(
            MemoryType.EPISODIC,
            self.episodic_memory,
        )

        # IMPORTANT:
        # Procedural memory was missing in your original code.
        self.register_store(
            MemoryType.PROCEDURAL,
            self.procedural_memory,
        )

        self.register_store(
            MemoryType.RESEARCH,
            self.research_memory,
        )

    def register_store(
        self,
        memory_type: MemoryType,
        store: object,
    ) -> None:

        self._stores[memory_type] = store

        logger.debug(
            "Registered %s memory store",
            memory_type.value,
        )

    def stores(self):
        return self._stores.items()

    def get_store(
        self,
        memory_type: MemoryType,
    ):
        if memory_type not in self._stores:
            raise ValueError(
                f"No store registered for {memory_type.value}"
            )

        return self._stores[memory_type]

    # =========================================================
    # CRUD
    # =========================================================

    def add(
        self,
        memory: Memory,
    ) -> None:

        store = self.get_store(
            memory.memory_type
        )

        add = getattr(
            store,
            "add",
            None,
        )

        if add is None:
            raise RuntimeError(
                f"{memory.memory_type.value} store "
                "does not support add()"
            )

        add(memory)

    def add_many(
        self,
        memories: Sequence[Memory],
    ) -> None:

        for memory in memories:
            self.add(memory)

    def remove(
        self,
        memory: Memory,
    ) -> bool:

        store = self.get_store(
            memory.memory_type
        )

        remove = getattr(
            store,
            "remove",
            None,
        )

        if remove is None:
            return False

        return bool(
            remove(memory)
        )

    def update(
        self,
        memory: Memory,
    ) -> bool:

        store = self.get_store(
            memory.memory_type
        )

        update = getattr(
            store,
            "update",
            None,
        )

        if update is not None:
            return bool(
                update(memory)
            )

        remove = getattr(
            store,
            "remove",
            None,
        )

        add = getattr(
            store,
            "add",
            None,
        )

        if add is None:
            return False

        if remove is not None:
            remove(memory)

        add(memory)

        return True

    def clear(
        self,
        memory_type: MemoryType,
    ) -> None:

        store = self.get_store(
            memory_type
        )

        clear = getattr(
            store,
            "clear",
            None,
        )

        if clear is not None:
            clear()

    # =========================================================
    # Retrieval
    # =========================================================

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        memory_types: Optional[
            Iterable[MemoryType]
        ] = None,
    ) -> List[Memory]:

        results: List[Memory] = []

        if memory_types is None:
            stores = list(
                self._stores.items()
            )
        else:
            stores = [
                (
                    memory_type,
                    self.get_store(memory_type),
                )
                for memory_type in memory_types
            ]

        for memory_type, store in stores:

            search = getattr(
                store,
                "search",
                None,
            )

            if search is None:
                continue

            try:

                memories = search(
                    query=query,
                    limit=limit,
                )

                if memories:
                    results.extend(memories)

            except Exception:

                logger.exception(
                    "Memory retrieval failed for %s",
                    memory_type.value,
                )

        return results[:limit]

    def retrieve_from_store(
        self,
        memory_type: MemoryType,
        query: str,
        limit: int = 5,
    ) -> List[Memory]:

        store = self.get_store(
            memory_type
        )

        search = getattr(
            store,
            "search",
            None,
        )

        if search is None:
            return []

        return search(
            query=query,
            limit=limit,
        )

    # =========================================================
    # Advanced Search
    # =========================================================

    def search(
        self,
        query: str,
        limit: int = 10,
        memory_types: Optional[
            Iterable[MemoryType]
        ] = None,
        min_importance: float = 0.0,
        rank: bool = True,
    ) -> List[Memory]:

        memories = self.retrieve(
            query=query,
            limit=max(
                limit * 3,
                limit,
            ),
            memory_types=memory_types,
        )

        if min_importance > 0:

            memories = [
                memory
                for memory in memories
                if getattr(
                    memory,
                    "importance",
                    0.0,
                ) >= min_importance
            ]

        if rank:
            memories = self.rank_memories(
                memories,
                query=query,
            )

        return memories[:limit]

    def retrieve_by_type(
        self,
        query: str,
        memory_type: MemoryType,
        limit: int = 5,
    ) -> List[Memory]:

        return self.retrieve(
            query=query,
            limit=limit,
            memory_types=[memory_type],
        )

    def retrieve_multiple_types(
        self,
        query: str,
        memory_types: Iterable[MemoryType],
        limit: int = 10,
    ) -> List[Memory]:

        return self.retrieve(
            query=query,
            limit=limit,
            memory_types=memory_types,
        )

    # =========================================================
    # Ranking
    # =========================================================

    def rank_memories(
        self,
        memories: List[Memory],
        query: Optional[str] = None,
    ) -> List[Memory]:

        def score(memory: Memory) -> float:

            retrieval_score = float(
                getattr(
                    memory,
                    "retrieval_score",
                    0.0,
                )
                or 0.0
            )

            importance = float(
                getattr(
                    memory,
                    "importance",
                    0.0,
                )
                or 0.0
            )

            recency = float(
                getattr(
                    memory,
                    "recency_score",
                    0.0,
                )
                or 0.0
            )

            access_count = int(
                getattr(
                    memory,
                    "access_count",
                    0,
                )
                or 0
            )

            return (
                retrieval_score * 0.55
                + importance * 0.25
                + recency * 0.15
                + min(
                    access_count / 100,
                    0.05,
                )
            )

        return sorted(
            memories,
            key=score,
            reverse=True,
        )

    # =========================================================
    # Context
    # =========================================================

    def build_context(
        self,
        query: str,
        limit: int = 8,
        memory_types: Optional[
            Iterable[MemoryType]
        ] = None,
    ) -> List[str]:

        memories = self.search(
            query=query,
            limit=limit,
            memory_types=memory_types,
        )

        return [
            content
            for memory in memories
            if (
                content := getattr(
                    memory,
                    "content",
                    None,
                )
            )
        ]

    def build_memory_context(
        self,
        query: str,
        limit: int = 8,
    ) -> str:

        context = self.build_context(
            query=query,
            limit=limit,
        )

        return "\n\n".join(context)

    # =========================================================
    # Planner Integration
    # =========================================================

    def planner_context(
        self,
        query: str,
        limit: int = 6,
    ) -> List[Memory]:

        return self.search(
            query=query,
            limit=limit,
            memory_types=[
                MemoryType.SEMANTIC,
                MemoryType.PROCEDURAL,
            ],
        )

    def planner_prompt_context(
        self,
        query: str,
        limit: int = 6,
    ) -> str:

        memories = self.planner_context(
            query=query,
            limit=limit,
        )

        return "\n\n".join(
            getattr(
                memory,
                "content",
                "",
            )
            for memory in memories
        )

    # =========================================================
    # Adaptive Retrieval Integration
    # =========================================================

    def retrieval_context(
        self,
        query: str,
        limit: int = 8,
    ) -> List[Memory]:

        return self.search(
            query=query,
            limit=limit,
            memory_types=[
                MemoryType.WORKING,
                MemoryType.SEMANTIC,
                MemoryType.EPISODIC,
                MemoryType.RESEARCH,
            ],
        )

    def retrieval_documents(
        self,
        query: str,
        limit: int = 8,
    ) -> List[dict]:

        memories = self.retrieval_context(
            query=query,
            limit=limit,
        )

        documents = []

        for memory in memories:

            documents.append(
                {
                    "id": getattr(
                        memory,
                        "id",
                        None,
                    ),
                    "text": getattr(
                        memory,
                        "content",
                        "",
                    ),
                    "score": getattr(
                        memory,
                        "retrieval_score",
                        0.0,
                    ),
                    "memory_type": (
                        memory.memory_type.value
                    ),
                    "metadata": getattr(
                        memory,
                        "metadata",
                        {},
                    ),
                }
            )

        return documents

    # =========================================================
    # Store Access
    # =========================================================

    def working(self) -> WorkingMemoryStore:
        return self.working_memory

    def semantic(self) -> SemanticMemoryStore:
        return self.semantic_memory

    def episodic(self) -> EpisodicMemoryStore:
        return self.episodic_memory

    def procedural(self) -> ProceduralMemoryStore:
        return self.procedural_memory

    def research(self) -> ResearchMemoryStore:
        return self.research_memory

    # =========================================================
    # Statistics
    # =========================================================

    def stats(self) -> Dict[str, int]:

        statistics: Dict[str, int] = {}

        for memory_type, store in self._stores.items():

            count = 0

            count_method = getattr(
                store,
                "count",
                None,
            )

            if count_method is not None:

                try:
                    count = int(
                        count_method()
                    )
                except Exception:
                    count = 0

            elif hasattr(store, "memories"):

                count = len(
                    store.memories
                )

            statistics[
                memory_type.value
            ] = count

        return statistics

    # =========================================================
    # Health
    # =========================================================

    def health(self) -> Dict[str, object]:

        stores = {}
        healthy = True

        for memory_type, store in self._stores.items():

            status = True

            health = getattr(
                store,
                "health",
                None,
            )

            if health is not None:

                try:
                    status = bool(
                        health()
                    )
                except Exception:
                    status = False

            stores[
                memory_type.value
            ] = status

            if not status:
                healthy = False

        return {
            "healthy": healthy,
            "stores": stores,
            "statistics": self.stats(),
        }

    def summary(self) -> Dict[str, object]:

        statistics = self.stats()

        long_term = (
            statistics.get("semantic", 0)
            + statistics.get("episodic", 0)
            + statistics.get("procedural", 0)
            + statistics.get("research", 0)
        )

        return {
            "statistics": statistics,
            "health": self.health(),
            "working_items": statistics.get(
                "working",
                0,
            ),
            "long_term_items": long_term,
        }

    # =========================================================
    # Maintenance
    # =========================================================

    def cleanup(self) -> Dict[str, int]:

        cleaned = {}

        for memory_type, store in self._stores.items():

            cleanup = getattr(
                store,
                "cleanup",
                None,
            )

            if cleanup is None:

                cleaned[
                    memory_type.value
                ] = 0

                continue

            try:

                cleaned[
                    memory_type.value
                ] = int(
                    cleanup()
                )

            except Exception:

                logger.exception(
                    "Cleanup failed for %s",
                    memory_type.value,
                )

                cleaned[
                    memory_type.value
                ] = 0

        return cleaned

    def optimize(self) -> Dict[str, object]:

        return {
            "cleanup": self.cleanup(),
            "statistics": self.stats(),
        }

    # =========================================================
    # Async Compatibility
    # =========================================================

    async def async_add(
        self,
        memory: Memory,
    ) -> None:

        self.add(memory)

    async def async_retrieve(
        self,
        *args,
        **kwargs,
    ) -> List[Memory]:

        return self.retrieve(
            *args,
            **kwargs,
        )

    async def async_search(
        self,
        *args,
        **kwargs,
    ) -> List[Memory]:

        return self.search(
            *args,
            **kwargs,
        )

    async def async_stats(
        self,
    ) -> Dict[str, int]:

        return self.stats()

    async def async_health(
        self,
    ) -> Dict[str, object]:

        return self.health()

    # =========================================================
    # Utility
    # =========================================================

    def __len__(self) -> int:
        return sum(
            self.stats().values()
        )

    def __contains__(
        self,
        memory_type: MemoryType,
    ) -> bool:

        return memory_type in self._stores

    def __repr__(self) -> str:

        stats = self.stats()

        return (
            f"{self.__class__.__name__}("
            f"working={stats.get('working', 0)}, "
            f"semantic={stats.get('semantic', 0)}, "
            f"episodic={stats.get('episodic', 0)}, "
            f"procedural={stats.get('procedural', 0)}, "
            f"research={stats.get('research', 0)}"
            ")"
        )