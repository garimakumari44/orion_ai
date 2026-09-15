"""
planning/models/execution_result.py

Execution result model for the Planning Engine.

Represents the outcome of executing an ExecutionPlan.
This model should contain only execution-related information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ExecutionResult:
    """
    Represents the result of executing an ExecutionPlan.

    Attributes:
        plan_id:
            Identifier of the execution plan.

        status:
            Overall execution status.
            Example values:
                - "completed"
                - "partial"
                - "failed"

        completed_tasks:
            IDs of successfully completed tasks.

        failed_tasks:
            IDs of tasks that failed.

        outputs:
            Mapping of task IDs to their execution outputs.

        execution_time:
            Total execution time in seconds.

        metadata:
            Additional execution information such as:
                - timestamps
                - retry counts
                - execution statistics
                - worker information
    """

    plan_id: str

    status: str

    completed_tasks: List[str] = field(default_factory=list)

    failed_tasks: List[str] = field(default_factory=list)

    outputs: Dict[str, Any] = field(default_factory=dict)

    execution_time: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)