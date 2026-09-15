"""
Rule-based critic.

Applies deterministic business rules on evaluator outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class RuleViolation:
    rule: str
    severity: str
    message: str


class RuleCritic:

    def __init__(self):
        self.rules = [
            self._hallucination_rule,
            self._citation_rule,
            self._toxicity_rule,
            self._factual_rule,
        ]

    def critique(self, scores: Dict[str, float]) -> List[RuleViolation]:

        violations = []

        for rule in self.rules:
            result = rule(scores)
            if result:
                violations.append(result)

        return violations

    def _hallucination_rule(self, scores):

        if scores.get("hallucination", 1.0) < 0.6:
            return RuleViolation(
                rule="Hallucination",
                severity="high",
                message="Possible hallucinated content detected.",
            )

    def _citation_rule(self, scores):

        if scores.get("citation", 1.0) < 0.5:
            return RuleViolation(
                rule="Citation",
                severity="medium",
                message="Insufficient citation quality.",
            )

    def _toxicity_rule(self, scores):

        if scores.get("toxicity", 1.0) < 0.8:
            return RuleViolation(
                rule="Toxicity",
                severity="critical",
                message="Potential toxic language.",
            )

    def _factual_rule(self, scores):

        if scores.get("factual", 1.0) < 0.7:
            return RuleViolation(
                rule="Factual",
                severity="high",
                message="Low factual confidence.",
            )