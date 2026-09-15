"""
Redundancy removal.

Removes highly similar chunks using Jaccard similarity.
"""

from __future__ import annotations

import re
from typing import List

from models.chunk import Chunk


class RedundancyRemover:

    def __init__(
        self,
        similarity_threshold: float = 0.85,
    ):
        self.threshold = similarity_threshold

    def _tokens(
        self,
        text: str,
    ) -> set[str]:

        return {
            w.lower()
            for w in re.findall(r"\w+", text)
        }

    def similarity(
        self,
        a: str,
        b: str,
    ) -> float:

        ta = self._tokens(a)
        tb = self._tokens(b)

        if not ta or not tb:
            return 0.0

        return len(ta & tb) / len(ta | tb)

    def compress(
        self,
        chunks: List[Chunk],
    ) -> List[Chunk]:

        unique = []

        for chunk in chunks:

            duplicate = False

            for kept in unique:

                if (
                    self.similarity(
                        chunk.text,
                        kept.text,
                    )
                    >= self.threshold
                ):
                    duplicate = True
                    break

            if not duplicate:
                unique.append(chunk)

        return unique