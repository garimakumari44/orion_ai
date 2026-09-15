"""
Duplicate memory detection.
"""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Iterable, List

from app.memory.models.memory import Memory


class MemoryDeduplicator:
    """
    Detect duplicate or highly similar memories.
    """

    def __init__(self, similarity_threshold: float = 0.90):
        self.similarity_threshold = similarity_threshold

    def similarity(self, text1: str, text2: str) -> float:
        """
        Text similarity.
        """

        return SequenceMatcher(
            None,
            text1.lower(),
            text2.lower(),
        ).ratio()

    def is_duplicate(
        self,
        first: Memory,
        second: Memory,
    ) -> bool:
        """
        Determine whether two memories are duplicates.
        """

        score = self.similarity(
            first.content,
            second.content,
        )

        return score >= self.similarity_threshold

    def group_duplicates(
        self,
        memories: Iterable[Memory],
    ) -> List[List[Memory]]:
        """
        Group duplicate memories.
        """

        memories = list(memories)

        groups = []
        visited = set()

        for i, memory in enumerate(memories):

            if i in visited:
                continue

            group = [memory]
            visited.add(i)

            for j in range(i + 1, len(memories)):

                if j in visited:
                    continue

                if self.is_duplicate(memory, memories[j]):
                    group.append(memories[j])
                    visited.add(j)

            groups.append(group)

        return groups