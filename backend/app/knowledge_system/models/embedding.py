"""
Embedding models.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import Field

from .base import BaseModel


class Embedding(BaseModel):
    """
    Vector embedding for a document or chunk.
    """

    id: UUID = Field(default_factory=uuid4)

    document_id: UUID
    chunk_id: Optional[UUID] = None

    model: str
    dimensions: int

    vector: List[float]

    created_at: datetime = Field(default_factory=datetime.utcnow)