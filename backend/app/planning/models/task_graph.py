
"""
app/planning/models/task_graph.py

Canonical dependency graph representation produced by
the Planning Engine.

Responsibilities:
- Store tasks
- Store dependency relationships
- Maintain parent/child relationships
- Provide graph access helpers

Does NOT:
- Execute tasks
- Schedule tasks
- Validate cycles
- Run graph algorithms

Canonical dependency contract:

    task_id depends on dependency_id

Example:

    company_research
            |
            v
    financial_analysis
            |
            v
        valuation

Therefore:

    financial_analysis.dependencies
        = ["company_research"]

    valuation.dependencies
        = ["financial_analysis"]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterator, List

from .task import Task


@dataclass
class TaskGraph:
    """
    Directed dependency graph of executable Tasks.

    The graph maintains two complementary relationships:

        dependencies[task_id]
            -> tasks that must complete first

        children[task_id]
            -> tasks that depend on this task

    Example:

        A -> B -> C

    means:

        dependencies["B"] == ["A"]
        dependencies["C"] == ["B"]

        children["A"] == ["B"]
        children["B"] == ["C"]
    """

    # ======================================================
    # Storage
    # ======================================================

    # task_id -> Task
    tasks: Dict[str, Task] = field(
        default_factory=dict
    )

    # task_id -> prerequisite task ids
    dependencies: Dict[str, List[str]] = field(
        default_factory=dict
    )

    # task_id -> dependent task ids
    children: Dict[str, List[str]] = field(
        default_factory=dict
    )

    # Optional graph metadata populated by GraphBuilder.
    metadata: Dict[str, object] = field(
        default_factory=dict
    )

    # ======================================================
    # Task Registration
    # ======================================================

    def add_task(
        self,
        task: Task,
    ) -> None:
        """
        Register a Task inside the graph.

        Dependency edges are registered separately through
        add_dependency().

        This keeps graph construction deterministic:

            add_task()
                |
                v
            add_dependency()
        """

        if not isinstance(
            task,
            Task,
        ):
            raise TypeError(
                "TaskGraph requires a Task instance. "
                f"Got {type(task).__name__}."
            )

        if not task.id:
            raise ValueError(
                "Cannot register a Task without an id."
            )

        if task.id in self.tasks:
            raise ValueError(
                f"Task '{task.id}' is already registered "
                "in the graph."
            )

        self.tasks[task.id] = task

        self.dependencies.setdefault(
            task.id,
            [],
        )

        self.children.setdefault(
            task.id,
            []

        )

    # ======================================================
    # Dependency Management
    # ======================================================

    def add_dependency(
        self,
        task_id: str,
        dependency_id: str,
    ) -> None:
        """
        Register a dependency edge.

        Canonical meaning:

            task_id depends on dependency_id

        Example:

            company_research
                    |
                    v
            financial_analysis

        Call:

            add_dependency(
                task_id="financial_analysis",
                dependency_id="company_research",
            )

        This creates:

            dependencies["financial_analysis"]
                -> ["company_research"]

            children["company_research"]
                -> ["financial_analysis"]
        """

        if not task_id:
            raise ValueError(
                "task_id is required."
            )

        if not dependency_id:
            raise ValueError(
                "dependency_id is required."
            )

        if task_id == dependency_id:
            raise ValueError(
                f"Task '{task_id}' cannot depend on itself."
            )

        # --------------------------------------------------
        # Both tasks must already exist.
        # --------------------------------------------------

        if task_id not in self.tasks:
            raise KeyError(
                f"Cannot add dependency: task "
                f"'{task_id}' is not registered."
            )

        if dependency_id not in self.tasks:
            raise KeyError(
                f"Cannot add dependency: dependency "
                f"'{dependency_id}' is not registered."
            )

        # --------------------------------------------------
        # Register dependency relationship.
        # --------------------------------------------------

        task_dependencies = self.dependencies.setdefault(
            task_id,
            [],
        )

        if dependency_id not in task_dependencies:
            task_dependencies.append(
                dependency_id
            )

        # --------------------------------------------------
        # Register reverse child relationship.
        # --------------------------------------------------

        dependency_children = self.children.setdefault(
            dependency_id,
            [],
        )

        if task_id not in dependency_children:
            dependency_children.append(
                task_id
            )

        # --------------------------------------------------
        # Synchronize Task model.
        #
        # TaskGraph remains the graph authority, while the
        # Task object reflects the same relationship.
        # --------------------------------------------------

        task = self.tasks[task_id]

        if dependency_id not in task.dependencies:
            task.dependencies.append(
                dependency_id
            )

        parent = self.tasks[dependency_id]

        if task_id not in parent.child_tasks:
            parent.child_tasks.append(
                task_id
            )

    # ======================================================
    # Accessors
    # ======================================================

    def get_task(
        self,
        task_id: str,
    ) -> Task:
        """
        Retrieve a Task by id.
        """

        if task_id not in self.tasks:
            raise KeyError(
                f"Task '{task_id}' does not exist "
                "in the graph."
            )

        return self.tasks[task_id]

    def get_dependencies(
        self,
        task_id: str,
    ) -> List[str]:
        """
        Return prerequisite task ids.

        Returns an empty list when the task has no
        dependencies.
        """

        if task_id not in self.tasks:
            raise KeyError(
                f"Task '{task_id}' does not exist "
                "in the graph."
            )

        return list(
            self.dependencies.get(
                task_id,
                [],
            )
        )

    def get_children(
        self,
        task_id: str,
    ) -> List[str]:
        """
        Return task ids that depend on this task.
        """

        if task_id not in self.tasks:
            raise KeyError(
                f"Task '{task_id}' does not exist "
                "in the graph."
            )

        return list(
            self.children.get(
                task_id,
                [],
            )
        )

    def all_tasks(self) -> List[Task]:
        """
        Return all registered Tasks.

        Used by:
        - Scheduler
        - Validator
        - Execution Engine
        """

        return list(
            self.tasks.values()
        )

    # ======================================================
    # Graph Helpers
    # ======================================================

    def root_tasks(self) -> List[Task]:
        """
        Return tasks with no dependencies.

        Root tasks can execute immediately.
        """

        return [
            task
            for task in self.tasks.values()
            if not self.dependencies.get(
                task.id
            )
        ]

    def leaf_tasks(self) -> List[Task]:
        """
        Return tasks with no children.

        Leaf tasks represent graph completion points.
        """

        return [
            task
            for task in self.tasks.values()
            if not self.children.get(
                task.id
            )
        ]

    def contains(
        self,
        task_id: str,
    ) -> bool:
        """
        Return True when task_id exists in the graph.
        """

        return task_id in self.tasks

    # ======================================================
    # Python Protocols
    # ======================================================

    def __contains__(
        self,
        task_id: str,
    ) -> bool:
        """
        Support:

            if task_id in graph
        """

        return task_id in self.tasks

    def __len__(
        self,
    ) -> int:
        """
        Return number of registered tasks.
        """

        return len(
            self.tasks
        )

    def __iter__(
        self,
    ) -> Iterator[Task]:
        """
        Iterate over registered Tasks.
        """

        return iter(
            self.tasks.values()
        )

