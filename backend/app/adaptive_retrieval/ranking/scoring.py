"""
Final ranking score computation.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.knowledge_system.models.chunk  import Chunk


@dataclass
class RankingWeights:
    retrieval: float = 0.35
    rerank: float = 0.45
    recency: float = 0.05
    authority: float = 0.05
    quality: float = 0.10


class RankingScorer:
    """
    Computes final ranking score.
    """

    def __init__(
        self,
        weights: RankingWeights | None = None,
    ):

        self.weights = (
            weights or RankingWeights()
        )

    def score(
        self,
        chunk: Chunk,
    ) -> float:

        retrieval = getattr(
            chunk,
            "retrieval_score",
            0.0,
        )

        rerank = getattr(
            chunk,
            "rerank_score",
            retrieval,
        )

        recency = getattr(
            chunk.metadata,
            "recency_score",
            0.0,
        )

        authority = getattr(
            chunk.metadata,
            "authority_score",
            0.0,
        )

        quality = getattr(
            chunk.metadata,
            "quality_score",
            0.0,
        )

        final = (

            retrieval * self.weights.retrieval +

            rerank * self.weights.rerank +

            recency * self.weights.recency +

            authority * self.weights.authority +

            quality * self.weights.quality

        )

        chunk.score = final

        return final

    def rank(
        self,
        chunks: list[Chunk],
    ) -> list[Chunk]:

        for chunk in chunks:
            self.score(chunk)

        return sorted(
            chunks,
            key=lambda c: c.score,
            reverse=True,
        )