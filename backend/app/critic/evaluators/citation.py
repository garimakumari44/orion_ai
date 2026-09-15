"""
Citation Verification Evaluator

Checks whether factual claims are properly cited.
"""

from __future__ import annotations

import re
from typing import List

from .base import BaseEvaluator
from ..result import EvaluationResult


class CitationEvaluator(BaseEvaluator):
    """
    Evaluates citation coverage.

    Looks for common citation patterns:
    - [1]
    - (Smith, 2024)
    - URLs
    - DOI references
    """

    name = "citation"

    CITATION_PATTERNS = [
        r"\[\d+\]",
        r"\([A-Za-z].*?\d{4}\)",
        r"https?://\S+",
        r"doi:\S+",
    ]

    def _count_citations(self, text: str) -> int:
        count = 0
        for pattern in self.CITATION_PATTERNS:
            count += len(re.findall(pattern, text))
        return count

    def evaluate(self, prompt: str, response: str, **kwargs) -> EvaluationResult:
        citations = self._count_citations(response)

        if citations == 0:
            score = 0.2
            issues = ["No citations detected."]
        elif citations < 3:
            score = 0.7
            issues = ["Limited citation coverage."]
        else:
            score = 1.0
            issues = []

        return EvaluationResult(
            evaluator=self.name,
            score=score,
            passed=score >= 0.7,
            issues=issues,
            metadata={
                "citations_found": citations,
            },
        )