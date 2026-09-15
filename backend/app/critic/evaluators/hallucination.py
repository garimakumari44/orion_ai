"""
Hallucination evaluator.

Detects potential hallucinations using lightweight
heuristics. Future implementations can use:

- RAG verification
- Search APIs
- Knowledge graphs
- LLM-as-a-Judge
- Citation verification
"""

from __future__ import annotations

import re
from typing import Any, Dict

from critic.evaluators.base import BaseEvaluator
from critic.result import EvaluationResult


class HallucinationEvaluator(BaseEvaluator):
    """Evaluates possible hallucinations."""

    name = "hallucination"

    UNCERTAIN_PHRASES = [
        "i think",
        "probably",
        "possibly",
        "maybe",
        "i guess",
        "it seems",
        "likely",
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

        uncertain = [
            phrase
            for phrase in self.UNCERTAIN_PHRASES
            if phrase in text
        ]

        if uncertain:
            score -= min(0.1 * len(uncertain), 0.4)
            feedback.append(
                "Contains uncertain claims."
            )

        # Detect many numeric claims
        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", response)

        if len(numbers) > 10:
            score -= 0.1
            feedback.append(
                "Many numeric claims; external verification recommended."
            )

        # Optional retrieval evidence
        evidence = None
        if context:
            evidence = context.get("verified")

        if evidence is False:
            score -= 0.3
            feedback.append(
                "Supporting evidence was not verified."
            )

        if evidence is True:
            score += 0.05

        score = max(0.0, min(score, 1.0))

        return EvaluationResult(
            evaluator=self.name,
            score=score,
            passed=score >= 0.7,
            feedback=feedback,
            metadata={
                "uncertain_phrases": uncertain,
                "numeric_claims": len(numbers),
                "verified": evidence,
            },
        )