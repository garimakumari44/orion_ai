"""
app/execution/models/execution_state.py

Runtime state for a single ExecutionEngine execution.

The TaskGraph is the canonical source of dependency
relationships.

ExecutionState is responsible for:

- execution lifecycle
- pending tasks
- running tasks
- completed tasks
- failed tasks
- blocked tasks
- task results
- dependency satisfaction
- execution progress

ExecutionState does NOT:

- create AgentContext
- execute agents
- dispatch tasks
- modify TaskGraph
- determine execution order
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.execution.models.task_result import TaskResult


@dataclass
class ExecutionState:
    """
    Mutable runtime state for a single execution.

    Dependency relationships are copied from the canonical
    TaskGraph during initialization.
    """

    execution_id: str

    status: str = "PENDING"

    started_at: datetime | None = None
    completed_at: datetime | None = None

    pending_tasks: set[str] = field(
        default_factory=set
    )

    running_tasks: set[str] = field(
        default_factory=set
    )

    completed_tasks: set[str] = field(
        default_factory=set
    )

    failed_tasks: set[str] = field(
        default_factory=set
    )

    blocked_tasks: set[str] = field(
        default_factory=set
    )

    task_dependencies: dict[str, set[str]] = field(
        default_factory=dict
    )

    task_results: dict[str, TaskResult] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # Initialization
    # =====================================================

    def initialize(self, graph) -> None:
        """
        Initialize runtime state from the canonical
        TaskGraph.

        IMPORTANT:

        TaskGraph is the source of truth for dependencies.

        Do NOT use:

            task.dependencies

        here because those are planner-level declarations.

        GraphBuilder may have validated, removed, or normalized
        dependencies before they become graph edges.
        """

        if graph is None:
            raise ValueError(
                "Execution graph is required."
            )

        self.status = "RUNNING"

        self.started_at = datetime.now(
            timezone.utc
        )

        self.completed_at = None

        self.pending_tasks.clear()
        self.running_tasks.clear()
        self.completed_tasks.clear()
        self.failed_tasks.clear()
        self.blocked_tasks.clear()
        self.task_dependencies.clear()
        self.task_results.clear()

        # -------------------------------------------------
        # TaskGraph is canonical.
        # -------------------------------------------------

        for task in graph:

            task_id = str(
                task.id
            )

            self.pending_tasks.add(
                task_id
            )

            dependencies = graph.get_dependencies(
                task_id
            )

            self.task_dependencies[
                task_id
            ] = {
                str(dependency_id)
                for dependency_id in (
                    dependencies or set()
                )
            }

        self.metadata["total_tasks"] = (
            len(self.pending_tasks)
        )

    # =====================================================
    # Dependency State
    # =====================================================

    def dependencies_satisfied(
        self,
        task_id: str,
    ) -> bool:
        """
        Return True when every dependency of a task has
        completed successfully.
        """

        task_id = str(
            task_id
        )

        dependencies = (
            self.task_dependencies.get(
                task_id,
                set(),
            )
        )

        return dependencies.issubset(
            self.completed_tasks
        )

    def dependencies_failed(
        self,
        task_id: str,
    ) -> bool:
        """
        Return True when at least one dependency has failed
        or has been blocked.
        """

        task_id = str(
            task_id
        )

        dependencies = (
            self.task_dependencies.get(
                task_id,
                set(),
            )
        )

        failed_or_blocked = (
            self.failed_tasks
            | self.blocked_tasks
        )

        return bool(
            dependencies
            & failed_or_blocked
        )

    def get_unsatisfied_dependencies(
        self,
        task_id: str,
    ) -> set[str]:
        """
        Return dependencies that have not completed.
        """

        task_id = str(
            task_id
        )

        dependencies = (
            self.task_dependencies.get(
                task_id,
                set(),
            )
        )

        return (
            dependencies
            - self.completed_tasks
        )

    # =====================================================
    # Task Lifecycle
    # =====================================================

    def mark_running(
        self,
        task_id: str,
    ) -> None:
        """
        Mark a task as running.
        """

        task_id = str(
            task_id
        )

        self.pending_tasks.discard(
            task_id
        )

        self.running_tasks.add(
            task_id
        )

    def mark_completed(
        self,
        task_id: str,
        result: TaskResult,
    ) -> None:
        """
        Mark a task as successfully completed.
        """

        task_id = str(
            task_id
        )

        self.pending_tasks.discard(
            task_id
        )

        self.running_tasks.discard(
            task_id
        )

        self.blocked_tasks.discard(
            task_id
        )

        self.failed_tasks.discard(
            task_id
        )

        self.completed_tasks.add(
            task_id
        )

        self.task_results[
            task_id
        ] = result

        if self.all_finished():

            self.status = "COMPLETED"

            self.completed_at = datetime.now(
                timezone.utc
            )

    def mark_failed(
        self,
        task_id: str,
        result: TaskResult,
    ) -> None:
        """
        Mark a task as failed because execution itself
        failed.
        """

        task_id = str(
            task_id
        )

        self.pending_tasks.discard(
            task_id
        )

        self.running_tasks.discard(
            task_id
        )

        self.completed_tasks.discard(
            task_id
        )

        self.blocked_tasks.discard(
            task_id
        )

        self.failed_tasks.add(
            task_id
        )

        self.task_results[
            task_id
        ] = result

        self.status = "FAILED"

        if self.all_finished():

            self.completed_at = datetime.now(
                timezone.utc
            )

    def mark_blocked(
        self,
        task_id: str,
        result: TaskResult,
    ) -> None:
        """
        Mark a task as blocked because one of its
        dependencies failed or was blocked.

        A blocked task is intentionally different from
        a task whose own execution failed.
        """

        task_id = str(
            task_id
        )

        self.pending_tasks.discard(
            task_id
        )

        self.running_tasks.discard(
            task_id
        )

        self.completed_tasks.discard(
            task_id
        )

        self.failed_tasks.discard(
            task_id
        )

        self.blocked_tasks.add(
            task_id
        )

        self.task_results[
            task_id
        ] = result

        if self.all_finished():

            self.status = "FAILED"

            self.completed_at = datetime.now(
                timezone.utc
            )

    # =====================================================
    # Execution Status
    # =====================================================

    def all_successful(self) -> bool:
        """
        Return True when every task completed successfully.
        """

        return (
            len(self.failed_tasks) == 0
            and len(self.blocked_tasks) == 0
            and len(self.pending_tasks) == 0
            and len(self.running_tasks) == 0
        )

    def all_finished(self) -> bool:
        """
        Return True when there are no remaining pending
        or running tasks.
        """

        return (
            len(self.pending_tasks) == 0
            and len(self.running_tasks) == 0
        )

    # =====================================================
    # Statistics
    # =====================================================

    @property
    def total_tasks(self) -> int:
        """
        Total number of known tasks.
        """

        return (
            len(self.pending_tasks)
            + len(self.running_tasks)
            + len(self.completed_tasks)
            + len(self.failed_tasks)
            + len(self.blocked_tasks)
        )

    @property
    def executed_tasks(self) -> int:
        """
        Number of tasks that produced a TaskResult.
        """

        return len(
            self.task_results
        )

    @property
    def progress(self) -> float:
        """
        Execution progress as a value between 0 and 1.
        """

        total = self.total_tasks

        if total == 0:
            return 0.0

        finished = (
            len(self.completed_tasks)
            + len(self.failed_tasks)
            + len(self.blocked_tasks)
        )

        return finished / total