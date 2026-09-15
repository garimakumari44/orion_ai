"""
Confidence Evaluator

Estimates confidence based on response quality heuristics.

This is NOT model confidence.

Instead it estimates confidence using:
- Hedging language
- Unsupported certainty
- Length
- Internal consistency
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from .base import BaseEvaluator
from ..result import EvaluationResult


class ConfidenceEvaluator(BaseEvaluator):
    """
    Estimates confidence of a generated response.
    """

    name = "confidence"

    HEDGING_PATTERNS = [
        r"\bmaybe\b",
        r"\bperhaps\b",
        r"\bpossibly\b",
        r"\bi think\b",
        r"\bi believe\b",
        r"\bnot sure\b",
        r"\bprobably\b",
        r"\blikely\b",
    ]

    OVERCONFIDENT_PATTERNS = [
        r"\bdefinitely\b",
        r"\bguaranteed\b",
        r"\bcertainly\b",
        r"\bwithout any doubt\b",
        r"\balways\b",
        r"\bnever\b",
    ]

    def evaluate(
        self,
        response: str,
        context: Dict[str, Any] | None = None,
    ) -> EvaluationResult:

        score = 1.0
        feedback: List[str] = []

        text = response.lower()

        hedges = 0
        for pattern in self.HEDGING_PATTERNS:
            hedges += len(re.findall(pattern, text))

        certainty = 0
        for pattern in self.OVERCONFIDENT_PATTERNS:
            certainty += len(re.findall(pattern, text))

        if hedges > 5:
            score -= 0.20
            feedback.append(
                "Response contains significant hedging language."
            )

        if certainty > 5:
            score -= 0.20
            feedback.append(
                "Response contains excessive certainty."
            )

        if len(response.split()) < 20:
            score -= 0.10
            feedback.append(
                "Short responses generally have lower confidence."
            )

        score = max(score, 0.0)

        metadata = {
            "hedging_terms": hedges,
            "certainty_terms": certainty,
            "word_count": len(response.split()),
        }

        return EvaluationResult(
            evaluator=self.name,
            score=score,
            passed=score >= 0.75,
            feedback=feedback or ["Confidence appears appropriate."],
            metadata=metadata,
        )