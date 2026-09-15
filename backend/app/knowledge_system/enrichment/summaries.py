"""
Document summarization models.

Supports

- Chunk summaries
- Section summaries
- Document summaries
- Executive summaries
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class SummaryType(str, Enum):
    CHUNK = "chunk"
    SECTION = "section"
    DOCUMENT = "document"
    EXECUTIVE = "executive"


class Summary(BaseModel):
    """
    Summary generated for a document.
    """

    type: SummaryType

    text: str

    model: str | None = None

    compression_ratio: float | None = None

    token_count: int | None = None

    confidence: float = Field(
        default=1.0,
        ge=0,
        le=1,
    )


class SummaryCollection(BaseModel):
    """
    Multiple summaries for one document.
    """

    chunk_summary: Summary | None = None

    section_summary: Summary | None = None

    document_summary: Summary | None = None

    executive_summary: Summary | None = None