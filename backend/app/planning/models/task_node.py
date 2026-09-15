"""
planning/models/task_node.py

Node representation inside the Planning Graph.

TaskNode wraps a Task and stores graph-only
relationships.

Responsibilities:
- Represent a task inside dependency graph
- Track dependencies
- Track dependent tasks
- Support graph traversal

Does NOT:
- Execute tasks
- Schedule tasks
- Validate graph correctness
"""


from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Set, Optional

from .task import Task


@dataclass(slots=True)
class TaskNode:
    """
    A node in the planning task graph.

    Wraps a Task and stores graph relationships.

    Used by:
    - GraphBuilder
    - Planner analysis
    - Scheduler preparation
    - ExecutionPlan generation
    """


    # ------------------------------------------------------
    # Wrapped Task
    # ------------------------------------------------------

    task: Task


    # ------------------------------------------------------
    # Graph Relationships
    # ------------------------------------------------------

    # Tasks that must complete before this task
    dependencies: Set[str] = field(
        default_factory=set
    )


    # Tasks waiting on this task
    dependents: Set[str] = field(
        default_factory=set
    )


    # ------------------------------------------------------
    # Graph Metadata
    # ------------------------------------------------------

    depth: Optional[int] = None


    visited: bool = False


    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


    # ------------------------------------------------------
    # Relationship Management
    # ------------------------------------------------------

    def add_dependency(
        self,
        task_id: str
    ) -> None:
        """
        Add prerequisite task.
        """

        if task_id != self.id:

            self.dependencies.add(
                task_id
            )


    def add_dependent(
        self,
        task_id: str
    ) -> None:
        """
        Add dependent task.
        """

        if task_id != self.id:

            self.dependents.add(
                task_id
            )


    def remove_dependency(
        self,
        task_id: str
    ) -> None:

        self.dependencies.discard(
            task_id
        )


    def remove_dependent(
        self,
        task_id: str
    ) -> None:

        self.dependents.discard(
            task_id
        )


    # ------------------------------------------------------
    # Properties
    # ------------------------------------------------------

    @property
    def id(self) -> str:
        """
        Task identifier.
        """

        return self.task.id


    @property
    def status(self):
        """
        Current task execution status.
        """

        return self.task.status


    @property
    def is_root(self) -> bool:
        """
        True when no prerequisites exist.
        """

        return len(self.dependencies) == 0


    @property
    def is_leaf(self) -> bool:
        """
        True when nothing depends on this task.
        """

        return len(self.dependents) == 0


    # ------------------------------------------------------
    # Serialization
    # ------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert node into serializable graph format.
        """

        return {
            "id": self.id,
            "task": self.task.model_dump(),
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "depth": self.depth,
            "metadata": self.metadata,
        }