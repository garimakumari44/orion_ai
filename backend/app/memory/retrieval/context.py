"""
memory/retrieval/context.py

Context builder for retrieved memories.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class RetrievalContext:
    """
    Final context assembled from retrieved memories.
    """

    query: str
    memories: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def count(self) -> int:
        return len(self.memories)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "count": self.count,
            "memories": self.memories,
            "metadata": self.metadata,
        }


class ContextBuilder:
    """
    Builds the final retrieval context.
    """

    def __init__(
        self,
        max_memories: int = 10,
    ) -> None:
        self.max_memories = max_memories

    def build(
        self,
        query: str,
        memories: Iterable[Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RetrievalContext:
        """
        Build a retrieval context.
        """

        selected = list(memories)[: self.max_memories]

        return RetrievalContext(
            query=query,
            memories=selected,
            metadata=metadata or {},
        )

    def group_by_type(
        self,
        memories: Iterable[Any],
    ) -> Dict[str, List[Any]]:
        """
        Group memories by their type.
        """

        grouped: Dict[str, List[Any]] = {}

        for memory in memories:
            memory_type = getattr(memory, "memory_type", "unknown")

            grouped.setdefault(memory_type, []).append(memory)

        return grouped

    def filter_by_score(
        self,
        memories: Iterable[Any],
        minimum_score: float,
    ) -> List[Any]:
        """
        Remove memories below a ranking threshold.
        """

        return [
            memory
            for memory in memories
            if getattr(memory, "ranking_score", 0.0) >= minimum_score
        ]

    def filter_by_type(
        self,
        memories: Iterable[Any],
        memory_type: str,
    ) -> List[Any]:
        """
        Return only memories of a specific type.
        """

        return [
            memory
            for memory in memories
            if getattr(memory, "memory_type", None) == memory_type
        ]