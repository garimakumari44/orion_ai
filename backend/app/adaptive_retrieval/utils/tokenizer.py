"""
Tokenizer utilities.

Handles:
- token counting
- text truncation
- token based splitting
"""

from typing import List


class Tokenizer:
    """
    Generic tokenizer abstraction.

    Supports approximate tokenization by default.
    Can later plug in:
    - tiktoken
    - HuggingFace tokenizer
    - SentencePiece
    """

    def __init__(self, tokenizer=None):
        self.tokenizer = tokenizer


    def tokenize(self, text: str) -> List[str]:
        """
        Convert text into tokens.
        """

        if self.tokenizer:
            return self.tokenizer.encode(text)

        # fallback approximation
        return text.split()



    def count_tokens(self, text: str) -> int:
        """
        Count number of tokens.
        """

        return len(self.tokenize(text))



    def truncate(
        self,
        text: str,
        max_tokens: int
    ) -> str:
        """
        Truncate text based on token limit.
        """

        tokens = self.tokenize(text)

        if len(tokens) <= max_tokens:
            return text

        return " ".join(tokens[:max_tokens])



    def split_by_tokens(
        self,
        text: str,
        chunk_size: int,
        overlap: int = 50
    ) -> List[str]:
        """
        Split text into token chunks.

        Useful for:
        - document ingestion
        - context windows
        """

        tokens = self.tokenize(text)

        chunks = []

        start = 0

        while start < len(tokens):

            end = start + chunk_size

            chunk = tokens[start:end]

            chunks.append(
                " ".join(chunk)
            )

            start = end - overlap


        return chunks



default_tokenizer = Tokenizer()