"""
Cost Estimator

Estimates the cost of executing an execution plan before execution.

This module estimates:

- LLM token cost
- Tool usage cost
- Estimated latency
- Total execution cost

The orchestrator can use these estimates to decide whether
a plan is acceptable or if a cheaper alternative should be used.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

MODEL_PRICING = {
    "gpt-4.1": {
        "input": 0.01 / 1000,
        "output": 0.03 / 1000,
    },
    "gpt-4o": {
        "input": 0.005 / 1000,
        "output": 0.015 / 1000,
    },
    "claude-sonnet": {
        "input": 0.003 / 1000,
        "output": 0.015 / 1000,
    },
}


TOOL_COSTS = {
    "web_search": 0.001,
    "github": 0.0,
    "browser": 0.002,
    "python": 0.0,
    "news": 0.001,
}


DEFAULT_LATENCY = {
    "web_search": 2.0,
    "github": 1.5,
    "browser": 5.0,
    "python": 3.0,
    "news": 2.0,
}


# -------------------------------------------------------------------
# Data Models
# -------------------------------------------------------------------

@dataclass
class TaskEstimate:
    """
    Estimated resource usage for a task.
    """

    model: str

    input_tokens: int

    output_tokens: int

    tools: List[str] = field(default_factory=list)


@dataclass
class CostEstimate:
    """
    Final estimated execution cost.
    """

    model_cost: float

    tool_cost: float

    total_cost: float

    estimated_latency: float

    total_input_tokens: int

    total_output_tokens: int