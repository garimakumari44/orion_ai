"""
Factual accuracy evaluator.

This implementation uses simple heuristics.

Future versions can integrate:

- RAG verification
- Knowledge Graphs
- Wikipedia
- Search APIs
- LLM-based verification
"""

from __future__ import annotations

import re
from typing import Any, Dict

from critic.evaluators.base import BaseEvaluator
from critic.result import EvaluationResult


class FactualEvaluator(BaseEvaluator):
    """Checks factual consistency."""

    name = "factual"

    UNCERTAIN_WORDS = {
        "maybe",
        "probably",
        "possibly",
        "guess",
        "assume",
        "approximately",
    }

    async def evaluate(
        self,
        prompt: str,
        response: str,
        context: Dict[str, Any] | None = None,
    ) -> EvaluationResult:

        score = 1.0
        feedback = []

        text = response.lower()

        # Penalize uncertainty
        uncertain = [
            word
            for word in self.UNCERTAIN_WORDS
            if word in text
        ]

        if uncertain:
            penalty = min(0.1 * len(uncertain), 0.4)
            score -= penalty

            feedback.append(
                f"Contains uncertain language: {', '.join(uncertain)}"
            )

        # Very short answers are often incomplete or unverifiable
        if len(response.split()) < 15:
            score -= 0.2
            feedback.append("Very short factual response.")

        score = max(0.0, min(score, 1.0))

        return EvaluationResult(
            evaluator=self.name,
            score=score,
            passed=score >= 0.7,
            feedback=feedback,
            metadata={
                "word_count": len(response.split()),
            },
        )