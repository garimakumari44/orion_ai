"""
Completeness evaluator.

Measures whether the response appears to answer
the user's request in sufficient detail.

This heuristic implementation can later be replaced
with an LLM-based evaluator.
"""

from __future__ import annotations

import re
from typing import Any, Dict

from critic.evaluators.base import BaseEvaluator
from critic.result import EvaluationResult


class CompletenessEvaluator(BaseEvaluator):
    """Evaluates answer completeness."""

    name = "completeness"

    async def evaluate(
        self,
        prompt: str,
        response: str,
        context: Dict[str, Any] | None = None,
    ) -> EvaluationResult:

        score = 1.0
        feedback = []

        prompt_words = set(re.findall(r"\w+", prompt.lower()))
        response_words = set(re.findall(r"\w+", response.lower()))

        if prompt_words:
            overlap = len(prompt_words & response_words) / len(prompt_words)
        else:
            overlap = 1.0

        # Coverage score
        if overlap < 0.25:
            score -= 0.5
            feedback.append(
                "Low coverage of prompt concepts."
            )

        elif overlap < 0.50:
            score -= 0.2
            feedback.append(
                "Only partial prompt coverage."
            )

        # Length heuristic
        word_count = len(response.split())

        if word_count < 20:
            score -= 0.25
            feedback.append(
                "Response is quite short."
            )

        elif word_count > 80:
            score += 0.05

        score = max(0.0, min(score, 1.0))

        return EvaluationResult(
            evaluator=self.name,
            score=score,
            passed=score >= 0.7,
            feedback=feedback,
            metadata={
                "coverage": round(overlap, 2),
                "word_count": word_count,
            },
        )