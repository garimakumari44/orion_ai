"""
critic.scoring

Scoring subsystem for the evaluation framework.

This package provides utilities for:

- Aggregating evaluator outputs
- Computing weighted scores
- Managing category weights
- Applying quality thresholds
- Ranking evaluation results
"""

from .aggregation import (
    AggregationEngine,
    AggregationSummary,
    EvaluationResult,
)

from .ranking import (
    RankedItem,
    RankingEngine,
)

from .score import (
    CategoryScore,
    FinalScore,
    MetricScore,
    ScoreCalculator,
)

from .thresholds import (
    Severity,
    ThresholdManager,
)

from .weights import (
    DEFAULT_WEIGHTS,
    WeightManager,
)

__version__ = "1.0.0"

__all__ = [
    # Score models
    "MetricScore",
    "CategoryScore",
    "FinalScore",
    "ScoreCalculator",

    # Aggregation
    "EvaluationResult",
    "AggregationSummary",
    "AggregationEngine",

    # Thresholds
    "Severity",
    "ThresholdManager",

    # Weights
    "DEFAULT_WEIGHTS",
    "WeightManager",

    # Ranking
    "RankedItem",
    "RankingEngine",
]