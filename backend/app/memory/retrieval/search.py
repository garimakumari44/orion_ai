"""
memory/retrieval/search.py

Memory search engine.

Coordinates multiple retrieval backends and returns
candidate memories for ranking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class SearchResult:
    """
    Result returned from a memory search.
    """

    query: str
    memories: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def count(self) -> int:
        return len(self.memories)


class MemorySearcher:
    """
    High-level retrieval orchestrator.

    Supports multiple retrieval backends such as:
        - Vector search
        - Keyword search
        - Graph search
        - Recent memory search
    """

    def __init__(
        self,
        vector_store: Optional[Any] = None,
        keyword_store: Optional[Any] = None,
        graph_store: Optional[Any] = None,
    ) -> None:

        self.vector_store = vector_store
        self.keyword_store = keyword_store
        self.graph_store = graph_store

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def search(
        self,
        query: str,
        *,
        top_k: int = 10,
        use_vector: bool = True,
        use_keyword: bool = True,
        use_graph: bool = False,
    ) -> SearchResult:
        """
        Retrieve candidate memories.
        """

        candidates: List[Any] = []

        if use_vector:
            candidates.extend(
                self.vector_search(query, top_k)
            )

        if use_keyword:
            candidates.extend(
                self.keyword_search(query, top_k)
            )

        if use_graph:
            candidates.extend(
                self.graph_search(query, top_k)
            )

        candidates = self.deduplicate(candidates)

        return SearchResult(
            query=query,
            memories=candidates[:top_k],
            metadata={
                "vector": use_vector,
                "keyword": use_keyword,
                "graph": use_graph,
                "retrieved": len(candidates),
            },
        )

    # ------------------------------------------------------------------ #
    # Individual retrieval methods
    # ------------------------------------------------------------------ #

    def vector_search(
        self,
        query: str,
        top_k: int,
    ) -> List[Any]:

        if self.vector_store is None:
            return []

        if hasattr(self.vector_store, "search"):
            return self.vector_store.search(
                query=query,
                top_k=top_k,
            )

        return []

    def keyword_search(
        self,
        query: str,
        top_k: int,
    ) -> List[Any]:

        if self.keyword_store is None:
            return []

        if hasattr(self.keyword_store, "search"):
            return self.keyword_store.search(
                query=query,
                top_k=top_k,
            )

        return []

    def graph_search(
        self,
        query: str,
        top_k: int,
    ) -> List[Any]:

        if self.graph_store is None:
            return []

        if hasattr(self.graph_store, "search"):
            return self.graph_store.search(
                query=query,
                top_k=top_k,
            )

        return []

    # ------------------------------------------------------------------ #
    # Utilities
    # ------------------------------------------------------------------ #

    def deduplicate(
        self,
        memories: Iterable[Any],
    ) -> List[Any]:
        """
        Remove duplicate memories.

        Duplicate detection uses the memory id.
        """

        unique = {}

        for memory in memories:
            memory_id = getattr(memory, "id", id(memory))
            unique[memory_id] = memory

        return list(unique.values())