"""
Reasoning quality evaluator.

Measures whether the response demonstrates
structured reasoning and explanation.
"""

from __future__ import annotations

from typing import Any, Dict

from critic.evaluators.base import BaseEvaluator
from critic.result import EvaluationResult


class ReasoningEvaluator(BaseEvaluator):
    """Evaluates reasoning quality."""

    name = "reasoning"

    REASONING_WORDS = {
        "because",
        "therefore",
        "thus",
        "hence",
        "consequently",
        "since",
        "if",
        "then",
        "therefore",
        "first",
        "second",
        "finally",
        "for example",
        "as a result",
    }

    async def evaluate(
        self,
        prompt: str,
        response: str,
        context: Dict[str, Any] | None = None,
    ) -> EvaluationResult:

        text = response.lower()

        score = 0.4
        feedback = []

        matches = [
            word
            for word in self.REASONING_WORDS
            if word in text
        ]

        score += min(len(matches) * 0.08, 0.5)

        if len(response.split()) > 60:
            score += 0.1

        if not matches:
            feedback.append(
                "Little evidence of explicit reasoning."
            )

        score = max(0.0, min(score, 1.0))

        return EvaluationResult(
            evaluator=self.name,
            score=score,
            passed=score >= 0.7,
            feedback=feedback,
            metadata={
                "reasoning_markers": matches,
                "count": len(matches),
            },
        )