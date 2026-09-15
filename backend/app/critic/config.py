"""
Configuration for the evaluation framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class CriticConfig:
    """
    Global configuration for evaluation.

    Attributes
    ----------
    fail_fast:
        Stop evaluation after the first critical failure.

    parallel:
        Execute evaluators concurrently when possible.

    max_workers:
        Maximum parallel workers.

    store_intermediate:
        Keep intermediate evaluator outputs.

    verbose:
        Enable verbose logging.

    evaluator_options:
        Per-evaluator configuration.
    """

    fail_fast: bool = False
    parallel: bool = False
    max_workers: int = 4
    store_intermediate: bool = True
    verbose: bool = False

    evaluator_options: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def options_for(self, evaluator: str) -> Dict[str, Any]:
        """Return configuration for an evaluator."""
        return self.evaluator_options.get(evaluator, {})