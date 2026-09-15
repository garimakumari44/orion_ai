from __future__ import annotations

from threading import Lock
from typing import Dict, List, Optional

from app.memory.models.memory import Memory


class ProceduralMemoryStore:
    """
    Stores procedural knowledge.

    Examples
    --------
    - User's coding workflow
    - Multi-step execution plans
    - Agent procedures
    - Tool usage patterns
    """

    def __init__(self):
        self._procedures: Dict[str, Memory] = {}
        self._lock = Lock()

    def add(self, procedure: Memory) -> None:
        with self._lock:
            self._procedures[procedure.id] = procedure

    def update(self, procedure: Memory) -> None:
        with self._lock:
            self._procedures[procedure.id] = procedure

    def get(self, procedure_id: str) -> Optional[Memory]:
        return self._procedures.get(procedure_id)

    def remove(self, procedure_id: str) -> bool:
        with self._lock:
            return self._procedures.pop(procedure_id, None) is not None

    def get_all(self) -> List[Memory]:
        return list(self._procedures.values())

    def find_by_tag(self, tag: str) -> List[Memory]:
        return [
            p
            for p in self._procedures.values()
            if tag in getattr(p, "tags", [])
        ]

    def clear(self):
        with self._lock:
            self._procedures.clear()

    def __len__(self):
        return len(self._procedures)

    def __iter__(self):
        return iter(self.get_all())