"""
Ranking algorithms for retrieved documents.

Responsible for:
- relevance scoring
- similarity calculation
- ranking signals

Future:
- BM25
- Embedding similarity
- Cross Encoder
- BGE reranker
- LLM scoring
"""

from __future__ import annotations

from typing import Any


class TokenOverlapRanker:
    """
    Simple lexical relevance ranker.

    Uses token overlap similarity.

    Score:
        matched query tokens / total query tokens
    """


    def score(
        self,
        query: str,
        document: Any,
    ) -> float:
        """
        Calculate relevance score.
        """

        text = self._extract_text(
            document
        )


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



    def _extract_text(
        self,
        document: Any,
    ) -> str:
        """
        Extract text from different formats.
        """


        if isinstance(
            document,
            dict
        ):

            return document.get(
                "text",
                document.get(
                    "content",
                    ""
                )
            )


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