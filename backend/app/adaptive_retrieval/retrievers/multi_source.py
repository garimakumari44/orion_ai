"""
Multi-Source Retriever

Combines retrieval results from multiple retrievers using
weighted reciprocal rank fusion (RRF).

Supports:
    - Dense
    - Sparse
    - BM25
    - Graph
    - Metadata
    - Temporal
    - Memory (episodic / semantic / working / preference)
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from app.knowledge_system.models.chunk import Chunk


class MultiSourceRetriever:
    """
    Merge retrieval outputs from multiple sources.

    Features
    --------
    • Weighted Reciprocal Rank Fusion
    • Duplicate removal
    • Memory-aware weighting
    • Cross-source score accumulation
    """

    MEMORY_PREFIX = "memory"

    def merge(
        self,
        results: Dict[str, List[Chunk]],
    ) -> List[Chunk]:

        scores: Dict[str, float] = defaultdict(float)
        documents: Dict[str, Chunk] = {}

        for source, chunks in results.items():

            weight = self._weight(source)

            for rank, chunk in enumerate(chunks):

                chunk_id = str(chunk.id)

                # Reciprocal Rank Fusion
                score = weight / (rank + 1)

                # Bonus if retrieved by multiple sources
                if chunk_id in scores:
                    score *= 1.15

                scores[chunk_id] += score

                if chunk_id not in documents:
                    documents[chunk_id] = chunk

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            documents[chunk_id]
            for chunk_id, _ in ranked
        ]

    def _weight(
        self,
        source: str,
    ) -> float:
        """
        Source importance.
        """

        if source.startswith("memory:episodic"):
            return 1.20

        if source.startswith("memory:working"):
            return 1.15

        if source.startswith("memory:semantic"):
            return 1.00

        if source.startswith("memory:preference"):
            return 0.95

        if source.startswith("memory"):
            return 1.00

        weights = {
            "dense": 1.00,
            "sparse": 0.90,
            "bm25": 0.90,
            "graph": 0.85,
            "metadata": 0.75,
            "temporal": 0.70,
        }

        return weights.get(source, 0.60)