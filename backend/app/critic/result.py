"""
Evaluation result models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class EvaluationItem:
    """
    Output from one evaluator.
    """

    evaluator: str

    score: float

    passed: bool

    message: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)

    duration: float | None = None


@dataclass(slots=True)
class EvaluationResult:
    """
    Final aggregated evaluation.
    """

    items: list[EvaluationItem] = field(default_factory=list)

    overall_score: float = 0.0

    passed: bool = False

    started_at: datetime = field(default_factory=datetime.utcnow)

    completed_at: datetime | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.items)

    @property
    def passed_count(self) -> int:
        return sum(item.passed for item in self.items)

    @property
    def failed_count(self) -> int:
        return self.total - self.passed_count

    def add(self, item: EvaluationItem) -> None:
        self.items.append(item)

    def finalize(self) -> None:
        self.completed_at = datetime.utcnow()

        if self.items:
            self.overall_score = (
                sum(i.score for i in self.items) / len(self.items)
            )
            self.passed = all(i.passed for i in self.items)
        else:
            self.overall_score = 0.0
            self.passed = False

    def to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "passed": self.passed,
            "total": self.total,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "items": [
                {
                    "evaluator": i.evaluator,
                    "score": i.score,
                    "passed": i.passed,
                    "message": i.message,
                    "metadata": i.metadata,
                    "duration": i.duration,
                }
                for i in self.items
            ],
        }