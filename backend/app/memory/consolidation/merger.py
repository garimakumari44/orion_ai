"""
memory/consolidation/merger.py

Memory consolidation and merging.

Responsibilities
----------------
- Merge duplicate memories
- Combine metadata
- Preserve highest quality content
- Update confidence and importance
- Aggregate references and tags
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from app.memory.models.memory import Memory


class MemoryMerger:
    """
    Consolidates multiple memories into one.

    Example
    -------
    merger = MemoryMerger()

    merged = merger.merge([memory1, memory2, memory3])
    """

    def merge(self, memories: Iterable[Memory]) -> Optional[Memory]:
        """
        Merge multiple memory objects into one.

        Parameters
        ----------
        memories:
            Iterable of Memory objects.

        Returns
        -------
        Memory | None
        """

        memories = list(memories)

        if not memories:
            return None

        if len(memories) == 1:
            return deepcopy(memories[0])

        base = deepcopy(memories[0])

        for memory in memories[1:]:
            base = self._merge_pair(base, memory)

        return base

    # ------------------------------------------------------------------ #

    def _merge_pair(
        self,
        first: Memory,
        second: Memory,
    ) -> Memory:
        """
        Merge two memory objects.
        """

        # Prefer longer content
        if len(second.content) > len(first.content):
            first.content = second.content

        # Higher importance wins
        first.importance = max(
            first.importance,
            second.importance,
        )

        # Average confidence
        first.confidence = (
            first.confidence + second.confidence
        ) / 2

        # Earliest creation time
        first.created_at = min(
            first.created_at,
            second.created_at,
        )

        # Latest update time
        first.updated_at = max(
            first.updated_at,
            second.updated_at,
        )

        # Latest access
        if second.last_accessed:
            if (
                first.last_accessed is None
                or second.last_accessed > first.last_accessed
            ):
                first.last_accessed = second.last_accessed

        # Merge tags
        first.tags = sorted(
            set(first.tags).union(second.tags)
        )

        # Merge metadata
        first.metadata = self._merge_dicts(
            first.metadata,
            second.metadata,
        )

        # Merge references
        first.references = list(
            dict.fromkeys(
                first.references + second.references
            )
        )

        # Increment occurrences
        first.access_count += second.access_count + 1

        # Consolidation timestamp
        first.updated_at = datetime.now(timezone.utc)

        return first

    # ------------------------------------------------------------------ #

    @staticmethod
    def _merge_dicts(
        first: Dict[str, Any],
        second: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Recursively merge dictionaries.

        Nested dictionaries are merged.
        Lists are unioned.
        Primitive values from the second dictionary
        overwrite the first.
        """

        result = deepcopy(first)

        for key, value in second.items():

            if key not in result:
                result[key] = deepcopy(value)
                continue

            current = result[key]

            if (
                isinstance(current, dict)
                and isinstance(value, dict)
            ):
                result[key] = MemoryMerger._merge_dicts(
                    current,
                    value,
                )

            elif (
                isinstance(current, list)
                and isinstance(value, list)
            ):
                result[key] = list(
                    dict.fromkeys(current + value)
                )

            else:
                result[key] = deepcopy(value)

        return result

    # ------------------------------------------------------------------ #

    def merge_groups(
        self,
        groups: List[List[Memory]],
    ) -> List[Memory]:
        """
        Merge several groups of memories.

        Parameters
        ----------
        groups:
            List of duplicate groups.

        Returns
        -------
        List[Memory]
        """

        merged = []

        for group in groups:
            memory = self.merge(group)
            if memory:
                merged.append(memory)

        return merged

    # ------------------------------------------------------------------ #

    def merge_into(
        self,
        target: Memory,
        incoming: Memory,
    ) -> Memory:
        """
        Merge incoming memory into an existing memory.
        """

        return self._merge_pair(
            deepcopy(target),
            incoming,
        )