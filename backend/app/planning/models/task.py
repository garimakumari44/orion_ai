"""
app/planning/models/task.py

Canonical Task model for the Planning Engine.

Represents a single executable unit of work.

Shared by:
- Planner
- Graph Builder
- Scheduler
- Orchestration Layer
- Execution Engine
- Agents
- Monitoring
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# Task Status
# ==========================================================


class TaskStatus(str, Enum):
    """Lifecycle state of a task."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ==========================================================
# Task Priority
# ==========================================================


class TaskPriority(str, Enum):
    """Scheduling priority."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ==========================================================
# Task Type
# ==========================================================


class TaskType(str, Enum):
    """Supported task categories."""

    RETRIEVE = "retrieve"

    SEARCH = "search"
    WEB_SEARCH = "web_search"
    NEWS_SEARCH = "news_search"

    COMPANY_LOOKUP = "company_lookup"
    FINANCIAL_DATA = "financial_data"
    MARKET_DATA = "market_data"
    FUNDAMENTALS = "fundamentals"
    SEC_FILING = "sec_filing"

    EXTRACT_INFORMATION = "extract_information"

    ANALYZE = "analyze"
    REASON = "reason"
    COMPARE = "compare"

    PLAN = "plan"
    DESIGN = "design"
    EXECUTE = "execute"

    SUMMARIZE = "summarize"

    VALIDATE = "validate"

    GENERATE_REPORT = "generate_report"

    DENSE_RETRIEVAL = "dense_retrieval"
    SPARSE_RETRIEVAL = "sparse_retrieval"
    HYBRID_RETRIEVAL = "hybrid_retrieval"
    GRAPH_RETRIEVAL = "graph_retrieval"

    MEMORY_STORE = "memory_store"
    MEMORY_EXTRACT = "memory_extract"
    MEMORY_CONSOLIDATE = "memory_consolidate"


# ==========================================================
# Execution Mode
# ==========================================================


class ExecutionMode(str, Enum):
    """How execution should happen."""

    SYNC = "sync"
    ASYNC = "async"
    STREAM = "stream"


# ==========================================================
# Failure Policy
# ==========================================================


class FailurePolicy(str, Enum):
    """Defines behavior after task failure."""

    STOP = "stop"
    RETRY = "retry"
    SKIP = "skip"


# ==========================================================
# Task Model
# ==========================================================


class Task(BaseModel):
    """
    Canonical executable unit.

    Flow:

        Planner
           |
           v
        Task
           |
           v
        TaskGraph
           |
           v
        Scheduler
           |
           v
        Execution Plan
           |
           v
        Execution Engine
           |
           v
        Worker
           |
           v
        AgentManager
           |
           v
        Registered Agent
    """

    # ------------------------------------------------------
    # Identity
    # ------------------------------------------------------

    id: str = Field(
        ...,
        description="Unique task identifier",
    )

    title: str = Field(
        ...,
        description="Human readable task name",
    )

    description: Optional[str] = Field(
        default=None,
        description="Detailed task explanation",
    )

    # ------------------------------------------------------
    # Classification
    # ------------------------------------------------------

    task_type: TaskType = Field(
        ...,
        description="Task category",
    )

    capability: Optional[str] = Field(
        default=None,
        description="Required system capability",
    )

    # ------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------

    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
    )

    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
    )

    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.ASYNC,
    )

    failure_policy: FailurePolicy = Field(
        default=FailurePolicy.RETRY,
    )

    # ------------------------------------------------------
    # Dependency Graph
    # ------------------------------------------------------

    dependencies: List[str] = Field(
        default_factory=list,
        description="Tasks that must complete first",
    )

    parent_task: Optional[str] = Field(
        default=None,
    )

    child_tasks: List[str] = Field(
        default_factory=list,
    )

    parallelizable: bool = Field(
        default=True,
    )

    # ------------------------------------------------------
    # Execution Parameters
    # ------------------------------------------------------

    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Planner generated arguments",
    )

    estimated_duration: Optional[float] = Field(
        default=None,
        description="Estimated execution duration in seconds",
    )

    timeout_seconds: Optional[int] = Field(
        default=None,
        description="Maximum execution time in seconds",
    )

    cost: str = Field(
        default="low",
        description="Estimated relative execution cost",
    )

    # ------------------------------------------------------
    # Tool Routing
    # ------------------------------------------------------

    selected_tool: Optional[str] = Field(
        default=None,
        description="Tool chosen by ToolRouter",
    )

    allowed_tools: List[str] = Field(
        default_factory=list,
        description="Tools allowed for this task",
    )

    tool_request: Dict[str, Any] = Field(
        default_factory=dict,
    )

    # ------------------------------------------------------
    # Agent Routing
    # ------------------------------------------------------

    agent_name: Optional[str] = Field(
        default=None,
        description="Registered agent responsible for executing the task",
    )

    # ------------------------------------------------------
    # Execution Result
    # ------------------------------------------------------

    result: Optional[Any] = Field(
        default=None,
    )

    error: Optional[str] = Field(
        default=None,
    )

    retry_count: int = Field(
        default=0,
    )

    max_retries: int = Field(
        default=3,
    )

    # ------------------------------------------------------
    # Runtime Tracking
    # ------------------------------------------------------

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    started_at: Optional[datetime] = Field(
        default=None,
    )

    completed_at: Optional[datetime] = Field(
        default=None,
    )

    duration_seconds: Optional[float] = Field(
        default=None,
    )

    # ------------------------------------------------------
    # Planner Metadata
    # ------------------------------------------------------

    planner_reasoning: Optional[str] = Field(
        default=None,
        description="Why the planner created this task",
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
    )

    # ------------------------------------------------------
    # Pydantic Configuration
    # ------------------------------------------------------

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        extra="forbid",
    )

    # ======================================================
    # Priority Inference
    # ======================================================

    def _infer_priority(self) -> TaskPriority:
        """
        Infer task priority from task type.

        This helper does not automatically overwrite an
        explicitly assigned priority.
        """

        high_priority_types = {
            TaskType.PLAN,
            TaskType.EXECUTE,
            TaskType.VALIDATE,
            TaskType.GENERATE_REPORT,
            TaskType.REASON,
        }

        low_priority_types = {
            TaskType.MEMORY_STORE,
            TaskType.MEMORY_EXTRACT,
            TaskType.MEMORY_CONSOLIDATE,
            TaskType.SUMMARIZE,
        }

        if self.task_type in high_priority_types:
            return TaskPriority.HIGH

        if self.task_type in low_priority_types:
            return TaskPriority.LOW

        return TaskPriority.MEDIUM