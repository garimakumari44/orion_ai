"""
Source Credibility Evaluator
"""

from __future__ import annotations

from urllib.parse import urlparse

from .base import BaseEvaluator
from ..result import EvaluationResult


class SourceValidationEvaluator(BaseEvaluator):
    """
    Estimates credibility of cited sources.

    Uses simple domain-based heuristics.
    """

    name = "source_validation"

    TRUSTED_DOMAINS = {
        "arxiv.org",
        "nature.com",
        "science.org",
        "nih.gov",
        "openai.com",
        "anthropic.com",
        "github.com",
        "wikipedia.org",
        "gov",
        "edu",
    }

    def _extract_domains(self, text: str):
        domains = []

        for token in text.split():
            if token.startswith("http://") or token.startswith("https://"):
                try:
                    domain = urlparse(token).netloc.lower()
                    domains.append(domain)
                except Exception:
                    pass

        return domains

    def evaluate(self, prompt: str, response: str, **kwargs) -> EvaluationResult:

        domains = self._extract_domains(response)

        trusted = 0

        for d in domains:
            if any(t in d for t in self.TRUSTED_DOMAINS):
                trusted += 1

        if not domains:
            score = 0.5
            issues = ["No external sources detected."]
        else:
            score = trusted / len(domains)
            issues = []

            if score < 0.5:
                issues.append("Most sources are not recognized as trusted.")

        return EvaluationResult(
            evaluator=self.name,
            score=score,
            passed=score >= 0.6,
            issues=issues,
            metadata={
                "domains": domains,
                "trusted_sources": trusted,
            },
        )