"""
Token budget compressor.

Limits retrieved context to a maximum number of
estimated tokens.
"""

from __future__ import annotations

from typing import List

from models.chunk import Chunk


class TokenBudgetCompressor:

    def __init__(
        self,
        max_tokens: int = 4000,
        chars_per_token: int = 4,
    ):
        self.max_tokens = max_tokens
        self.chars_per_token = chars_per_token

    def estimate_tokens(
        self,
        text: str,
    ) -> int:

        return max(
            1,
            len(text) // self.chars_per_token,
        )

    def compress(
        self,
        chunks: List[Chunk],
    ) -> List[Chunk]:

        total = 0
        selected = []

        for chunk in chunks:

            tokens = self.estimate_tokens(chunk.text)

            if total + tokens > self.max_tokens:
                break

            selected.append(chunk)
            total += tokens

        return selected