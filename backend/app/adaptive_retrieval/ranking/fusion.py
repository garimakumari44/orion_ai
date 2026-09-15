"""
Rank Fusion Algorithms.
"""

from __future__ import annotations

from collections import defaultdict
from typing import List

from app.knowledge_system.models.chunk  import Chunk


class ReciprocalRankFusion:
    """
    RRF

    score = Σ 1/(k + rank)
    """

    def __init__(self, k: int = 60):
        self.k = k

    def fuse(
        self,
        ranked_lists: List[List[Chunk]],
    ) -> List[Chunk]:

        scores = defaultdict(float)
        documents = {}

        for ranking in ranked_lists:

            for rank, doc in enumerate(ranking):

                doc_id = str(doc.id)

                scores[doc_id] += 1.0 / (self.k + rank + 1)
                documents[doc_id] = doc

        fused = sorted(
            documents.values(),
            key=lambda d: scores[str(d.id)],
            reverse=True,
        )

        for doc in fused:
            doc.score = scores[str(doc.id)]

        return fused


class WeightedFusion:
    """
    Weighted score fusion.

    Example:

    Dense = 0.7

    Sparse = 0.3
    """

    def fuse(
        self,
        rankings: List[List[Chunk]],
        weights: List[float],
    ) -> List[Chunk]:

        if len(rankings) != len(weights):
            raise ValueError("Weights and rankings mismatch.")

        scores = defaultdict(float)
        docs = {}

        for weight, ranking in zip(weights, rankings):

            for doc in ranking:

                doc_id = str(doc.id)

                scores[doc_id] += (
                    weight * getattr(doc, "score", 0.0)
                )

                docs[doc_id] = doc

        fused = sorted(
            docs.values(),
            key=lambda d: scores[str(d.id)],
            reverse=True,
        )

        for doc in fused:
            doc.score = scores[str(doc.id)]

        return fused