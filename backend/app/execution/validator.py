from __future__ import annotations

from typing import Set

from app.planning.models.execution_plan import ExecutionPlan


class ValidationError(Exception):
    """Raised when an execution plan is invalid."""


class ExecutionValidator:
    """
    Validates execution plans before execution begins.
    """

    def validate(self, plan: ExecutionPlan) -> None:
        self._validate_not_empty(plan)
        self._validate_unique_ids(plan)
        self._validate_required_fields(plan)
        self._validate_dependencies(plan)
        self._validate_self_dependencies(plan)
        self._validate_roots(plan)
        self._validate_cycles(plan)

    def _validate_not_empty(self, plan: ExecutionPlan):
        if not plan.tasks:
            raise ValidationError("Execution plan contains no tasks.")

    def _validate_unique_ids(self, plan: ExecutionPlan):
        seen = set()

        for task in plan.tasks:
            if task.id in seen:
                raise ValidationError(
                    f"Duplicate task id: {task.id}"
                )
            seen.add(task.id)

    def _validate_required_fields(self, plan: ExecutionPlan):
        for task in plan.tasks:
            if not task.id:
                raise ValidationError("Task missing id.")

            if not task.name:
                raise ValidationError(
                    f"Task {task.id} missing name."
                )

            if not task.tool:
                raise ValidationError(
                    f"Task {task.id} missing tool."
                )

    def _validate_dependencies(self, plan: ExecutionPlan):
        ids = {task.id for task in plan.tasks}

        for task in plan.tasks:
            for dep in task.dependencies:
                if dep not in ids:
                    raise ValidationError(
                        f"Task {task.id} depends on unknown task {dep}"
                    )

    def _validate_self_dependencies(self, plan: ExecutionPlan):
        for task in plan.tasks:
            if task.id in task.dependencies:
                raise ValidationError(
                    f"Task {task.id} depends on itself."
                )

    def _validate_roots(self, plan: ExecutionPlan):
        roots = [
            task
            for task in plan.tasks
            if not task.dependencies
        ]

        if not roots:
            raise ValidationError(
                "Execution plan has no root task."
            )

    def _validate_cycles(self, plan: ExecutionPlan):
        graph = {
            task.id: task.dependencies
            for task in plan.tasks
        }

        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(node: str):
            if node in stack:
                raise ValidationError(
                    "Circular dependency detected."
                )

            if node in visited:
                return

            stack.add(node)

            for dep in graph[node]:
                dfs(dep)

            stack.remove(node)
            visited.add(node)

        for node in graph:
            dfs(node)