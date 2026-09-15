"""
similarity.py

Similarity utilities for evaluation comparisons.
"""

from typing import List, Tuple

from .text import normalize_text, extract_words


def jaccard_similarity(
    text_a: str,
    text_b: str
) -> float:
    """
    Compute Jaccard similarity.

    Formula:

    intersection / union

    Useful for:
    - duplicate detection
    - answer overlap
    """

    words_a = set(extract_words(text_a))
    words_b = set(extract_words(text_b))

    if not words_a or not words_b:
        return 0.0

    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)

    return len(intersection) / len(union)



def word_overlap(
    text_a: str,
    text_b: str
) -> float:
    """
    Percentage of words from A appearing in B.
    """

    words_a = set(extract_words(text_a))
    words_b = set(extract_words(text_b))

    if not words_a:
        return 0.0

    return len(
        words_a.intersection(words_b)
    ) / len(words_a)



def exact_match(
    text_a: str,
    text_b: str
) -> bool:
    """
    Exact normalized comparison.
    """

    return (
        normalize_text(text_a)
        ==
        normalize_text(text_b)
    )



def cosine_similarity(
    vector_a: List[float],
    vector_b: List[float]
) -> float:
    """
    Cosine similarity between embeddings.

    Used when:
    - comparing LLM outputs
    - semantic similarity
    """

    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Vectors must have same dimension"
        )

    dot = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sum(
        a*a
        for a in vector_a
    ) ** 0.5

    magnitude_b = sum(
        b*b
        for b in vector_b
    ) ** 0.5


    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0


    return dot / (
        magnitude_a * magnitude_b
    )



def compare_outputs(
    output_a: str,
    output_b: str
) -> dict:
    """
    Compare two AI outputs.

    Used by:
    history/comparisons.py
    evaluator ranking
    """

    return {
        "exact_match":
            exact_match(output_a, output_b),

        "jaccard":
            jaccard_similarity(
                output_a,
                output_b
            ),

        "word_overlap":
            word_overlap(
                output_a,
                output_b
            )
    }



def find_most_similar(
    target: str,
    candidates: List[str]
) -> Tuple[str, float]:
    """
    Find closest candidate response.
    """

    best_candidate = None
    best_score = 0.0


    for candidate in candidates:

        score = jaccard_similarity(
            target,
            candidate
        )

        if score > best_score:
            best_score = score
            best_candidate = candidate


    return best_candidate, best_score