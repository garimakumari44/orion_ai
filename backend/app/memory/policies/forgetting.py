from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional


@dataclass
class ForgetDecision:
    """
    Result of evaluating whether a memory should be forgotten.
    """

    should_forget: bool
    reason: str
    score: float


class ForgettingPolicy(ABC):
    """
    Base class for forgetting policies.
    """

    @abstractmethod
    def evaluate(
        self,
        *,
        metadata: Dict,
        now: Optional[datetime] = None,
    ) -> ForgetDecision:
        raise NotImplementedError


class AdaptiveForgettingPolicy(ForgettingPolicy):
    """
    Adaptive forgetting strategy.

    A memory is forgotten if:

    - It has expired
    - Importance is too low
    - It has not been accessed recently
    - It has very low usage

    Score:

        0.0 -> keep forever
        1.0 -> delete immediately
    """

    def __init__(
        self,
        importance_threshold: float = 0.20,
        stale_days: int = 90,
        min_accesses: int = 1,
    ):
        self.importance_threshold = importance_threshold
        self.stale_days = stale_days
        self.min_accesses = min_accesses

    def evaluate(
        self,
        *,
        metadata: Dict,
        now: Optional[datetime] = None,
    ) -> ForgetDecision:

        now = now or datetime.utcnow()

        importance = metadata.get("importance", 0.0)
        access_count = metadata.get("access_count", 0)

        expiration = metadata.get("expires_at")
        if expiration is not None and now >= expiration:
            return ForgetDecision(
                should_forget=True,
                reason="expired",
                score=1.0,
            )

        last_access = metadata.get("last_accessed")

        stale = False
        if last_access:
            age = (now - last_access).days
            stale = age >= self.stale_days

        score = 0.0

        if importance < self.importance_threshold:
            score += 0.5

        if stale:
            score += 0.3

        if access_count <= self.min_accesses:
            score += 0.2

        score = min(score, 1.0)

        return ForgetDecision(
            should_forget=score >= 0.7,
            reason="low_value" if score >= 0.7 else "retain",
            score=score,
        )

    def filter_memories(
        self,
        memories: Iterable[Dict],
    ) -> List[Dict]:
        """
        Return only memories that should be retained.
        """

        retained = []

        for memory in memories:
            decision = self.evaluate(
                metadata=memory.get("metadata", {})
            )

            if not decision.should_forget:
                retained.append(memory)

        return retained