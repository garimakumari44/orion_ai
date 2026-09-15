"""
critic/scoring/ranking.py

Ranking utilities for evaluation results.

Responsibilities
----------------
- Rank metrics
- Rank categories
- Rank complete evaluation results
- Return top-k / bottom-k results
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


# ==========================================================
# Ranked Item
# ==========================================================


@dataclass(slots=True, order=True)
class RankedItem:
    """
    Generic ranked item.
    """

    score: float
    name: str
    data: Optional[Any] = None


# ==========================================================
# Ranking Engine
# ==========================================================


class RankingEngine:
    """
    Provides ranking utilities for evaluator outputs.
    """

    # -------------------------------------------------- #

    def rank_metrics(
        self,
        metrics: Iterable[Any],
        descending: bool = True,
    ) -> List[RankedItem]:
        """
        Rank MetricScore objects.

        Expected attributes:
            - name
            - normalized()
        """

        ranked = [
            RankedItem(
                score=m.normalized() * 100,
                name=m.name,
                data=m,
            )
            for m in metrics
        ]

        return sorted(
            ranked,
            reverse=descending,
        )

    # -------------------------------------------------- #

    def rank_categories(
        self,
        category_scores: Dict[str, float],
        descending: bool = True,
    ) -> List[RankedItem]:
        """
        Rank category averages.
        """

        ranked = [
            RankedItem(
                score=score,
                name=name,
            )
            for name, score in category_scores.items()
        ]

        return sorted(
            ranked,
            reverse=descending,
        )

    # -------------------------------------------------- #

    def rank_results(
        self,
        results: Iterable[Any],
        key: str = "weighted",
        descending: bool = True,
    ) -> List[Any]:
        """
        Rank FinalScore objects.

        key examples:
            overall
            weighted
        """

        return sorted(
            results,
            key=lambda r: getattr(r, key),
            reverse=descending,
        )

    # -------------------------------------------------- #

    def best_metric(
        self,
        metrics: Iterable[Any],
    ) -> Optional[RankedItem]:
        """
        Highest scoring evaluator.
        """

        ranked = self.rank_metrics(metrics)

        return ranked[0] if ranked else None

    # -------------------------------------------------- #

    def worst_metric(
        self,
        metrics: Iterable[Any],
    ) -> Optional[RankedItem]:
        """
        Lowest scoring evaluator.
        """

        ranked = self.rank_metrics(
            metrics,
            descending=False,
        )

        return ranked[0] if ranked else None

    # -------------------------------------------------- #

    def top_k(
        self,
        items: Iterable[RankedItem],
        k: int = 5,
    ) -> List[RankedItem]:
        """
        Return top-k ranked items.
        """

        ranked = sorted(
            items,
            reverse=True,
        )

        return ranked[:k]

    # -------------------------------------------------- #

    def bottom_k(
        self,
        items: Iterable[RankedItem],
        k: int = 5,
    ) -> List[RankedItem]:
        """
        Return bottom-k ranked items.
        """

        ranked = sorted(items)

        return ranked[:k]

    # -------------------------------------------------- #

    def percentile_rank(
        self,
        score: float,
        scores: Iterable[float],
    ) -> float:
        """
        Compute percentile rank.

        Returns value in [0,100].
        """

        values = list(scores)

        if not values:
            return 0.0

        lower = sum(s <= score for s in values)

        return (lower / len(values)) * 100

    # -------------------------------------------------- #

    def leaderboard(
        self,
        metrics: Iterable[Any],
    ) -> List[Dict[str, Any]]:
        """
        Produce a leaderboard.
        """

        ranked = self.rank_metrics(metrics)

        board = []

        for position, item in enumerate(ranked, start=1):
            board.append(
                {
                    "rank": position,
                    "name": item.name,
                    "score": round(item.score, 2),
                }
            )

        return board