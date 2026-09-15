"""
Ranking and scoring utilities.
"""

from typing import Dict, List



def weighted_score(
    scores: Dict[str,float],
    weights: Dict[str,float]
) -> float:
    """
    Combine multiple scores.

    Example:

    {
      "semantic":0.8,
      "keyword":0.6
    }

    weights:

    {
      "semantic":0.7,
      "keyword":0.3
    }

    """

    total = 0.0


    for key,value in scores.items():

        weight = weights.get(
            key,
            0
        )

        total += value * weight


    return total



def normalize_scores(
    scores: List[float]
) -> List[float]:
    """
    Min-max normalization.

    Converts:

    [10,20,30]

    into:

    [0,0.5,1]
    """

    if not scores:
        return []


    minimum = min(scores)
    maximum = max(scores)


    if minimum == maximum:
        return [
            1.0 
            for _ in scores
        ]


    return [
        (s-minimum)
        /
        (maximum-minimum)

        for s in scores
    ]



def confidence_score(
    relevance: float,
    quality: float,
    freshness: float
) -> float:
    """
    Calculate retrieval confidence.

    Used for:
    - answer generation threshold
    - fallback decisions
    """

    return (
        relevance * 0.5
        +
        quality * 0.3
        +
        freshness * 0.2
    )



def rank_items(
    items,
    scores
):
    """
    Sort items by score.

    items:
        retrieved documents

    scores:
        relevance scores
    """

    ranked = sorted(
        zip(items,scores),
        key=lambda x:x[1],
        reverse=True
    )


    return [
        item
        for item,_ in ranked
    ]