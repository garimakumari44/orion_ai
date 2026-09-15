"""
Provenance and lineage models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import Field

from .base import BaseModel


class Provenance(BaseModel):
    """
    Tracks where a knowledge artifact originated.
    """

    id: UUID = Field(default_factory=uuid4)

    artifact_id: UUID

    artifact_type: str

    source_document: UUID

    source_chunk: Optional[UUID] = None

    pipeline_stage: Optional[str] = None

    processor: Optional[str] = None

    model_name: Optional[str] = None

    version: Optional[str] = None

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = Field(default_factory=dict)