from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Deque, List, Optional

from app.memory.models.memory import Memory


class WorkingMemoryStore:
    """
    Short-term working memory.

    Keeps only the most recent memories.

    Example
    -------
    store.add(memory)

    recent = store.get_recent(10)

    store.clear()
    """

    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self._items: Deque[Memory] = deque(maxlen=capacity)
        self._lock = Lock()

    def add(self, memory: Memory) -> None:
        with self._lock:
            self._items.append(memory)

    def extend(self, memories: List[Memory]) -> None:
        with self._lock:
            self._items.extend(memories)

    def get_recent(self, limit: Optional[int] = None) -> List[Memory]:
        with self._lock:
            items = list(self._items)

        if limit is None:
            return items

        return items[-limit:]

    def get_all(self) -> List[Memory]:
        with self._lock:
            return list(self._items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def size(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self.get_all())