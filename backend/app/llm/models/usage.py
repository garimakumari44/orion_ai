"""
Token usage and cost tracking models.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TokenUsage(BaseModel):
    """
    Tracks token consumption for a single request.
    """

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0

    cached_prompt_tokens: int = 0

    reasoning_tokens: int = 0

    audio_tokens: int = 0

    image_tokens: int = 0

    def compute_total(self) -> int:
        """
        Compute total tokens if provider did not return it.
        """

        self.total_tokens = (
            self.prompt_tokens +
            self.completion_tokens
        )

        return self.total_tokens


class CostUsage(BaseModel):
    """
    Monetary cost associated with a request.
    """

    prompt_cost: float = 0.0

    completion_cost: float = 0.0

    total_cost: float = 0.0

    currency: str = "USD"

    def compute_total(self) -> float:
        """
        Compute total cost.
        """

        self.total_cost = (
            self.prompt_cost +
            self.completion_cost
        )

        return self.total_cost


class UsageSummary(BaseModel):
    """
    Combined usage information.
    """

    usage: TokenUsage

    cost: Optional[CostUsage] = None

    latency_ms: Optional[float] = None

    requests: int = 1

    cache_hit: bool = False