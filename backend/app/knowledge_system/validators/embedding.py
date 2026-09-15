from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EmbeddingModel(BaseModel):
    """
    Stores vector embedding metadata.
    """

    id: UUID = Field(default_factory=uuid4)

    document_id: UUID
    chunk_id: UUID

    vector: List[float]

    dimension: int

    provider: str
    model_name: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    metadata: Dict[str, str] = Field(default_factory=dict)


class EmbeddingRequest(BaseModel):
    """
    Request sent to embedding providers.
    """

    text: str

    provider: str
    model_name: str


class EmbeddingResponse(BaseModel):
    """
    Response from embedding service.
    """

    vector: List[float]

    dimension: int

    provider: str

    model_name: str