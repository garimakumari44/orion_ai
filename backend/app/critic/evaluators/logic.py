"""
Logical consistency evaluator.

Checks whether the response appears internally consistent
and avoids obvious logical contradictions.
"""

from __future__ import annotations

from typing import Any, Dict

from critic.evaluators.base import BaseEvaluator
from critic.result import EvaluationResult


class LogicEvaluator(BaseEvaluator):
    """Evaluates logical consistency."""

    name = "logic"

    CONTRADICTION_PAIRS = [
        ("always", "never"),
        ("all", "none"),
        ("yes", "no"),
        ("true", "false"),
        ("possible", "impossible"),
        ("required", "optional"),
        ("must", "must not"),
        ("can", "cannot"),
    ]

    async def evaluate(
        self,
        prompt: str,
        response: str,
        context: Dict[str, Any] | None = None,
    ) -> EvaluationResult:

        text = response.lower()

        score = 1.0
        feedback = []
        contradictions = []

        for left, right in self.CONTRADICTION_PAIRS:
            if left in text and right in text:
                contradictions.append(f"{left} ↔ {right}")

        if contradictions:
            penalty = min(0.15 * len(contradictions), 0.5)
            score -= penalty

            feedback.append(
                "Potential contradictions detected: "
                + ", ".join(contradictions)
            )

        if len(response.split()) < 15:
            score -= 0.1
            feedback.append("Limited explanation reduces confidence.")

        score = max(0.0, min(score, 1.0))

        return EvaluationResult(
            evaluator=self.name,
            score=score,
            passed=score >= 0.7,
            feedback=feedback,
            metadata={
                "contradictions": contradictions,
            },
        )