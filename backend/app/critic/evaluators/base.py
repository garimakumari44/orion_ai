"""
Base evaluator interface.

Every evaluator scores one aspect of an AI response.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from critic.result import EvaluationResult


class BaseEvaluator(ABC):
    """
    Abstract evaluator.

    Each evaluator analyzes one quality dimension
    (factuality, completeness, safety, etc.).
    """

    #: Human-readable evaluator name.
    name: str = "base"

    @abstractmethod
    async def evaluate(
        self,
        prompt: str,
        response: str,
        context: Dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """
        Evaluate the response.

        Args:
            prompt:
                Original user prompt.

            response:
                Generated response.

            context:
                Optional supporting information.

        Returns:
            EvaluationResult
        """
        raise NotImplementedError