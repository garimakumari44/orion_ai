from __future__ import annotations

from threading import Lock
from typing import Dict, List, Optional

from app.memory.models.research import ResearchMemory


class ResearchMemoryStore:
    """
    Stores long-term research artifacts.

    Examples
    --------
    - Papers
    - Literature reviews
    - Notes
    - Citations
    - Experiments
    """

    def __init__(self):
        self._research: Dict[str, ResearchMemory] = {}
        self._lock = Lock()

    def add(self, memory: ResearchMemory) -> None:
        with self._lock:
            self._research[memory.id] = memory

    def update(self, memory: ResearchMemory) -> None:
        with self._lock:
            self._research[memory.id] = memory

    def get(self, memory_id: str) -> Optional[ResearchMemory]:
        return self._research.get(memory_id)

    def remove(self, memory_id: str) -> bool:
        with self._lock:
            return self._research.pop(memory_id, None) is not None

    def get_all(self) -> List[ResearchMemory]:
        return list(self._research.values())

    def search_topic(self, topic: str) -> List[ResearchMemory]:
        topic = topic.lower()

        return [
            r
            for r in self._research.values()
            if topic in r.title.lower()
            or topic in getattr(r, "summary", "").lower()
        ]

    def recent(self, limit: int = 10) -> List[ResearchMemory]:
        items = sorted(
            self._research.values(),
            key=lambda x: x.updated_at,
            reverse=True,
        )

        return items[:limit]

    def clear(self):
        with self._lock:
            self._research.clear()

    def __len__(self):
        return len(self._research)

    def __iter__(self):
        return iter(self.get_all())