"""
critic/scoring/score.py

Overall scoring engine.

Responsibilities
----------------
- Aggregate evaluator results
- Apply weighted scoring
- Compute category scores
- Produce overall evaluation score
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Dict, Iterable, List, Optional

from .weights import WeightManager


# ==========================================================
# Score Models
# ==========================================================


@dataclass(slots=True)
class MetricScore:
    """
    Score produced by a single evaluator.
    """

    name: str
    score: float
    max_score: float = 1.0
    category: str = "general"

    def normalized(self) -> float:
        if self.max_score <= 0:
            return 0.0

        return max(0.0, min(1.0, self.score / self.max_score))


@dataclass(slots=True)
class CategoryScore:
    """
    Aggregated category score.
    """

    category: str
    score: float
    weight: float


@dataclass(slots=True)
class FinalScore:
    """
    Final scoring output.
    """

    overall: float
    weighted: float

    categories: Dict[str, CategoryScore] = field(default_factory=dict)

    metrics: List[MetricScore] = field(default_factory=list)

    passed: bool = True

    summary: Dict[str, float] = field(default_factory=dict)


# ==========================================================
# Score Calculator
# ==========================================================


class ScoreCalculator:
    """
    Computes weighted evaluation scores.
    """

    def __init__(
        self,
        weight_manager: Optional[WeightManager] = None,
        pass_threshold: float = 70.0,
    ) -> None:

        self.weights = weight_manager or WeightManager()
        self.pass_threshold = pass_threshold

    # ------------------------------------------------------ #

    def calculate(
        self,
        metrics: Iterable[MetricScore],
    ) -> FinalScore:

        metrics = list(metrics)

        if not metrics:
            return FinalScore(
                overall=0.0,
                weighted=0.0,
                passed=False,
            )

        category_scores = self._compute_categories(metrics)

        weighted_score = self._compute_weighted(category_scores)

        overall = mean(
            metric.normalized() * 100
            for metric in metrics
        )

        summary = {
            "metric_count": len(metrics),
            "average": overall,
            "weighted": weighted_score,
            "min": min(m.normalized() * 100 for m in metrics),
            "max": max(m.normalized() * 100 for m in metrics),
        }

        return FinalScore(
            overall=round(overall, 2),
            weighted=round(weighted_score, 2),
            categories=category_scores,
            metrics=metrics,
            passed=weighted_score >= self.pass_threshold,
            summary=summary,
        )

    # ------------------------------------------------------ #

    def _compute_categories(
        self,
        metrics: List[MetricScore],
    ) -> Dict[str, CategoryScore]:

        grouped: Dict[str, List[MetricScore]] = {}

        for metric in metrics:
            grouped.setdefault(metric.category, []).append(metric)

        categories: Dict[str, CategoryScore] = {}

        for category, values in grouped.items():

            score = mean(v.normalized() for v in values)

            weight = self.weights.get(category)

            categories[category] = CategoryScore(
                category=category,
                score=score,
                weight=weight,
            )

        return categories

    # ------------------------------------------------------ #

    def _compute_weighted(
        self,
        categories: Dict[str, CategoryScore],
    ) -> float:

        total = 0.0
        total_weight = 0.0

        for category in categories.values():

            total += category.score * category.weight

            total_weight += category.weight

        if total_weight == 0:
            return 0.0

        return (total / total_weight) * 100