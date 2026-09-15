"""
Evaluation workflow.
"""

from __future__ import annotations

from typing import Any

from .config import CriticConfig
from .result import EvaluationResult, EvaluationItem


class EvaluationPipeline:
    """
    Sequential evaluation pipeline.

    Each evaluator must implement:

        evaluate(data) -> EvaluationItem
    """

    def __init__(
        self,
        evaluators: list[Any],
        config: CriticConfig | None = None,
    ):
        self.evaluators = evaluators
        self.config = config or CriticConfig()

    def run(self, data: Any) -> EvaluationResult:
        result = EvaluationResult()

        for evaluator in self.evaluators:
            evaluation: EvaluationItem = evaluator.evaluate(data)

            result.add(evaluation)

            if (
                self.config.fail_fast
                and not evaluation.passed
            ):
                break

        result.finalize()

        return result