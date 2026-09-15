"""
Similarity functions.

Supports:
- cosine similarity
- euclidean similarity
- dot product
"""

from typing import List
import math



def dot_product(
    a: List[float],
    b: List[float]
) -> float:
    """
    Calculate dot product.
    """

    return sum(
        x*y 
        for x,y in zip(a,b)
    )



def magnitude(
    vector: List[float]
) -> float:
    """
    Calculate vector magnitude.
    """

    return math.sqrt(
        sum(
            x*x 
            for x in vector
        )
    )



def cosine_similarity(
    a: List[float],
    b: List[float]
) -> float:
    """
    Cosine similarity.

    Range:
    -1 -> opposite
     0 -> unrelated
     1 -> identical
    """

    denominator = (
        magnitude(a)
        *
        magnitude(b)
    )


    if denominator == 0:
        return 0.0


    return (
        dot_product(a,b)
        /
        denominator
    )



def euclidean_distance(
    a: List[float],
    b: List[float]
) -> float:
    """
    Euclidean distance.
    """

    return math.sqrt(
        sum(
            (x-y)**2
            for x,y in zip(a,b)
        )
    )



def similarity_score(
    a: List[float],
    b: List[float]
) -> float:
    """
    Normalized similarity score.
    """

    distance = euclidean_distance(
        a,
        b
    )

    return 1 / (1 + distance)