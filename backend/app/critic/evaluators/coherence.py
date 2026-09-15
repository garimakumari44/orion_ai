"""
Coherence Evaluator

Evaluates the structural coherence and readability of a response.
"""

from __future__ import annotations

import re
from typing import List

from .base import BaseEvaluator
from ..result import EvaluationResult


class CoherenceEvaluator(BaseEvaluator):
    """
    Measures how well the response flows.

    Checks:
    - sentence structure
    - paragraph organization
    - abrupt transitions
    - average sentence length
    """

    name = "coherence"

    TRANSITIONS = {
        "however",
        "therefore",
        "thus",
        "moreover",
        "furthermore",
        "additionally",
        "finally",
        "first",
        "second",
        "next",
        "then",
        "because",
        "although",
        "meanwhile",
        "for example",
        "in conclusion",
    }

    def _split_sentences(self, text: str) -> List[str]:
        return [
            s.strip()
            for s in re.split(r"[.!?]+", text)
            if s.strip()
        ]

    def evaluate(
        self,
        prompt: str,
        response: str,
        **kwargs,
    ) -> EvaluationResult:

        sentences = self._split_sentences(response)

        if not sentences:
            return EvaluationResult(
                evaluator=self.name,
                score=0.0,
                passed=False,
                issues=["No readable content found."],
            )

        lengths = [len(s.split()) for s in sentences]

        avg_len = sum(lengths) / len(lengths)

        transition_count = sum(
            response.lower().count(word)
            for word in self.TRANSITIONS
        )

        score = 1.0

        issues = []

        if avg_len < 5:
            score -= 0.25
            issues.append("Sentences are unusually short.")

        if avg_len > 35:
            score -= 0.20
            issues.append("Sentences are overly long.")

        if transition_count == 0 and len(sentences) > 4:
            score -= 0.20
            issues.append("Few logical transitions detected.")

        if len(sentences) < 2:
            score -= 0.20
            issues.append("Very little structural organization.")

        score = max(0.0, min(score, 1.0))

        return EvaluationResult(
            evaluator=self.name,
            score=score,
            passed=score >= 0.7,
            issues=issues,
            metadata={
                "sentences": len(sentences),
                "average_sentence_length": round(avg_len, 2),
                "transitions": transition_count,
            },
        )