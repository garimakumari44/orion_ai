from __future__ import annotations

from threading import Lock
from typing import Dict, List, Optional

from app.memory.models.memory import Memory


class SemanticMemoryStore:
    """
    Stores semantic (fact) memories.

    Semantic memories represent stable facts extracted from
    conversations.

    Examples
    --------
    - User lives in Delhi.
    - User prefers Python.
    - Company uses PostgreSQL.
    """

    def __init__(self):
        self._memories: Dict[str, Memory] = {}
        self._lock = Lock()

    def add(self, memory: Memory) -> None:
        with self._lock:
            self._memories[memory.id] = memory

    def update(self, memory: Memory) -> None:
        with self._lock:
            self._memories[memory.id] = memory

    def get(self, memory_id: str) -> Optional[Memory]:
        return self._memories.get(memory_id)

    def remove(self, memory_id: str) -> bool:
        with self._lock:
            return self._memories.pop(memory_id, None) is not None

    def get_all(self) -> List[Memory]:
        return list(self._memories.values())

    def find_by_source(self, source: str) -> List[Memory]:
        return [
            m
            for m in self._memories.values()
            if getattr(m, "source", None) == source
        ]

    def clear(self) -> None:
        with self._lock:
            self._memories.clear()

    def __len__(self):
        return len(self._memories)

    def __iter__(self):
        return iter(self.get_all())