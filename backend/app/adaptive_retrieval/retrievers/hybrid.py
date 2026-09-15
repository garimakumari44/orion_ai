"""
Hybrid Retriever

Combines:
- Dense Retrieval
- Sparse Retrieval
- Keyword Retrieval
- Graph Retrieval

Uses Reciprocal Rank Fusion (RRF).
"""

from __future__ import annotations

from collections import defaultdict
from typing import List

from .base import BaseRetriever
from .dense import DenseRetriever
from .sparse import SparseRetriever
from .keyword import KeywordRetriever
from .graph import GraphRetriever

from app.knowledge_system.models.chunk import Chunk


class HybridRetriever(BaseRetriever):

    def __init__(
        self,
        dense: DenseRetriever,
        sparse: SparseRetriever,
        keyword: KeywordRetriever,
        graph: GraphRetriever,
    ):

        self.dense = dense
        self.sparse = sparse
        self.keyword = keyword
        self.graph = graph

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[Chunk]:

        dense_results = await self.dense.retrieve(query, top_k)

        sparse_results = await self.sparse.retrieve(query, top_k)

        keyword_results = await self.keyword.retrieve(query, top_k)

        graph_results = await self.graph.retrieve(query, top_k)

        return self._rrf(
            dense_results,
            sparse_results,
            keyword_results,
            graph_results,
            top_k=top_k,
        )

    def _rrf(
        self,
        *result_sets: List[Chunk],
        top_k: int = 10,
        k: int = 60,
    ) -> List[Chunk]:
        """
        Reciprocal Rank Fusion

        score += 1/(k + rank)
        """

        scores = defaultdict(float)
        lookup = {}

        for result_set in result_sets:

            for rank, chunk in enumerate(result_set):

                scores[chunk.id] += 1.0 / (k + rank + 1)
                lookup[chunk.id] = chunk

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            lookup[cid]
            for cid, _ in ranked[:top_k]
        ]