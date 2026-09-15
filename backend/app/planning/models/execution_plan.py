from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .task_graph import TaskGraph


@dataclass(frozen=True)
class ExecutionPlan:
    """
    Immutable execution artifact produced by the planning system.

    Flow:

        User Request
              |
              v
          Planner
              |
              v
        ExecutionPlan
              |
              v
        Execution Engine

    Responsibilities
    ----------------
    - Store original request information.
    - Store finalized TaskGraph.
    - Define execution order.
    - Carry memory context.
    - Define execution policies.
    - Provide runtime metadata.

    Does NOT:
    - Execute tasks.
    - Schedule workers.
    - Call tools.
    - Modify memory.
    """

    # ==========================================================
    # Required Fields (Must Come First)
    # ==========================================================

    # Identity
    id: str

    # Request Context
    query: str
    intent: str

    # Workflow Graph
    graph: TaskGraph

    # ==========================================================
    # Optional Fields (Defaults)
    # ==========================================================

    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    # Agent Information
    agent_type: str = "general"

    # Workflow
    execution_order: Tuple[str, ...] = field(default_factory=tuple)
    root_tasks: Tuple[str, ...] = field(default_factory=tuple)
    leaf_tasks: Tuple[str, ...] = field(default_factory=tuple)

    # Tool Requirements
    required_tools: Tuple[str, ...] = field(default_factory=tuple)

    # Memory
    memory_context: Dict[str, Any] = field(default_factory=dict)
    memory_updates: Dict[str, Any] = field(default_factory=dict)
    use_memory: bool = False

    # Execution Configuration
    execution_policy: Dict[str, Any] = field(default_factory=dict)

    # Planner Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ==========================================================
    # Derived Properties
    # ==========================================================

    @property
    def total_tasks(self) -> int:
        """Total number of tasks."""
        return len(self.graph.tasks)

    @property
    def total_execution_steps(self) -> int:
        """Number of execution steps."""
        return len(self.execution_order)

    @property
    def has_memory_context(self) -> bool:
        return bool(self.memory_context)

    @property
    def has_memory_updates(self) -> bool:
        return bool(self.memory_updates)

    @property
    def memory_types(self) -> List[str]:
        return list(self.memory_context.keys())

    @property
    def requires_tools(self) -> bool:
        return bool(self.required_tools)

    @property
    def confidence(self) -> Optional[float]:
        """
        Planner confidence score.

        Used for:
        - planner evaluation
        - reinforcement feedback
        - self improvement
        """
        return self.metadata.get("confidence")

    # ==========================================================
    # Validation Helpers
    # ==========================================================

    def is_empty(self) -> bool:
        """Check whether plan has no executable tasks."""
        return self.total_tasks == 0

    def summary(self) -> Dict[str, Any]:
        """Lightweight API/debug representation."""
        return {
            "id": self.id,
            "intent": self.intent,
            "agent": self.agent_type,
            "tasks": self.total_tasks,
            "steps": self.total_execution_steps,
            "tools": list(self.required_tools),
            "memory_enabled": self.use_memory,
            "confidence": self.confidence,
        }

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            "ExecutionPlan("
            f"id={self.id!r}, "
            f"intent={self.intent!r}, "
            f"agent={self.agent_type!r}, "
            f"tasks={self.total_tasks}, "
            f"steps={self.total_execution_steps}, "
            f"tools={list(self.required_tools)}, "
            f"use_memory={self.use_memory}"
            ")"
        )