from __future__ import annotations

from typing import Dict, Set

from app.execution.models.task_result import TaskResult


class StateManager:
    """
    Tracks the execution state of tasks.

    Responsibilities:
    - Track pending tasks
    - Track running tasks
    - Track completed tasks
    - Track failed tasks
    """

    def __init__(self) -> None:
        self._pending: Set[str] = set()
        self._running: Set[str] = set()
        self._completed: Dict[str, TaskResult] = {}
        self._failed: Dict[str, TaskResult] = {}

    def add_task(self, task_id: str) -> None:
        """Register a task as pending."""
        self._pending.add(task_id)

    def mark_running(self, task_id: str) -> None:
        """Move a task from pending to running."""
        self._pending.discard(task_id)
        self._running.add(task_id)

    def mark_completed(self, result: TaskResult) -> None:
        """Mark a task as successfully completed."""
        self._running.discard(result.task_id)
        self._completed[result.task_id] = result

    def mark_failed(self, result: TaskResult) -> None:
        """Mark a task as failed."""
        self._running.discard(result.task_id)
        self._failed[result.task_id] = result

    def is_completed(self, task_id: str) -> bool:
        return task_id in self._completed

    def is_failed(self, task_id: str) -> bool:
        return task_id in self._failed

    def is_running(self, task_id: str) -> bool:
        return task_id in self._running

    def is_pending(self, task_id: str) -> bool:
        return task_id in self._pending

    @property
    def pending(self) -> Set[str]:
        return set(self._pending)

    @property
    def running(self) -> Set[str]:
        return set(self._running)

    @property
    def completed(self) -> Dict[str, TaskResult]:
        return dict(self._completed)

    @property
    def failed(self) -> Dict[str, TaskResult]:
        return dict(self._failed)

    @property
    def finished(self) -> bool:
        """
        Returns True when there are no pending or running tasks.
        """
        return not self._pending and not self._running