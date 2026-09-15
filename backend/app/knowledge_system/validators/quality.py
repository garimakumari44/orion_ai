from __future__ import annotations

from datetime import datetime
from typing import Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class QualityScore(BaseModel):
    """
    Overall quality metrics for a document or chunk.
    """

    id: UUID = Field(default_factory=uuid4)

    resource_id: UUID

    completeness: float = 1.0

    readability: float = 1.0

    coherence: float = 1.0

    relevance: float = 1.0

    uniqueness: float = 1.0

    factuality: float = 1.0

    overall_score: float = 1.0

    metadata: Dict[str, str] = Field(default_factory=dict)

    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class QualityReport(BaseModel):
    """
    Human-readable quality evaluation.
    """

    resource_id: UUID

    passed: bool

    message: str

    score: float