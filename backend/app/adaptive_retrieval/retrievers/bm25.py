"""
BM25 Retriever

Sparse lexical retrieval using rank-bm25.

Install:
    pip install rank-bm25
"""

from __future__ import annotations

from typing import List

from rank_bm25 import BM25Okapi

from app.knowledge_system.models.chunk import Chunk


class BM25Retriever:

    def __init__(self):

        self.bm25 = None
        self.documents: List[Chunk] = []

    def build_index(
        self,
        chunks: List[Chunk],
    ):

        self.documents = chunks

        corpus = [
            chunk.text.lower().split()
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(corpus)

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[Chunk]:

        if self.bm25 is None:
            raise RuntimeError(
                "BM25 index has not been built."
            )

        tokens = query.lower().split()

        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            doc
            for doc, _
            in ranked[:top_k]
        ]

    def retrieve_with_scores(
        self,
        query: str,
        top_k: int = 10,
    ):

        tokens = query.lower().split()

        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        return ranked[:top_k]