"""
critic/scoring/weights.py

Weight management for the evaluation framework.

Responsibilities
----------------
- Store category weights
- Validate weight values
- Normalize weights
- Allow runtime overrides
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional


# ==========================================================
# Default Weights
# ==========================================================

DEFAULT_WEIGHTS: Dict[str, float] = {
    # Core answer quality
    "quality": 0.30,

    # Reasoning & logic
    "reasoning": 0.20,

    # Safety & policy
    "safety": 0.15,

    # Retrieval / citations
    "retrieval": 0.10,

    # Completeness & relevance
    "coverage": 0.10,

    # Formatting / structure
    "presentation": 0.05,

    # Confidence calibration
    "confidence": 0.05,

    # Bias / fairness
    "fairness": 0.05,
}


# ==========================================================
# Weight Manager
# ==========================================================


@dataclass(slots=True)
class WeightManager:
    """
    Manages evaluator category weights.

    The weights do not need to sum to exactly 1.0;
    normalization is handled automatically.
    """

    weights: Dict[str, float] = field(
        default_factory=lambda: DEFAULT_WEIGHTS.copy()
    )

    # ------------------------------------------------------ #

    def __post_init__(self) -> None:
        self.validate()

    # ------------------------------------------------------ #

    def get(self, category: str) -> float:
        """
        Get the weight for a category.

        Unknown categories receive weight 1.0.
        """
        return self.weights.get(category, 1.0)

    # ------------------------------------------------------ #

    def set(self, category: str, weight: float) -> None:
        """
        Set/update a category weight.
        """
        if weight < 0:
            raise ValueError("Weight cannot be negative.")

        self.weights[category] = float(weight)

    # ------------------------------------------------------ #

    def update(self, values: Mapping[str, float]) -> None:
        """
        Bulk update weights.
        """
        for category, weight in values.items():
            self.set(category, weight)

    # ------------------------------------------------------ #

    def remove(self, category: str) -> None:
        """
        Remove a category weight.
        """
        self.weights.pop(category, None)

    # ------------------------------------------------------ #

    def validate(self) -> None:
        """
        Validate all stored weights.
        """
        for category, weight in self.weights.items():
            if weight < 0:
                raise ValueError(
                    f"Weight for '{category}' must be non-negative."
                )

    # ------------------------------------------------------ #

    def normalized(self) -> Dict[str, float]:
        """
        Return normalized weights that sum to 1.0.
        """
        total = sum(self.weights.values())

        if total == 0:
            return {
                key: 0.0
                for key in self.weights
            }

        return {
            key: value / total
            for key, value in self.weights.items()
        }

    # ------------------------------------------------------ #

    def total(self) -> float:
        """
        Sum of all configured weights.
        """
        return sum(self.weights.values())

    # ------------------------------------------------------ #

    def categories(self) -> list[str]:
        """
        Return all configured categories.
        """
        return sorted(self.weights.keys())

    # ------------------------------------------------------ #

    def as_dict(self) -> Dict[str, float]:
        """
        Return a copy of the current weights.
        """
        return dict(self.weights)

    # ------------------------------------------------------ #

    def reset(self) -> None:
        """
        Restore default weights.
        """
        self.weights = DEFAULT_WEIGHTS.copy()