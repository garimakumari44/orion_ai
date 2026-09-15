"""
app/execution/execution_engine.py

Execution Engine
================

Pure orchestration boundary for executing an ExecutionPlan.

Canonical execution flow:

    ResearchService
          |
          | creates AgentContext exactly once
          v
    ExecutionEngine
          |
          | same AgentContext
          v
      Dispatcher
          |
          | same AgentContext
          v
        Worker
          |
          | same AgentContext
          v
     AgentManager
          |
          | same AgentContext
          v
       BaseAgent
          |
          v
   Specialized Agent


ARCHITECTURAL RULES
-------------------

1. ExecutionEngine MUST receive an AgentContext.

2. ExecutionEngine MUST NOT create an AgentContext.

3. ExecutionEngine MUST NOT reconstruct an AgentContext.

4. ExecutionEngine MUST NOT access the database.

5. ExecutionEngine MUST NOT resolve Research records.

6. ExecutionEngine MUST NOT resolve Company records.

7. ExecutionEngine MUST NOT execute agents directly.

8. ExecutionEngine MUST pass the exact same AgentContext
   instance to Dispatcher.

9. ExecutionEngine owns execution_id.

10. ExecutionEngine owns execution-level orchestration.

11. Worker owns task-level runtime metadata.

12. Task.agent_name is the canonical routing field.

13. Dispatcher/Worker return TaskResult.

14. ExecutionEngine preserves TaskResult semantics.

15. AgentContext object identity must remain unchanged.

16. ExecutionEngine must not create task-specific contexts.

17. ExecutionEngine must not convert AgentContext into dicts.

18. ExecutionEngine must not pass research_id separately as
    a replacement for AgentContext.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.execution.dispatcher import Dispatcher
from app.execution.models.execution_result import ExecutionResult
from app.execution.models.execution_state import ExecutionState
from app.execution.models.task_result import TaskResult
from app.execution.scheduler import TaskScheduler
from app.planning.models.execution_plan import ExecutionPlan


logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    Pure execution orchestration layer.

    ResearchService owns:
        - database
        - Research lifecycle
        - canonical AgentContext creation

    ExecutionEngine owns:
        - execution_id
        - execution-level trace identity
        - scheduling
        - task orchestration
        - execution state
        - execution-level metrics
        - final ExecutionResult

    ExecutionEngine does NOT own:
        - database access
        - Research loading
        - Company loading
        - AgentContext creation
        - Agent construction
        - Agent execution
    """

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        dispatcher: Dispatcher,
        scheduler: TaskScheduler | None = None,
    ) -> None:
        """
        Initialize ExecutionEngine.
        """

        if dispatcher is None:
            raise ValueError(
                "Dispatcher is required."
            )

        if not isinstance(
            dispatcher,
            Dispatcher,
        ):
            raise TypeError(
                "dispatcher must be a Dispatcher instance, "
                f"got {type(dispatcher).__name__}."
            )

        self.dispatcher = dispatcher

        self.scheduler = (
            scheduler
            if scheduler is not None
            else TaskScheduler()
        )

        if not isinstance(
            self.scheduler,
            TaskScheduler,
        ):
            raise TypeError(
                "scheduler must be a TaskScheduler instance, "
                f"got {type(self.scheduler).__name__}."
            )

        logger.info(
            "ExecutionEngine initialized | "
            "dispatcher=%s | "
            "scheduler=%s | "
            "dispatcher_id=%s | "
            "scheduler_id=%s",
            type(self.dispatcher).__name__,
            type(self.scheduler).__name__,
            id(self.dispatcher),
            id(self.scheduler),
        )

    # =========================================================
    # Execute
    # =========================================================

    async def execute(
        self,
        plan: ExecutionPlan,
        *,
        context: AgentContext,
    ) -> ExecutionResult:
        """
        Execute an ExecutionPlan using the canonical AgentContext.

        The supplied AgentContext belongs to ResearchService.

        ExecutionEngine NEVER:

            AgentContext(...)

        or:

            AgentContext(**...)

        or:

            AgentContext.from_dict(...)

        or:

            dict(context)

        The exact same AgentContext object is passed to Dispatcher
        for every task.
        """

        # =====================================================
        # Validate context
        # =====================================================

        if not isinstance(
            context,
            AgentContext,
        ):
            raise TypeError(
                "ExecutionEngine requires an AgentContext "
                "created by ResearchService. "
                f"Got {type(context).__name__}."
            )

        # IMPORTANT:
        #
        # This is only an alias.
        #
        # No copy is made.
        #
        # id(agent_context) == id(context)

        agent_context = context

        original_context_id = id(
            agent_context
        )

        # =====================================================
        # Validate research identity
        # =====================================================

        research_id = (
            agent_context.research_id
        )

        if research_id is None:
            raise ValueError(
                "ExecutionEngine requires "
                "context.research_id."
            )

        # =====================================================
        # Validate plan
        # =====================================================

        if plan is None:
            raise ValueError(
                "ExecutionEngine requires an ExecutionPlan."
            )

        if not isinstance(
            plan,
            ExecutionPlan,
        ):
            raise TypeError(
                "ExecutionEngine requires an ExecutionPlan "
                f"instance, got {type(plan).__name__}."
            )

        # =====================================================
        # Validate graph
        # =====================================================

        graph = getattr(
            plan,
            "graph",
            None,
        )

        if graph is None:
            raise ValueError(
                "ExecutionPlan.graph is required."
            )

        execution_order = list(
            getattr(
                plan,
                "execution_order",
                [],
            )
            or []
        )

        # =====================================================
        # Create execution identity
        # =====================================================

        execution_id = str(
            uuid.uuid4()
        )

        # Preserve an existing trace ID if one already exists.
        existing_trace_id = (
            agent_context.get_metadata(
                "trace_id"
            )
        )

        trace_id = (
            str(existing_trace_id)
            if existing_trace_id
            else str(uuid.uuid4())
        )

        # =====================================================
        # Store execution metadata on SAME context
        # =====================================================

        agent_context.set_metadata(
            "execution_id",
            execution_id,
        )

        agent_context.set_metadata(
            "trace_id",
            trace_id,
        )

        # =====================================================
        # Context checkpoint
        # =====================================================

        self._log_context_checkpoint(
            agent_context,
            execution_id=execution_id,
            trace_id=trace_id,
        )

        # =====================================================
        # Initialize execution state
        # =====================================================

        state = ExecutionState(
            execution_id=execution_id
        )

        state.initialize(
            graph
        )

        # =====================================================
        # Build schedule
        # =====================================================

        schedule = self.scheduler.build_schedule(
            graph
        )

        if schedule is None:
            raise RuntimeError(
                "TaskScheduler returned None instead of a schedule."
            )

        # =====================================================
        # Runtime state
        # =====================================================

        task_results: dict[
            str,
            TaskResult,
        ] = {}

        started = time.perf_counter()

        total_tokens = 0
        total_cost = 0.0

        scheduled_task_count = sum(
            len(stage)
            for stage in schedule
        )

        logger.info(
            "Execution started | "
            "execution_id=%s | "
            "trace_id=%s | "
            "research_id=%s | "
            "company_id=%r | "
            "plan_tasks=%d | "
            "scheduled_tasks=%d | "
            "stages=%d | "
            "context_object_id=%s",
            execution_id,
            trace_id,
            research_id,
            getattr(
                agent_context,
                "company_id",
                None,
            ),
            len(execution_order),
            scheduled_task_count,
            len(schedule),
            original_context_id,
        )

        # =====================================================
        # Execute scheduled stages
        # =====================================================

        for stage_index, stage in enumerate(
            schedule,
            start=1,
        ):
            logger.info(
                "Executing stage | "
                "execution_id=%s | "
                "stage=%d | "
                "tasks=%d | "
                "context_object_id=%s",
                execution_id,
                stage_index,
                len(stage),
                original_context_id,
            )

            for node in stage:

                # =================================================
                # Resolve TaskNode -> Task
                # =================================================

                task = getattr(
                    node,
                    "task",
                    None,
                )

                if task is None:
                    logger.error(
                        "Scheduler returned invalid node | "
                        "execution_id=%s | "
                        "stage=%d",
                        execution_id,
                        stage_index,
                    )

                    continue

                task_id = str(
                    getattr(
                        task,
                        "id",
                        "",
                    )
                )

                if not task_id:
                    logger.error(
                        "Scheduler returned task without id | "
                        "execution_id=%s | "
                        "stage=%d",
                        execution_id,
                        stage_index,
                    )

                    continue

                # =================================================
                # Canonical routing
                # =================================================

                agent_name = getattr(
                    task,
                    "agent_name",
                    None,
                )

                if agent_name is not None:
                    agent_name = str(
                        agent_name
                    ).strip()

                logger.info(
                    "Resolved task | "
                    "execution_id=%s | "
                    "task_id=%s | "
                    "agent_name=%s | "
                    "context_object_id=%s",
                    execution_id,
                    task_id,
                    agent_name,
                    original_context_id,
                )

                # =================================================
                # Validate task routing
                # =================================================

                if not agent_name:
                    error = (
                        f"Task '{task_id}' has no "
                        "assigned agent_name."
                    )

                    result = self._failure_result(
                        task_id=task_id,
                        execution_id=execution_id,
                        trace_id=trace_id,
                        error=error,
                        metadata={
                            "failure_type": (
                                "missing_agent_name"
                            )
                        },
                    )

                    state.mark_failed(
                        task_id,
                        result,
                    )

                    task_results[
                        task_id
                    ] = result

                    logger.error(
                        "Task rejected | "
                        "execution_id=%s | "
                        "task_id=%s | "
                        "error=%s",
                        execution_id,
                        task_id,
                        error,
                    )

                    continue

                # =================================================
                # Dependency validation
                # =================================================

                try:
                    dependencies_satisfied = (
                        state.dependencies_satisfied(
                            task_id
                        )
                    )

                except Exception as exc:
                    logger.exception(
                        "Dependency validation failed | "
                        "execution_id=%s | "
                        "task_id=%s",
                        execution_id,
                        task_id,
                    )

                    result = self._failure_result(
                        task_id=task_id,
                        execution_id=execution_id,
                        trace_id=trace_id,
                        error=(
                            "Dependency validation failed: "
                            f"{exc}"
                        ),
                        metadata={
                            "failure_type": (
                                "dependency_validation_error"
                            ),
                            "exception_type": (
                                type(exc).__name__
                            ),
                        },
                    )

                    state.mark_failed(
                        task_id,
                        result,
                    )

                    task_results[
                        task_id
                    ] = result

                    continue

                if not dependencies_satisfied:
                    error = (
                        f"Dependencies not satisfied "
                        f"for task '{task_id}'."
                    )

                    result = self._failure_result(
                        task_id=task_id,
                        execution_id=execution_id,
                        trace_id=trace_id,
                        error=error,
                        metadata={
                            "failure_type": (
                                "dependency_failure"
                            )
                        },
                    )

                    state.mark_failed(
                        task_id,
                        result,
                    )

                    task_results[
                        task_id
                    ] = result

                    logger.error(
                        "Task dependency failure | "
                        "execution_id=%s | "
                        "research_id=%s | "
                        "task_id=%s",
                        execution_id,
                        research_id,
                        task_id,
                    )

                    continue

                # =================================================
                # CRITICAL CONTEXT IDENTITY CHECK
                # =================================================

                if id(agent_context) != original_context_id:
                    raise RuntimeError(
                        "AgentContext identity changed "
                        "inside ExecutionEngine."
                    )

                # =================================================
                # Dispatch
                # =================================================

                logger.info(
                    "Dispatching task | "
                    "execution_id=%s | "
                    "trace_id=%s | "
                    "research_id=%s | "
                    "task_id=%s | "
                    "agent_name=%s | "
                    "context_object_id=%s",
                    execution_id,
                    trace_id,
                    research_id,
                    task_id,
                    agent_name,
                    original_context_id,
                )

                try:

                    # ---------------------------------------------
                    # CRITICAL BOUNDARY
                    #
                    # EXACT SAME AgentContext object.
                    # ---------------------------------------------

                    output = await self.dispatcher.dispatch(
                        task=task,
                        context=agent_context,
                    )

                    # =================================================
                    # Verify context identity AFTER dispatch
                    # =================================================

                    if id(agent_context) != original_context_id:
                        raise RuntimeError(
                            "AgentContext identity changed "
                            "during Dispatcher execution."
                        )

                    # =================================================
                    # Normalize Dispatcher output
                    # =================================================

                    result = (
                        self._normalize_dispatch_result(
                            task=task,
                            output=output,
                            execution_id=execution_id,
                            trace_id=trace_id,
                        )
                    )

                    # =================================================
                    # State update
                    # =================================================

                    if result.success:

                        state.mark_completed(
                            task_id,
                            result,
                        )

                        logger.info(
                            "Task completed | "
                            "execution_id=%s | "
                            "research_id=%s | "
                            "task_id=%s | "
                            "agent_name=%s | "
                            "context_object_id=%s",
                            execution_id,
                            research_id,
                            task_id,
                            agent_name,
                            original_context_id,
                        )

                    else:

                        state.mark_failed(
                            task_id,
                            result,
                        )

                        logger.error(
                            "Task returned failure | "
                            "execution_id=%s | "
                            "research_id=%s | "
                            "task_id=%s | "
                            "agent_name=%s | "
                            "error=%s",
                            execution_id,
                            research_id,
                            task_id,
                            agent_name,
                            result.error,
                        )

                    # =================================================
                    # Preserve canonical TaskResult
                    # =================================================

                    task_results[
                        task_id
                    ] = result

                    # =================================================
                    # Metrics
                    # =================================================

                    tokens, cost = (
                        self._extract_metrics(
                            result
                        )
                    )

                    total_tokens += tokens
                    total_cost += cost

                except Exception as exc:

                    logger.exception(
                        "Task execution failed | "
                        "execution_id=%s | "
                        "research_id=%s | "
                        "task_id=%s | "
                        "agent_name=%s | "
                        "context_object_id=%s",
                        execution_id,
                        research_id,
                        task_id,
                        agent_name,
                        original_context_id,
                    )

                    result = self._failure_result(
                        task_id=task_id,
                        execution_id=execution_id,
                        trace_id=trace_id,
                        error=str(exc),
                        metadata={
                            "exception_type": (
                                type(exc).__name__
                            ),
                            "agent_name": agent_name,
                        },
                    )

                    state.mark_failed(
                        task_id,
                        result,
                    )

                    task_results[
                        task_id
                    ] = result

        # =====================================================
        # Execution statistics
        # =====================================================

        duration = (
            time.perf_counter()
            - started
        )

        completed_tasks = sum(
            1
            for result in task_results.values()
            if result.success
        )

        failed_tasks = sum(
            1
            for result in task_results.values()
            if not result.success
        )

        # Use actual scheduled task count where possible.
        #
        # execution_order may contain identifiers that differ
        # from the scheduler's actual output.
        total_tasks = (
            scheduled_task_count
            if scheduled_task_count > 0
            else len(execution_order)
        )

        # If there are no tasks at all, an empty execution is
        # considered successful.
        if total_tasks == 0:
            success = True
        else:
            success = (
                failed_tasks == 0
                and completed_tasks == total_tasks
            )

        # =====================================================
        # Collect failures
        # =====================================================

        failures: list[
            dict[str, Any]
        ] = []

        for task_id, result in (
            task_results.items()
        ):

            if result.success:
                continue

            failures.append(
                {
                    "task_id": task_id,
                    "error": result.error,
                    "execution_id": getattr(
                        result,
                        "execution_id",
                        None,
                    ),
                    "trace_id": getattr(
                        result,
                        "trace_id",
                        None,
                    ),
                    "metadata": dict(
                        getattr(
                            result,
                            "metadata",
                            {},
                        )
                        or {}
                    ),
                }
            )

        # =====================================================
        # Final context identity check
        # =====================================================

        if id(agent_context) != original_context_id:
            raise RuntimeError(
                "AgentContext identity changed "
                "before execution completion."
            )

        # =====================================================
        # Final context mutation
        #
        # SAME OBJECT.
        # =====================================================

        agent_context.clear_task()

        agent_context.set_current_agent(
            None
        )

        agent_context.set_metadata(
            "execution_completed",
            True,
        )

        agent_context.set_metadata(
            "execution_success",
            success,
        )

        agent_context.set_metadata(
            "execution_duration_seconds",
            round(
                duration,
                2,
            ),
        )

        agent_context.set_metadata(
            "completed_tasks",
            completed_tasks,
        )

        agent_context.set_metadata(
            "failed_tasks",
            failed_tasks,
        )

        agent_context.set_metadata(
            "total_tasks",
            total_tasks,
        )

        # =====================================================
        # Final logging
        # =====================================================

        logger.info(
            "Execution finished | "
            "execution_id=%s | "
            "trace_id=%s | "
            "research_id=%s | "
            "company_id=%r | "
            "success=%s | "
            "completed=%d | "
            "failed=%d | "
            "total=%d | "
            "duration=%.2fs | "
            "total_tokens=%d | "
            "estimated_cost=%s | "
            "context_object_id=%s",
            execution_id,
            trace_id,
            research_id,
            getattr(
                agent_context,
                "company_id",
                None,
            ),
            success,
            completed_tasks,
            failed_tasks,
            total_tasks,
            duration,
            total_tokens,
            total_cost,
            original_context_id,
        )

        # =====================================================
        # Final ExecutionResult
        # =====================================================

        return ExecutionResult(
            success=success,
            task_results=task_results,
            metadata={
                "execution_id": execution_id,
                "trace_id": trace_id,
                "research_id": research_id,
                "company_id": getattr(
                    agent_context,
                    "company_id",
                    None,
                ),
                "execution_order": execution_order,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "executed_tasks": len(
                    task_results
                ),
                "total_tasks": total_tasks,
                "duration_seconds": round(
                    duration,
                    2,
                ),
                "total_tokens": total_tokens,
                "estimated_cost": total_cost,
                "failures": failures,
                "context_object_id": (
                    original_context_id
                ),
            },
        )

    # =========================================================
    # Context Logging
    # =========================================================

    @staticmethod
    def _log_context_checkpoint(
        context: AgentContext,
        *,
        execution_id: str,
        trace_id: str,
    ) -> None:
        """
        Log the canonical AgentContext at the execution boundary.
        """

        logger.info(
            "=================================================="
        )

        logger.info(
            "EXECUTION ENGINE CONTEXT CHECKPOINT"
        )

        logger.info(
            "context_object_id=%s",
            id(context),
        )

        logger.info(
            "context_type=%s",
            type(context).__name__,
        )

        logger.info(
            "research_id=%r",
            context.research_id,
        )

        logger.info(
            "company_id=%r",
            getattr(
                context,
                "company_id",
                None,
            ),
        )

        logger.info(
            "company=%r",
            getattr(
                context,
                "company",
                None,
            ),
        )

        logger.info(
            "ticker=%r",
            getattr(
                context,
                "ticker",
                None,
            ),
        )

        logger.info(
            "industry=%r",
            getattr(
                context,
                "industry",
                None,
            ),
        )

        logger.info(
            "execution_id=%s",
            execution_id,
        )

        logger.info(
            "trace_id=%s",
            trace_id,
        )

        logger.info(
            "services_object_id=%s",
            (
                id(context.services)
                if getattr(
                    context,
                    "services",
                    None,
                ) is not None
                else None
            ),
        )

        logger.info(
            "=================================================="
        )

    # =========================================================
    # Failure Result
    # =========================================================

    @staticmethod
    def _failure_result(
        *,
        task_id: str,
        execution_id: str,
        trace_id: str,
        error: str,
        metadata: dict[str, Any] | None = None,
    ) -> TaskResult:
        """
        Create canonical execution-layer TaskResult
        for failures originating inside ExecutionEngine.
        """

        return TaskResult(
            task_id=task_id,
            success=False,
            execution_id=execution_id,
            trace_id=trace_id,
            output=None,
            error=error,
            metadata=(
                dict(metadata)
                if metadata is not None
                else {}
            ),
        )

    # =========================================================
    # Result Normalization
    # =========================================================

    @staticmethod
    def _normalize_dispatch_result(
        *,
        task: Any,
        output: Any,
        execution_id: str,
        trace_id: str,
    ) -> TaskResult:
        """
        Normalize Dispatcher output.

        Canonical contract:

            Dispatcher -> TaskResult

        The current Worker already guarantees this.

        AgentResult/dict/raw output are retained only as
        backward compatibility for older execution paths.

        IMPORTANT:

        If Dispatcher already returns TaskResult, it is returned
        unchanged. ExecutionEngine does NOT reconstruct it.
        """

        task_id = str(
            getattr(
                task,
                "id",
                "",
            )
        )

        if not task_id:
            raise ValueError(
                "Cannot normalize execution result "
                "for Task without id."
            )

        # =====================================================
        # Canonical TaskResult
        # =====================================================

        if isinstance(
            output,
            TaskResult,
        ):
            return output

        # =====================================================
        # Legacy AgentResult
        #
        # This path should eventually be removed.
        # Worker is now responsible for AgentResult -> TaskResult.
        # =====================================================

        if isinstance(
            output,
            AgentResult,
        ):
            metadata = dict(
                getattr(
                    output,
                    "metadata",
                    None,
                )
                or {}
            )

            status = getattr(
                output,
                "status",
                None,
            )

            status_value = (
                status.value
                if hasattr(
                    status,
                    "value",
                )
                else (
                    str(status)
                    if status is not None
                    else None
                )
            )

            metadata.update(
                {
                    "agent_name": getattr(
                        output,
                        "agent_name",
                        None,
                    ),
                    "agent_status": status_value,
                    "confidence": getattr(
                        output,
                        "confidence",
                        None,
                    ),
                    "sources": getattr(
                        output,
                        "sources",
                        [],
                    ),
                    "reasoning": getattr(
                        output,
                        "reasoning",
                        None,
                    ),
                    "execution_time": getattr(
                        output,
                        "execution_time",
                        None,
                    ),
                    "legacy_agent_result": True,
                }
            )

            succeeded = getattr(
                output,
                "succeeded",
                None,
            )

            if succeeded is None:
                succeeded = getattr(
                    output,
                    "success",
                    None,
                )

            if succeeded is None:
                succeeded = (
                    getattr(
                        output,
                        "error",
                        None,
                    )
                    is None
                )

            return TaskResult(
                task_id=task_id,
                success=bool(
                    succeeded
                ),
                execution_id=(
                    execution_id
                ),
                trace_id=trace_id,
                output=getattr(
                    output,
                    "data",
                    None,
                ),
                error=getattr(
                    output,
                    "error",
                    None,
                ),
                metadata=metadata,
            )

        # =====================================================
        # Legacy dictionary
        # =====================================================

        if isinstance(
            output,
            dict,
        ):
            success = bool(
                output.get(
                    "success",
                    True,
                )
            )

            metadata = output.get(
                "metadata"
            )

            if not isinstance(
                metadata,
                dict,
            ):
                metadata = {}

            metadata = dict(
                metadata
            )

            metadata.setdefault(
                "execution_id",
                execution_id,
            )

            metadata.setdefault(
                "trace_id",
                trace_id,
            )

            metadata.setdefault(
                "legacy_output",
                True,
            )

            return TaskResult(
                task_id=task_id,
                success=success,
                execution_id=execution_id,
                trace_id=trace_id,
                output=output,
                error=(
                    output.get(
                        "error"
                    )
                    if not success
                    else None
                ),
                metadata=metadata,
            )

        # =====================================================
        # Legacy raw output
        # =====================================================

        return TaskResult(
            task_id=task_id,
            success=True,
            execution_id=execution_id,
            trace_id=trace_id,
            output=output,
            error=None,
            metadata={
                "legacy_output": True,
            },
        )

    # =========================================================
    # Metrics
    # =========================================================

    @staticmethod
    def _extract_metrics(
        output: Any,
    ) -> tuple[int, float]:
        """
        Extract generic token/cost metrics.

        ExecutionEngine performs only generic execution-level
        aggregation.
        """

        metadata: Any = None

        if isinstance(
            output,
            TaskResult,
        ):
            metadata = output.metadata

        elif isinstance(
            output,
            AgentResult,
        ):
            metadata = output.metadata

        elif isinstance(
            output,
            dict,
        ):
            metadata = output.get(
                "metadata"
            )

        if not isinstance(
            metadata,
            dict,
        ):
            return 0, 0.0

        tokens = metadata.get(
            "total_tokens",
            metadata.get(
                "tokens",
                0,
            ),
        )

        cost = metadata.get(
            "cost",
            metadata.get(
                "estimated_cost",
                0.0,
            ),
        )

        try:
            tokens = int(
                tokens or 0
            )

        except (
            TypeError,
            ValueError,
        ):
            tokens = 0

        try:
            cost = float(
                cost or 0.0
            )

        except (
            TypeError,
            ValueError,
        ):
            cost = 0.0

        return tokens, cost