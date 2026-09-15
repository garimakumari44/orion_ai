"""
Relevance Evaluator

Measures how well the response addresses the user's request.
"""

from __future__ import annotations

import re

from .base import BaseEvaluator
from ..result import EvaluationResult


class RelevanceEvaluator(BaseEvaluator):
    """
    Simple lexical relevance evaluator.

    Computes overlap between prompt keywords
    and response content.
    """

    name = "relevance"

    STOPWORDS = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "to",
        "of",
        "for",
        "with",
        "this",
        "that",
        "it",
        "be",
        "on",
        "in",
        "at",
        "by",
        "and",
        "or",
    }

    def _keywords(self, text: str):

        words = re.findall(r"[A-Za-z]{3,}", text.lower())

        return {
            w
            for w in words
            if w not in self.STOPWORDS
        }

    def evaluate(self, prompt: str, response: str, **kwargs):

        prompt_words = self._keywords(prompt)
        response_words = self._keywords(response)

        if not prompt_words:
            overlap = 1.0
        else:
            overlap = len(prompt_words & response_words) / len(prompt_words)

        issues = []

        if overlap < 0.4:
            issues.append("Response appears only weakly related to the prompt.")

        return EvaluationResult(
            evaluator=self.name,
            score=overlap,
            passed=overlap >= 0.5,
            issues=issues,
            metadata={
                "prompt_keywords": len(prompt_words),
                "response_keywords": len(response_words),
                "overlap": overlap,
            },
        )