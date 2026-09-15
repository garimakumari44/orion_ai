"""
Execution Critic.

Analyzes execution results and identifies failures,
performance bottlenecks, retries, and resource usage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TaskExecution:
    task_id: str
    success: bool
    duration: float
    retries: int = 0
    error: str | None = None


@dataclass
class ExecutionReport:
    success_rate: float
    average_duration: float
    failed_tasks: List[str]
    warnings: List[str]
    recommendations: List[str]


class ExecutionCritic:
    """
    Reviews workflow execution quality.
    """

    def critique(
        self,
        executions: List[TaskExecution],
    ) -> ExecutionReport:

        if not executions:
            return ExecutionReport(
                success_rate=0.0,
                average_duration=0.0,
                failed_tasks=[],
                warnings=["No execution data available."],
                recommendations=["Execute the workflow first."],
            )

        failed = [
            task.task_id
            for task in executions
            if not task.success
        ]

        success_rate = (
            (len(executions) - len(failed))
            / len(executions)
        )

        avg_duration = (
            sum(task.duration for task in executions)
            / len(executions)
        )

        warnings = []
        recommendations = []

        # Slow execution detection
        if avg_duration > 10:
            warnings.append(
                "Average execution time exceeds 10 seconds."
            )

        # Retry detection
        if any(task.retries > 2 for task in executions):
            warnings.append(
                "Some tasks required excessive retries."
            )

        # Failure detection
        if failed:
            recommendations.append(
                "Investigate failed tasks before rerunning."
            )

        if success_rate == 1.0:
            recommendations.append(
                "Workflow executed successfully."
            )

        return ExecutionReport(
            success_rate=success_rate,
            average_duration=avg_duration,
            failed_tasks=failed,
            warnings=warnings,
            recommendations=recommendations,
        )