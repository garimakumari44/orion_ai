"""
Scoring utilities used throughout the memory subsystem.
"""

from __future__ import annotations

from datetime import datetime, timezone


def normalize_score(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    """
    Clamp a score to a specified range.
    """
    return max(minimum, min(value, maximum))


def weighted_score(
    scores: list[float],
    weights: list[float],
) -> float:
    """
    Compute a weighted average score.

    Returns
    -------
    float
        Value in the range [0, 1].
    """
    if not scores:
        return 0.0

    if len(scores) != len(weights):
        raise ValueError("Scores and weights must have equal length.")

    total_weight = sum(weights)

    if total_weight == 0:
        return 0.0

    value = sum(score * weight for score, weight in zip(scores, weights))

    return normalize_score(value / total_weight)


def recency_score(
    created_at: datetime,
    decay_days: int = 90,
) -> float:
    """
    Calculate a recency score using linear decay.

    Returns
    -------
    float
        Score between 0 and 1.
    """
    now = datetime.now(timezone.utc)

    age_days = (now - created_at).days

    score = max(0.0, 1.0 - age_days / decay_days)

    return normalize_score(score)


def importance_score(
    importance: float,
    confidence: float,
    recency: float,
) -> float:
    """
    Combine importance, confidence, and recency into a single score.
    """
    return weighted_score(
        scores=[
            importance,
            confidence,
            recency,
        ],
        weights=[
            0.5,
            0.3,
            0.2,
        ],
    )


def retrieval_score(
    similarity: float,
    importance: float,
    recency: float,
) -> float:
    """
    Final retrieval ranking score.
    """
    return weighted_score(
        scores=[
            similarity,
            importance,
            recency,
        ],
        weights=[
            0.6,
            0.25,
            0.15,
        ],
    )