"""
Diversification algorithms.

Implements Maximum Marginal Relevance (MMR).
"""

from __future__ import annotations

from typing import List

import numpy as np

from app.knowledge_system.models.chunk  import Chunk


class MMRDiversifier:
    """
    Maximum Marginal Relevance.

    Balances:

    - relevance

    - diversity
    """

    def __init__(self, lambda_param: float = 0.7):
        self.lambda_param = lambda_param

    @staticmethod
    def cosine_similarity(
        a: np.ndarray,
        b: np.ndarray,
    ) -> float:

        return float(
            np.dot(a, b)
            / (
                np.linalg.norm(a)
                * np.linalg.norm(b)
                + 1e-10
            )
        )

    def diversify(
        self,
        query_embedding: np.ndarray,
        documents: List[Chunk],
        top_k: int = 10,
    ) -> List[Chunk]:

        if not documents:
            return []

        selected = []
        remaining = documents.copy()

        while remaining and len(selected) < top_k:

            best_doc = None
            best_score = -1e9

            for doc in remaining:

                emb = np.array(doc.embedding.vector)

                relevance = self.cosine_similarity(
                    query_embedding,
                    emb,
                )

                if not selected:
                    diversity_penalty = 0.0
                else:
                    diversity_penalty = max(
                        self.cosine_similarity(
                            emb,
                            np.array(
                                d.embedding.vector
                            ),
                        )
                        for d in selected
                    )

                score = (
                    self.lambda_param * relevance
                    - (1 - self.lambda_param)
                    * diversity_penalty
                )

                if score > best_score:
                    best_score = score
                    best_doc = doc

            selected.append(best_doc)
            remaining.remove(best_doc)

        return selected