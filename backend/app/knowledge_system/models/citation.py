"""
Citation models.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field

from .base import BaseModel


class Citation(BaseModel):
    """
    Citation pointing to the original source.
    """

    id: UUID = Field(default_factory=uuid4)

    document_id: UUID

    chunk_id: Optional[UUID] = None

    source: str

    page: Optional[int] = None

    section: Optional[str] = None

    start_char: Optional[int] = None
    end_char: Optional[int] = None

    url: Optional[str] = None

    snippet: Optional[str] = None