from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional


class ImportancePolicy(ABC):
    """
    Base class for memory importance scoring.

    Importance is normalized to:

        0.0 -> useless
        1.0 -> critical
    """

    @abstractmethod
    def score(
        self,
        *,
        memory_type: str,
        metadata: Optional[Dict] = None,
    ) -> float:
        raise NotImplementedError


class WeightedImportancePolicy(ImportancePolicy):
    """
    Simple weighted importance policy.

    Importance is based on:

    - memory type
    - user feedback
    - manual priority
    - access count

    Final score is clamped to [0,1].
    """

    DEFAULT_TYPE_WEIGHTS = {
        "research": 0.95,
        "preference": 0.90,
        "fact": 0.85,
        "project": 0.80,
        "conversation": 0.60,
        "working": 0.40,
        "temporary": 0.20,
    }

    def __init__(
        self,
        type_weights: Optional[Dict[str, float]] = None,
    ):
        self.type_weights = (
            type_weights or self.DEFAULT_TYPE_WEIGHTS
        )

    def score(
        self,
        *,
        memory_type: str,
        metadata: Optional[Dict] = None,
    ) -> float:
        metadata = metadata or {}

        base = self.type_weights.get(memory_type, 0.5)

        manual_priority = metadata.get("priority", 0.0)
        access_count = metadata.get("access_count", 0)
        positive_feedback = metadata.get("positive_feedback", 0)

        score = base

        score += min(manual_priority * 0.20, 0.20)

        score += min(access_count / 100.0, 0.15)

        score += min(positive_feedback * 0.05, 0.10)

        return max(0.0, min(score, 1.0))