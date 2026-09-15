"""
Memory decay and forgetting.
"""

from __future__ import annotations

from datetime import datetime, timezone
from math import exp
from typing import Iterable, List

from app.memory.models.memory import Memory


class MemoryDecay:
    """
    Applies time-based decay to memories.
    """

    def __init__(
        self,
        decay_rate: float = 0.0005,
    ):
        self.decay_rate = decay_rate

    def score(
        self,
        memory: Memory,
    ) -> float:
        """
        Compute current retention score.
        """

        now = datetime.now(timezone.utc)

        age = (
            now - memory.updated_at
        ).total_seconds()

        retention = exp(
            -self.decay_rate * age
        )

        return (
            retention
            * memory.importance
            * memory.confidence
        )

    def should_forget(
        self,
        memory: Memory,
        threshold: float = 0.10,
    ) -> bool:
        """
        Decide whether memory should be removed.
        """

        return self.score(memory) < threshold

    def filter_active(
        self,
        memories: Iterable[Memory],
        threshold: float = 0.10,
    ) -> List[Memory]:
        """
        Remove memories that have decayed below threshold.
        """

        return [
            memory
            for memory in memories
            if not self.should_forget(
                memory,
                threshold,
            )
        ]

    def refresh(
        self,
        memory: Memory,
        amount: float = 0.05,
    ) -> Memory:
        """
        Reinforce a memory after access.
        """

        memory.confidence = min(
            1.0,
            memory.confidence + amount,
        )

        memory.access_count += 1
        memory.last_accessed = datetime.now(timezone.utc)

        return memory