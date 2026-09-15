
"""
app/execution/worker.py

Canonical execution worker.

ExecutionEngine
    ↓
Dispatcher
    ↓
Worker
    ↓
AgentManager
    ↓
BaseAgent
    ↓
Specialized Agent

Worker receives the canonical AgentContext and passes the
EXACT SAME OBJECT to AgentManager.

Worker MUST NOT:

- create AgentContext
- call AgentContext.from_dict()
- serialize/deserialize context
- create AgentServices
- create CompanyRepository
- create execution_id
- construct an agent-specific input dictionary
- execute specialized agents directly
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.manager.agent_manager import AgentManager
from app.execution.models.task_result import TaskResult
from app.planning.models.task import Task


logger = logging.getLogger(__name__)


class Worker:
    """Execute one Task through AgentManager."""

    def __init__(
        self,
        agent_manager: AgentManager,
    ) -> None:
        if agent_manager is None:
            raise ValueError(
                "AgentManager is required."
            )

        if not isinstance(
            agent_manager,
            AgentManager,
        ):
            raise TypeError(
                "agent_manager must be an AgentManager instance"
            )

        self.agent_manager = agent_manager

    # =========================================================
    # Public API
    # =========================================================

    async def run(
        self,
        task: Task,
        context: AgentContext,
    ) -> TaskResult:
        """
        Execute one Task using the existing AgentContext.

        The object received here is the object passed to
        AgentManager. No reconstruction occurs.
        """

        self._validate_task(task)
        self._validate_context(context)

        # -----------------------------------------------------
        # CRITICAL:
        # Do not call AgentContext.from_dict().
        # Do not copy the object.
        # -----------------------------------------------------

        agent_context = context

        if agent_context.research_id is None:
            raise ValueError(
                "Worker received AgentContext without research_id."
            )

        # -----------------------------------------------------
        # Canonical task routing
        # -----------------------------------------------------

        agent_name = self._resolve_agent_name(task)

        if not agent_name:
            raise ValueError(
                f"Task '{task.id}' does not specify an agent_name."
            )

        # -----------------------------------------------------
        # ExecutionEngine owns execution_id.
        # -----------------------------------------------------

        execution_id = agent_context.get_metadata(
            "execution_id"
        )

        if not execution_id:
            raise ValueError(
                "Worker received AgentContext without execution_id. "
                "ExecutionEngine must initialize execution_id "
                "before dispatch."
            )

        execution_id = str(execution_id)

        # -----------------------------------------------------
        # Trace ID
        #
        # execution_id remains ExecutionEngine-owned.
        # trace_id is execution tracing metadata.
        # -----------------------------------------------------

        trace_id = agent_context.get_metadata(
            "trace_id"
        )

        if not trace_id:
            trace_id = str(uuid.uuid4())

            agent_context.set_metadata(
                "trace_id",
                trace_id,
            )

        trace_id = str(trace_id)

        # -----------------------------------------------------
        # Establish task runtime identity.
        # -----------------------------------------------------

        task_type = getattr(
            task,
            "task_type",
            None,
        )

        agent_context.set_task(
            task_id=task.id,
            task_type=(
                str(task_type)
                if task_type is not None
                else None
            ),
            assigned_executor=agent_name,
        )

        # -----------------------------------------------------
        # Establish current agent.
        # -----------------------------------------------------

        agent_context.set_current_agent(
            agent_name
        )

        # -----------------------------------------------------
        # Runtime metadata.
        # -----------------------------------------------------

        agent_context.set_metadata(
            "execution_id",
            execution_id,
        )

        agent_context.set_metadata(
            "trace_id",
            trace_id,
        )

        agent_context.set_metadata(
            "agent_name",
            agent_name,
        )

        # -----------------------------------------------------
        # Task metadata.
        # -----------------------------------------------------

        task_metadata = self._extract_task_metadata(task)

        if task_metadata:
            agent_context.set_metadata(
                "task_metadata",
                task_metadata,
            )
        else:
            agent_context.metadata.pop(
                "task_metadata",
                None,
            )

        # -----------------------------------------------------
        # Identity logging.
        # -----------------------------------------------------

        logger.info(
            "Worker dispatch | "
            "task=%s | "
            "agent=%s | "
            "research_id=%r | "
            "company_id=%r | "
            "ticker=%r | "
            "execution_id=%s | "
            "trace_id=%s | "
            "context_object_id=%s",
            task.id,
            agent_name,
            agent_context.research_id,
            agent_context.company_id,
            agent_context.ticker,
            execution_id,
            trace_id,
            id(agent_context),
        )

        started_at = datetime.now(timezone.utc)

        # =====================================================
        # AgentManager boundary
        # =====================================================

        try:
            result = await self.agent_manager.execute(
                agent_name=agent_name,
                context=agent_context,
            )

            # -------------------------------------------------
            # Diagnostic identity verification.
            #
            # AgentManager should pass this exact object onward.
            # -------------------------------------------------

            logger.info(
                "Worker returned from AgentManager | "
                "task=%s | "
                "agent=%s | "
                "research_id=%r | "
                "company_id=%r | "
                "context_object_id=%s",
                task.id,
                agent_name,
                agent_context.research_id,
                agent_context.company_id,
                id(agent_context),
            )

            completed_at = datetime.now(timezone.utc)

            # =================================================
            # Canonical AgentResult
            # =================================================

            if isinstance(result, AgentResult):
                return self._build_agent_result(
                    task=task,
                    result=result,
                    execution_id=execution_id,
                    trace_id=trace_id,
                    started_at=started_at,
                    completed_at=completed_at,
                    agent_name=agent_name,
                )

            # =================================================
            # Existing TaskResult
            # =================================================

            if isinstance(result, TaskResult):
                return self._normalize_task_result(
                    task=task,
                    result=result,
                    execution_id=execution_id,
                    trace_id=trace_id,
                    started_at=started_at,
                    completed_at=completed_at,
                    agent_name=agent_name,
                )

            # =================================================
            # Legacy arbitrary result
            # =================================================

            logger.warning(
                "AgentManager returned non-standard result | "
                "task=%s | "
                "agent=%s | "
                "result_type=%s",
                task.id,
                agent_name,
                type(result).__name__,
            )

            return TaskResult(
                task_id=task.id,
                success=True,
                execution_id=execution_id,
                trace_id=trace_id,
                output=result,
                error=None,
                started_at=started_at,
                completed_at=completed_at,
                metadata={
                    "agent_name": agent_name,
                    "legacy_result": True,
                },
            )

        except Exception as exc:
            completed_at = datetime.now(timezone.utc)

            logger.exception(
                "Task execution failed | "
                "task=%s | "
                "agent=%s | "
                "research_id=%r | "
                "company_id=%r | "
                "execution_id=%s | "
                "trace_id=%s | "
                "context_object_id=%s",
                task.id,
                agent_name,
                agent_context.research_id,
                agent_context.company_id,
                execution_id,
                trace_id,
                id(agent_context),
            )

            return TaskResult(
                task_id=task.id,
                success=False,
                execution_id=execution_id,
                trace_id=trace_id,
                output=None,
                error=str(exc),
                started_at=started_at,
                completed_at=completed_at,
                metadata={
                    "agent_name": agent_name,
                    "exception_type": type(exc).__name__,
                },
            )

        finally:
            # -------------------------------------------------
            # DO NOT clear context.
            #
            # Other tasks may use the same execution context.
            # ExecutionEngine owns final lifecycle cleanup.
            # -------------------------------------------------
            pass

    # =========================================================
    # Validation
    # =========================================================

    @staticmethod
    def _validate_task(task: Task) -> None:
        if not isinstance(task, Task):
            raise TypeError(
                "Worker expected Task instance, "
                f"received {type(task).__name__}."
            )

        task_id = getattr(task, "id", None)

        if task_id is None:
            raise ValueError(
                "Worker received Task without id."
            )

    @staticmethod
    def _validate_context(
        context: AgentContext,
    ) -> None:
        if not isinstance(context, AgentContext):
            raise TypeError(
                "Worker requires the canonical AgentContext "
                "created by ResearchService."
            )

    # =========================================================
    # Agent routing
    # =========================================================

    @staticmethod
    def _resolve_agent_name(
        task: Task,
    ) -> str | None:
        """
        Resolve agent using canonical Task.agent_name.

        assigned_executor exists only for persisted legacy tasks.
        """

        agent_name = getattr(
            task,
            "agent_name",
            None,
        )

        if agent_name:
            return str(agent_name)

        legacy_executor = getattr(
            task,
            "assigned_executor",
            None,
        )

        if legacy_executor:
            logger.warning(
                "Task '%s' uses legacy assigned_executor='%s'. "
                "Migrate task to agent_name.",
                getattr(task, "id", None),
                legacy_executor,
            )

            return str(legacy_executor)

        return None

    # =========================================================
    # Task metadata
    # =========================================================

    @staticmethod
    def _extract_task_metadata(
        task: Task,
    ) -> dict[str, Any]:
        """
        Extract observational task metadata.

        This metadata is NOT used as agent input.
        """

        metadata: dict[str, Any] = {}

        for field_name in (
            "name",
            "description",
            "task_type",
            "priority",
            "status",
        ):
            value = getattr(
                task,
                field_name,
                None,
            )

            if value is not None:
                metadata[field_name] = value

        agent_name = getattr(
            task,
            "agent_name",
            None,
        )

        if agent_name:
            metadata["agent_name"] = str(agent_name)

        task_metadata = getattr(
            task,
            "metadata",
            None,
        )

        if isinstance(task_metadata, dict):
            # -------------------------------------------------
            # Do not permit arbitrary task metadata to replace
            # canonical execution identity.
            # -------------------------------------------------
            protected_keys = {
                "execution_id",
                "research_id",
                "company_id",
                "agent_name",
                "task_id",
                "trace_id",
            }

            for key, value in task_metadata.items():
                if key not in protected_keys:
                    metadata[key] = value

        return metadata

    # =========================================================
    # AgentResult -> TaskResult
    # =========================================================

    @staticmethod
    def _build_agent_result(
        task: Task,
        result: AgentResult,
        execution_id: str,
        trace_id: str,
        started_at: datetime,
        completed_at: datetime,
        agent_name: str,
    ) -> TaskResult:
        """
        Convert AgentResult into execution-layer TaskResult.

        Supports both the current `succeeded` property and
        legacy `success` property.
        """

        result_metadata = dict(
            getattr(result, "metadata", None) or {}
        )

        status = getattr(
            result,
            "status",
            None,
        )

        status_value = (
            status.value
            if hasattr(status, "value")
            else str(status)
            if status is not None
            else None
        )

        succeeded = getattr(
            result,
            "succeeded",
            None,
        )

        if succeeded is None:
            succeeded = getattr(
                result,
                "success",
                None,
            )

        if succeeded is None:
            succeeded = (
                getattr(result, "error", None)
                is None
            )

        result_metadata.update(
            {
                "agent_name": (
                    getattr(
                        result,
                        "agent_name",
                        None,
                    )
                    or agent_name
                ),
                "agent_status": status_value,
                "confidence": getattr(
                    result,
                    "confidence",
                    None,
                ),
                "sources": getattr(
                    result,
                    "sources",
                    None,
                ),
                "reasoning": getattr(
                    result,
                    "reasoning",
                    None,
                ),
                "execution_time": getattr(
                    result,
                    "execution_time",
                    None,
                ),
            }
        )

        return TaskResult(
            task_id=task.id,
            success=bool(succeeded),
            execution_id=execution_id,
            trace_id=trace_id,
            output=getattr(result, "data", None),
            error=getattr(result, "error", None),
            started_at=started_at,
            completed_at=completed_at,
            metadata=result_metadata,
        )

    # =========================================================
    # TaskResult normalization
    # =========================================================

    @staticmethod
    def _normalize_task_result(
        task: Task,
        result: TaskResult,
        execution_id: str,
        trace_id: str,
        started_at: datetime,
        completed_at: datetime,
        agent_name: str,
    ) -> TaskResult:
        metadata = dict(
            getattr(result, "metadata", None) or {}
        )

        metadata.setdefault(
            "agent_name",
            agent_name,
        )

        return TaskResult(
            task_id=task.id,
            success=bool(result.success),
            execution_id=(
                result.execution_id
                or execution_id
            ),
            trace_id=(
                result.trace_id
                or trace_id
            ),
            output=result.output,
            error=result.error,
            started_at=(
                result.started_at
                or started_at
            ),
            completed_at=(
                result.completed_at
                or completed_at
            ),
            metadata=metadata,
        )

    # =========================================================
    # Compatibility alias
    # =========================================================

    async def execute(
        self,
        task: Task,
        context: AgentContext,
    ) -> TaskResult:
        """Backward-compatible alias for run()."""

        return await self.run(
            task=task,
            context=context,
        )

