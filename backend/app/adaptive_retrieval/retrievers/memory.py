"""
Memory Retriever

Retrieves relevant chunks from conversation or retrieval history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.knowledge_system.models.chunk import Chunk




@dataclass
class MemoryEntry:
    query: str
    chunks: List[Chunk]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MemoryRetriever:
    """
    Stores previous retrievals for reuse.
    """

    def __init__(self, memory_manager: Any,):
        self._history: List[MemoryEntry] = []
        self.memory_manager = memory_manager

    def add(
        self,
        query: str,
        chunks: List[Chunk],
    ) -> None:
        self._history.append(
            MemoryEntry(
                query=query,
                chunks=chunks,
            )
        )

    def retrieve(
        self,
        query: str,
    ) -> Optional[List[Chunk]]:
        """
        Exact query lookup.
        """

        for entry in reversed(self._history):
            if entry.query == query:
                return entry.chunks

        return None

    def recent(
        self,
        limit: int = 5,
    ) -> List[MemoryEntry]:
        return self._history[-limit:]

    def clear(self):
        self._history.clear()

    @property
    def size(self) -> int:
        return len(self._history)