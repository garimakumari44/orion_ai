"""
Result Reranker

Ranks retrieved documents/chunks after retrieval.

Pipeline:

Retriever Results
        |
        v
    Reranker
        |
        v
 Top-k Context Candidates
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List


# ============================================================
# Models
# ============================================================

@dataclass
class RankedDocument:
    """
    Document with relevance score.
    """

    document: Any
    score: float



# ============================================================
# Reranker
# ============================================================

class ResultReranker:
    """
    Base retrieval reranker.

    Responsibilities:
    - calculate relevance score
    - reorder retrieved results
    - select top-k documents

    Future upgrades:
    - CrossEncoder reranker
    - BGE reranker
    - Cohere rerank
    - LLM reranking
    """

    def __init__(
        self,
        top_k: int = 5,
    ):
        self.top_k = top_k



    # --------------------------------------------------------
    # Scoring
    # --------------------------------------------------------

    def score(
        self,
        query: str,
        document: Any,
    ) -> float:
        """
        Calculate relevance score.

        Current:
            token overlap similarity

        Later:
            neural relevance model
        """

        text = self._extract_text(document)


        if not text:
            return 0.0


        query_tokens = set(
            query.lower().split()
        )

        document_tokens = set(
            text.lower().split()
        )


        if not query_tokens:
            return 0.0


        overlap = (
            len(
                query_tokens.intersection(
                    document_tokens
                )
            )
            /
            len(query_tokens)
        )


        return float(overlap)



    # --------------------------------------------------------
    # Text Extraction
    # --------------------------------------------------------

    def _extract_text(
        self,
        document: Any,
    ) -> str:
        """
        Supports:
        - dict documents
        - Chunk objects
        """

        # dictionary style
        if isinstance(document, dict):

            return document.get(
                "text",
                document.get(
                    "content",
                    ""
                )
            )


        # object style
        if hasattr(
            document,
            "content"
        ):
            return document.content


        if hasattr(
            document,
            "text"
        ):
            return document.text


        return ""



    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

    def rerank(
        self,
        query: str,
        documents: List[Any],
    ) -> List[RankedDocument]:
        """
        Rank retrieved documents.

        Returns:
            [
                RankedDocument(
                    document=chunk,
                    score=0.91
                )
            ]
        """

        ranked_documents = []


        for document in documents:

            relevance = self.score(
                query,
                document
            )


            ranked_documents.append(
                RankedDocument(
                    document=document,
                    score=relevance,
                )
            )



        ranked_documents.sort(
            key=lambda item: item.score,
            reverse=True,
        )


        return ranked_documents[
            : self.top_k
        ]