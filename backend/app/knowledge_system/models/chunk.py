"""
Chunk models used for indexing and retrieval.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field

from .base import BaseModel


class Chunk(BaseModel):
    """
    Individual text chunk.
    """

    id: UUID = Field(default_factory=uuid4)

    document_id: UUID

    text: str

    chunk_index: int

    start_char: Optional[int] = None
    end_char: Optional[int] = None

    token_count: Optional[int] = None

    checksum: Optional[str] = None

    parent_chunk: Optional[UUID] = None