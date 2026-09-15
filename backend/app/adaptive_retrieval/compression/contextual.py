"""
Context-aware compression.

Scores chunks using:
    - metadata
    - retrieval score
    - query overlap
"""

from __future__ import annotations

import re
from typing import List
from app.knowledge_system.models.chunk   import Chunk


class ContextualCompressor:

    def __init__(
        self,
        min_score: float = 0.15,
    ):
        self.min_score = min_score

    def compress(
        self,
        query: str,
        chunks: List[Chunk],
    ) -> List[Chunk]:

        query_terms = {
            w.lower()
            for w in re.findall(r"\w+", query)
        }

        kept = []

        for chunk in chunks:

            text_terms = {
                w.lower()
                for w in re.findall(r"\w+", chunk.text)
            }

            overlap = len(query_terms & text_terms)

            retrieval_score = getattr(
                chunk,
                "score",
                0.5,
            )

            score = (
                overlap * 0.6
                + retrieval_score * 0.4
            )

            if score >= self.min_score:
                kept.append(chunk)

        return kept