"""
Formatting Evaluator

Evaluates whether a response follows the expected output format.

Supports:
- Markdown validation
- JSON validation
- Code block detection
- General formatting quality
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from .base import BaseEvaluator
from ..result import EvaluationResult


class FormattingEvaluator(BaseEvaluator):
    """
    Evaluates response formatting.
    """

    name = "formatting"

    def evaluate(
        self,
        response: str,
        context: Dict[str, Any] | None = None,
    ) -> EvaluationResult:

        context = context or {}

        expected = context.get("expected_format", "text")

        score = 1.0
        feedback: List[str] = []
        metadata = {
            "expected_format": expected,
        }

        if expected == "json":
            try:
                json.loads(response)
            except Exception:
                score -= 0.6
                feedback.append("Response is not valid JSON.")

        elif expected == "markdown":

            if "#" not in response:
                score -= 0.15
                feedback.append("Missing markdown headings.")

            if "-" not in response and "*" not in response:
                score -= 0.10
                feedback.append("Missing markdown lists.")

            if "```" in response:
                metadata["contains_code_block"] = True

        elif expected == "code":

            if "```" not in response:
                score -= 0.5
                feedback.append("Missing fenced code block.")

        else:
            # General formatting heuristics
            if len(response.strip()) == 0:
                score = 0.0
                feedback.append("Empty response.")

            if "\n" not in response:
                score -= 0.05

        score = max(0.0, score)

        return EvaluationResult(
            evaluator=self.name,
            score=score,
            passed=score >= 0.8,
            feedback=feedback or ["Formatting is valid."],
            metadata=metadata,
        )