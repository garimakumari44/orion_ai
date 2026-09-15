"""
critic/scoring/thresholds.py

Quality thresholds used during evaluation.

Responsibilities
----------------
- Define minimum passing scores
- Support per-category thresholds
- Support severity levels
- Allow runtime overrides
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Mapping


# ==========================================================
# Severity
# ==========================================================


class Severity(str, Enum):
    """Overall evaluation quality."""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    FAIL = "fail"


# ==========================================================
# Default Thresholds
# ==========================================================


DEFAULT_CATEGORY_THRESHOLDS: Dict[str, float] = {
    "quality": 0.75,
    "reasoning": 0.70,
    "safety": 0.95,
    "retrieval": 0.70,
    "coverage": 0.70,
    "presentation": 0.60,
    "confidence": 0.60,
    "fairness": 0.90,
}

DEFAULT_OVERALL_THRESHOLD = 70.0


# ==========================================================
# Threshold Manager
# ==========================================================


@dataclass(slots=True)
class ThresholdManager:
    """
    Stores and validates evaluation thresholds.
    """

    overall: float = DEFAULT_OVERALL_THRESHOLD

    categories: Dict[str, float] = field(
        default_factory=lambda: DEFAULT_CATEGORY_THRESHOLDS.copy()
    )

    # ----------------------------------------------------- #

    def get(self, category: str) -> float:
        """
        Return threshold for a category.

        Unknown categories default to 0.0.
        """
        return self.categories.get(category, 0.0)

    # ----------------------------------------------------- #

    def set(self, category: str, threshold: float) -> None:
        """
        Update category threshold.
        """
        self._validate(threshold)
        self.categories[category] = threshold

    # ----------------------------------------------------- #

    def update(self, values: Mapping[str, float]) -> None:
        """
        Bulk update thresholds.
        """
        for category, threshold in values.items():
            self.set(category, threshold)

    # ----------------------------------------------------- #

    def remove(self, category: str) -> None:
        """
        Remove category threshold.
        """
        self.categories.pop(category, None)

    # ----------------------------------------------------- #

    def set_overall(self, threshold: float) -> None:
        """
        Update overall passing threshold.
        """
        if not 0 <= threshold <= 100:
            raise ValueError("Overall threshold must be between 0 and 100.")

        self.overall = threshold

    # ----------------------------------------------------- #

    def passed_category(
        self,
        category: str,
        score: float,
    ) -> bool:
        """
        Check whether category passed.

        score is expected to be normalized [0,1].
        """
        return score >= self.get(category)

    # ----------------------------------------------------- #

    def passed_overall(
        self,
        score: float,
    ) -> bool:
        """
        Check overall score.

        score is expected to be 0-100.
        """
        return score >= self.overall

    # ----------------------------------------------------- #

    def severity(
        self,
        score: float,
    ) -> Severity:
        """
        Convert score into quality level.
        """

        if score >= 95:
            return Severity.EXCELLENT

        if score >= 85:
            return Severity.GOOD

        if score >= 70:
            return Severity.ACCEPTABLE

        if score >= 50:
            return Severity.POOR

        return Severity.FAIL

    # ----------------------------------------------------- #

    def validate_categories(
        self,
        scores: Mapping[str, float],
    ) -> Dict[str, bool]:
        """
        Validate every category score.
        """

        return {
            category: self.passed_category(category, value)
            for category, value in scores.items()
        }

    # ----------------------------------------------------- #

    def as_dict(self) -> Dict[str, float]:
        """
        Return thresholds dictionary.
        """
        return dict(self.categories)

    # ----------------------------------------------------- #

    def reset(self) -> None:
        """
        Restore default thresholds.
        """
        self.overall = DEFAULT_OVERALL_THRESHOLD
        self.categories = DEFAULT_CATEGORY_THRESHOLDS.copy()

    # ----------------------------------------------------- #

    @staticmethod
    def _validate(value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                "Category thresholds must be between 0.0 and 1.0."
            )