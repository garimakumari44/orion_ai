"""
memory/retrieval/ranking.py

Ranking engine for retrieved memories.

Responsibilities
----------------
- Compute final ranking scores
- Combine multiple scoring signals
- Support configurable weighting
- Sort retrieval results
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Optional


# ---------------------------------------------------------------------
# Ranking Weights
# ---------------------------------------------------------------------


@dataclass
class RankingWeights:
    """
    Weights used during memory ranking.
    """

    similarity: float = 0.40
    importance: float = 0.20
    recency: float = 0.15
    confidence: float = 0.10
    frequency: float = 0.10
    boost: float = 0.05
    


# ---------------------------------------------------------------------
# Memory Ranker
# ---------------------------------------------------------------------


class MemoryRanker:
    """
    Multi-factor memory ranking engine.

    Final score is a weighted combination of:

        - embedding similarity
        - memory importance
        - recency
        - confidence
        - access frequency
        - custom boost
    """

    def __init__(
        self,
        weights: Optional[RankingWeights] = None,
    ) -> None:
        self.weights = weights or RankingWeights()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rank(
        self,
        memories: Iterable,
    ) -> List:
        """
        Rank retrieved memories.

        Each memory is expected to expose:

            similarity
            importance
            confidence
            access_count
            boost
            updated_at
        """

        ranked = []

        for memory in memories:
            score = self.score(memory)

            memory.ranking_score = score

            ranked.append(memory)

        ranked.sort(
            key=lambda m: getattr(m, "ranking_score", 0.0),
            reverse=True,
        )

        return ranked

    def score(self, memory) -> float:
        """
        Compute the final ranking score for a memory.
        """

        similarity = self._clip(
            getattr(memory, "similarity", 0.0)
        )

        importance = self._clip(
            getattr(memory, "importance", 0.0)
        )

        confidence = self._clip(
            getattr(memory, "confidence", 0.0)
        )

        frequency = self._frequency_score(
            getattr(memory, "access_count", 0)
        )

        recency = self._recency_score(
            getattr(memory, "updated_at", None)
        )

        boost = self._clip(
            getattr(memory, "boost", 0.0)
        )

        return (
            similarity * self.weights.similarity
            + importance * self.weights.importance
            + recency * self.weights.recency
            + confidence * self.weights.confidence
            + frequency * self.weights.frequency
            + boost * self.weights.boost
        )

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _frequency_score(
        self,
        access_count: int,
    ) -> float:
        """
        Convert access count into a normalized score.

        Saturates after roughly 20 accesses.
        """

        if access_count <= 0:
            return 0.0

        return min(access_count / 20.0, 1.0)

    def _recency_score(
        self,
        timestamp: Optional[datetime],
    ) -> float:
        """
        Compute normalized recency score.

        More recent memories receive higher scores.
        """

        if timestamp is None:
            return 0.0

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(timezone.utc)

        age_days = (
            now - timestamp
        ).total_seconds() / 86400

        if age_days <= 0:
            return 1.0

        return max(
            0.0,
            1.0 / (1.0 + age_days / 30.0),
        )

    @staticmethod
    def _clip(value: float) -> float:
        """
        Clamp a numeric value into the range [0, 1].
        """

        return max(
            0.0,
            min(float(value), 1.0),
        )