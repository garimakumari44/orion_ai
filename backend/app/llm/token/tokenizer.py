"""
Universal tokenizer utilities.

This module provides provider-independent token counting.

Features
--------
- Exact counting (tiktoken if available)
- Approximate fallback
- Batch counting
- Message counting (OpenAI chat format)
"""

from __future__ import annotations

from typing import List, Dict, Any

try:
    import tiktoken

    _HAS_TIKTOKEN = True
except ImportError:
    _HAS_TIKTOKEN = False


class Tokenizer:
    """
    Universal tokenizer.
    """

    DEFAULT_ENCODING = "cl100k_base"

    def __init__(self, encoding: str | None = None):
        self.encoding_name = encoding or self.DEFAULT_ENCODING

        if _HAS_TIKTOKEN:
            self.encoding = tiktoken.get_encoding(self.encoding_name)
        else:
            self.encoding = None

    # ---------------------------------------------------------
    # Core
    # ---------------------------------------------------------

    def count(self, text: str) -> int:
        """
        Count tokens in text.
        """

        if not text:
            return 0

        if self.encoding:
            return len(self.encoding.encode(text))

        # Approximation
        return max(1, len(text) // 4)

    def count_many(self, texts: List[str]) -> List[int]:
        """
        Count tokens for multiple texts.
        """
        return [self.count(t) for t in texts]

    def total(self, texts: List[str]) -> int:
        """
        Total tokens.
        """
        return sum(self.count_many(texts))

    # ---------------------------------------------------------
    # Chat messages
    # ---------------------------------------------------------

    def count_messages(
        self,
        messages: List[Dict[str, Any]],
    ) -> int:
        """
        Estimate chat token usage.

        Supports:
        [
            {"role":"user","content":"..."},
            {"role":"assistant","content":"..."}
        ]
        """

        total = 0

        for msg in messages:

            total += 4  # metadata estimate

            total += self.count(msg.get("role", ""))

            content = msg.get("content", "")

            if isinstance(content, list):
                for part in content:
                    total += self.count(str(part))
            else:
                total += self.count(str(content))

        total += 2

        return total

    # ---------------------------------------------------------

    def remaining(
        self,
        used: int,
        context_window: int,
    ) -> int:
        """
        Remaining available tokens.
        """
        return max(0, context_window - used)

    def fits(
        self,
        used: int,
        context_window: int,
    ) -> bool:
        """
        Whether prompt fits model.
        """
        return used <= context_window


default_tokenizer = Tokenizer()