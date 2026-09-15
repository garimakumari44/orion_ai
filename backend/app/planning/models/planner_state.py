from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .execution_plan import ExecutionPlan
from .task_graph import TaskGraph
from .task import Task


class PlanningStatus(str, Enum):
    CREATED = "created"
    PARSED = "parsed"
    TASKS_CREATED = "tasks_created"
    GRAPH_BUILT = "graph_built"
    SCHEDULED = "scheduled"
    VALIDATED = "validated"
    READY = "ready"
    FAILED = "failed"


@dataclass
class PlannerState:
    """
    Shared state flowing through the planning pipeline.

    PlannerState is the memory object of the planner.

    It stores:
    - user input
    - parsed intent
    - generated tasks
    - task graph
    - scheduling result
    - validation result
    - final execution plan

    It does NOT:
    - create plans
    - execute tasks
    """

    user_query: str = ""

    intent: dict[str, Any] = field(default_factory=dict)

    tasks: list[Task] = field(default_factory=list)

    graph: TaskGraph | None = None

    execution_stages: list[list[Task]] = field(default_factory=list)

    execution_plan: ExecutionPlan | None = None


    status: PlanningStatus = PlanningStatus.CREATED


    is_valid: bool = False

    validation_errors: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)


    artifacts: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)


    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


    def update_status(self, status: PlanningStatus):
        self.status = status
        self.updated_at = datetime.now(timezone.utc)