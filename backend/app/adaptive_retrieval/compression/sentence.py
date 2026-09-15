"""
Sentence-level compression.

Keeps only the most relevant sentences from retrieved documents.
"""

from __future__ import annotations

import re
from typing import List

from models.chunk import Chunk


class SentenceCompressor:
    """
    Extract important sentences using keyword overlap.

    Later this can be replaced by:
        - Cross Encoder
        - BGE Reranker
        - MiniLM
        - LLM
    """

    SENTENCE_REGEX = re.compile(r"(?<=[.!?])\s+")

    def __init__(
        self,
        max_sentences: int = 5,
        min_sentence_length: int = 20,
    ):
        self.max_sentences = max_sentences
        self.min_sentence_length = min_sentence_length

    def compress(
        self,
        query: str,
        chunks: List[Chunk],
    ) -> List[Chunk]:

        query_words = {
            word.lower()
            for word in re.findall(r"\w+", query)
        }

        compressed = []

        for chunk in chunks:

            sentences = self.SENTENCE_REGEX.split(chunk.text)

            scored = []

            for sentence in sentences:

                if len(sentence) < self.min_sentence_length:
                    continue

                words = {
                    w.lower()
                    for w in re.findall(r"\w+", sentence)
                }

                score = len(query_words & words)

                scored.append((score, sentence))

            scored.sort(
                key=lambda x: x[0],
                reverse=True,
            )

            best = [
                s
                for _, s in scored[: self.max_sentences]
            ]

            new_chunk = chunk.model_copy(deep=True)
            new_chunk.text = " ".join(best)

            compressed.append(new_chunk)

        return compressed