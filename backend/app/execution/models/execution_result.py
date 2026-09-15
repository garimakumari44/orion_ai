from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .task_result import TaskResult


@dataclass(slots=True)
class ExecutionResult:
    """
    Final result produced by the Execution Engine.

    This object summarizes the entire execution lifecycle.
    """

    success: bool

    task_results: List[TaskResult] = field(default_factory=list)

    outputs: Dict[str, Any] = field(default_factory=dict)

    errors: List[str] = field(default_factory=list)

    execution_time: float = 0.0

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def completed_tasks(self) -> int:
        """Number of successfully completed tasks."""
        return sum(
            1
            for task in self.task_results
            if task.success
        )

    @property
    def failed_tasks(self) -> int:
        """Number of failed tasks."""
        return sum(
            1
            for task in self.task_results
            if not task.success
        )

    def add_result(self, result: TaskResult) -> None:
        """
        Store a completed task result.
        """
        self.task_results.append(result)

        if result.success:
            self.outputs[result.task_id] = result.output
        elif result.error:
            self.errors.append(result.error)

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """
        Retrieve the result of a specific task.
        """
        for result in self.task_results:
            if result.task_id == task_id:
                return result
        return None

    def has_errors(self) -> bool:
        """
        Returns True if execution encountered any errors.
        """
        return len(self.errors) > 0

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize execution result.
        """
        return {
            "success": self.success,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "execution_time": self.execution_time,
            "outputs": self.outputs,
            "errors": self.errors,
            "metadata": self.metadata,
            "task_results": [
                result.to_dict()
                for result in self.task_results
            ],
        }