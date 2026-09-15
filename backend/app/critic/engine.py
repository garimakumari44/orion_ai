"""
Main evaluation orchestrator.
"""

from __future__ import annotations

from typing import Any

from .config import CriticConfig
from .pipeline import EvaluationPipeline
from .result import EvaluationResult


class CriticEngine:
    """
    High-level API for running evaluations.

    Example
    -------
    engine = CriticEngine([Faithfulness(), Toxicity()])
    result = engine.evaluate(answer)
    """

    def __init__(
        self,
        evaluators: list[Any],
        config: CriticConfig | None = None,
    ):
        self.pipeline = EvaluationPipeline(
            evaluators=evaluators,
            config=config or CriticConfig(),
        )

    def evaluate(self, data: Any) -> EvaluationResult:
        """
        Run all evaluators.
        """
        return self.pipeline.run(data)