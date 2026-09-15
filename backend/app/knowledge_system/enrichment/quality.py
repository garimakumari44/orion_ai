"""
Quality assessment models.

Represents quality metrics computed during document
processing and enrichment.
"""

from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class QualityMetrics(BaseModel):
    """
    Overall quality metrics for processed content.
    """

    completeness: float = Field(default=1.0, ge=0.0, le=1.0)

    readability: float = Field(default=1.0, ge=0.0, le=1.0)

    coherence: float = Field(default=1.0, ge=0.0, le=1.0)

    extraction_quality: float = Field(default=1.0, ge=0.0, le=1.0)

    embedding_quality: float = Field(default=1.0, ge=0.0, le=1.0)

    overall_score: float = Field(default=1.0, ge=0.0, le=1.0)

    metadata: Dict[str, str] = Field(default_factory=dict)

    @property
    def is_high_quality(self) -> bool:
        return self.overall_score >= 0.8