"""
Cost optimization for LLM routing.

Responsible for estimating request costs and recommending
the most cost-effective provider/model.

This module does NOT invoke providers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================================
# Pricing
# ============================================================

@dataclass(slots=True, frozen=True)
class ModelPricing:
    """
    Cost per 1M tokens.
    """

    provider: str
    model: str

    input_cost: float
    output_cost: float

    supports_reasoning: bool = True
    supports_code: bool = True
    context_window: int = 128_000


# ============================================================
# Request
# ============================================================

@dataclass(slots=True)
class CostRequest:

    input_tokens: int
    output_tokens: int

    requires_reasoning: bool = False
    requires_code: bool = False

    minimum_context: int = 0


# ============================================================
# Estimate
# ============================================================

@dataclass(slots=True)
class CostEstimate:

    provider: str
    model: str

    estimated_cost: float


# ============================================================
# Optimizer
# ============================================================

class CostOptimizer:

    def __init__(
        self,
        pricing: List[ModelPricing],
    ) -> None:

        self.pricing = pricing

        self.total_cost = 0.0

    # --------------------------------------------------------

    def estimate(
        self,
        pricing: ModelPricing,
        request: CostRequest,
    ) -> float:
        """
        Estimate request cost.
        """

        input_cost = (
            request.input_tokens / 1_000_000
        ) * pricing.input_cost

        output_cost = (
            request.output_tokens / 1_000_000
        ) * pricing.output_cost

        return input_cost + output_cost

    # --------------------------------------------------------

    def recommend(
        self,
        request: CostRequest,
    ) -> Optional[CostEstimate]:
        """
        Return the cheapest compatible model.
        """

        candidates: List[CostEstimate] = []

        for pricing in self.pricing:

            if (
                request.requires_reasoning
                and not pricing.supports_reasoning
            ):
                continue

            if (
                request.requires_code
                and not pricing.supports_code
            ):
                continue

            if pricing.context_window < request.minimum_context:
                continue

            candidates.append(
                CostEstimate(
                    provider=pricing.provider,
                    model=pricing.model,
                    estimated_cost=self.estimate(
                        pricing,
                        request,
                    ),
                )
            )

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda x: x.estimated_cost,
        )

    # --------------------------------------------------------

    def add_usage(
        self,
        cost: float,
    ) -> None:

        self.total_cost += cost

    # --------------------------------------------------------

    def reset(self) -> None:

        self.total_cost = 0.0

    # --------------------------------------------------------

    def session_cost(self) -> float:

        return self.total_cost