"""
Quality assessment models.

Stores automatic and human quality evaluations for
documents, chunks, summaries, entities, and extracted knowledge.
"""

from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Dict, List, Optional

from pydantic import Field

from .base import BaseModel


class QualityMetric(BaseModel):
    """
    Individual quality metric.
    """

    name: str
    score: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(default=1.0, gt=0)
    explanation: Optional[str] = None


class QualityAssessment(BaseModel):
    """
    Overall quality assessment.
    """

    target_id: str

    metrics: List[QualityMetric] = Field(default_factory=list)

    reviewer: Optional[str] = None
    model_name: Optional[str] = None

    confidence: float = Field(default=1.0, ge=0, le=1)

    notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def overall_score(self) -> float:
        """
        Weighted average.
        """

        if not self.metrics:
            return 0.0

        total_weight = sum(m.weight for m in self.metrics)

        if total_weight == 0:
            return 0.0

        weighted = sum(
            m.score * m.weight
            for m in self.metrics
        )

        return weighted / total_weight

    @property
    def metric_count(self) -> int:
        return len(self.metrics)

    def metric(self, name: str) -> Optional[QualityMetric]:
        for m in self.metrics:
            if m.name == name:
                return m
        return None

    def add_metric(
        self,
        name: str,
        score: float,
        weight: float = 1.0,
        explanation: Optional[str] = None,
    ) -> None:

        self.metrics.append(
            QualityMetric(
                name=name,
                score=score,
                weight=weight,
                explanation=explanation,
            )
        )


class DatasetQuality(BaseModel):
    """
    Aggregate quality statistics.
    """

    dataset_name: str

    assessments: List[QualityAssessment] = Field(default_factory=list)

    @property
    def average_score(self) -> float:

        if not self.assessments:
            return 0.0

        return mean(
            a.overall_score
            for a in self.assessments
        )

    @property
    def count(self) -> int:
        return len(self.assessments)

    def distribution(self) -> Dict[str, int]:
        """
        Quality buckets.
        """

        buckets = {
            "excellent": 0,
            "good": 0,
            "average": 0,
            "poor": 0,
        }

        for assessment in self.assessments:

            score = assessment.overall_score

            if score >= 0.9:
                buckets["excellent"] += 1

            elif score >= 0.75:
                buckets["good"] += 1

            elif score >= 0.5:
                buckets["average"] += 1

            else:
                buckets["poor"] += 1

        return buckets