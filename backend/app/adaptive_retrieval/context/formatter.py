"""
Context Formatter

Responsible for:
- Formatting retrieved chunks
- Preparing context blocks
- Controlling token size
- Adding metadata
- Creating structured LLM input
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional


# ============================================================
# Context Block
# ============================================================

@dataclass(slots=True)
class ContextBlock:
    """
    Single formatted retrieval unit.
    """

    content: str

    source: Optional[str] = None
    document_id: Optional[str] = None
    chunk_id: Optional[str] = None

    score: float = 0.0

    metadata: Dict = None


# ============================================================
# Context Formatter
# ============================================================

class ContextFormatter:
    """
    Converts retrieved chunks into LLM-ready context.
    """

    def __init__(
        self,
        include_metadata: bool = True,
        separator: str = "\n\n",
    ):

        self.include_metadata = include_metadata
        self.separator = separator


    def format_chunk(
        self,
        chunk,
        index: int,
    ) -> str:
        """
        Formats a single chunk.
        """

        metadata = getattr(
            chunk,
            "metadata",
            {}
        ) or {}

        text = chunk.content


        if not self.include_metadata:
            return text


        header = (
            f"[Document {index}]"
        )


        if metadata.get("title"):
            header += (
                f"\nTitle: {metadata['title']}"
            )


        if metadata.get("source"):
            header += (
                f"\nSource: {metadata['source']}"
            )


        return (
            f"{header}\n\n"
            f"{text}"
        )


    def format(
        self,
        chunks: List,
    ) -> str:
        """
        Creates final context string.
        """

        formatted = []

        for i, chunk in enumerate(chunks, 1):

            formatted.append(
                self.format_chunk(
                    chunk,
                    i
                )
            )


        return self.separator.join(formatted)



# ============================================================
# Structured Formatter
# ============================================================

class StructuredContextFormatter(ContextFormatter):
    """
    Returns structured context instead of plain text.
    """

    def format_structured(
        self,
        chunks: List,
    ) -> List[ContextBlock]:

        blocks = []


        for chunk in chunks:

            metadata = getattr(
                chunk,
                "metadata",
                {}
            ) or {}


            blocks.append(
                ContextBlock(
                    content=chunk.content,
                    document_id=getattr(
                        chunk,
                        "document_id",
                        None
                    ),
                    chunk_id=getattr(
                        chunk,
                        "chunk_id",
                        None
                    ),
                    source=metadata.get(
                        "source"
                    ),
                    score=getattr(
                        chunk,
                        "score",
                        0.0
                    ),
                    metadata=metadata,
                )
            )


        return blocks



# ============================================================
# Token Aware Formatter
# ============================================================

class TokenAwareFormatter(ContextFormatter):
    """
    Prevents context from exceeding token budget.
    """

    def __init__(
        self,
        max_tokens: int = 4000,
        tokenizer=None,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.max_tokens = max_tokens
        self.tokenizer = tokenizer



    def count_tokens(
        self,
        text: str
    ) -> int:

        if self.tokenizer:

            return len(
                self.tokenizer.encode(text)
            )


        # Approximation
        return len(
            text.split()
        )



    def format(
        self,
        chunks: List,
    ) -> str:


        output = []

        token_count = 0


        for i, chunk in enumerate(chunks,1):

            formatted = self.format_chunk(
                chunk,
                i
            )


            size = self.count_tokens(
                formatted
            )


            if token_count + size > self.max_tokens:
                break


            output.append(formatted)

            token_count += size


        return self.separator.join(output)