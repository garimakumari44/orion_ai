"""
app/agents/base/base_agent.py

Base Agent
==========

Universal runtime contract for every specialized agent in the
Multi-Agent Equity Research System.

Architecture
------------

    ExecutionEngine
          |
          v
    AgentContext
          |
          v
        Worker
          |
          v
     AgentManager
          |
          v
      BaseAgent
          |
          +── AgentServices
          |      |
          |      +── LLM
          |      +── Retrieval
          |      +── Knowledge
          |      +── Memory
          |      +── Tools
          |      +── MCP
          |      +── Orchestration
          |      +── Observability
          |      +── Domain Services
          |
          v
    Specialized Agent


Design Principles
-----------------

1. AgentServices is the canonical dependency container.

2. BaseAgent does not construct shared infrastructure.

3. BaseAgent does not reconstruct AgentContext.

4. ExecutionEngine creates the canonical AgentContext.

5. Worker / AgentManager propagate that context to the agent.

6. Specialized agents implement only:

       async def run(
           self,
           context: AgentContext,
       ) -> AgentResult:

7. Agents access infrastructure through canonical services:

       self.services.llm
       self.services.retrieval
       self.services.knowledge
       self.services.memory
       self.services.tools
       self.services.mcp
       self.services.orchestration
       self.services.company_research
       self.services.observability

8. Convenience references may exist for readability, but they
   MUST point to the canonical AgentServices capabilities.

9. Agent memory is NOT constructed separately per BaseAgent.
   AgentServices.memory is the canonical memory capability.

10. Generic lifecycle management, validation, result normalization,
    error handling, and observability belong here.

11. Task is NOT passed directly to specialized agents.

12. Canonical task information comes from AgentContext:

       context.task_id
       context.task_type
       context.assigned_executor

13. AgentContext.services MUST be the exact same AgentServices
    instance injected into the BaseAgent.

14. Specialized agents should not duplicate generic execution
    try/except handling.

15. Cleanup is part of the universal lifecycle and must not mask
    the original execution result or exception.
"""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import (
    AgentResult,
    AgentStatus,
)
from app.agents.base.agent_services import AgentServices
from app.agents.base.agent_state import AgentState
from app.agents.base.agent_tools import AgentTools


class BaseAgent(ABC):
    """
    Abstract runtime contract for every specialized agent.

    BaseAgent owns:

        - dependency injection
        - lifecycle state
        - context validation
        - service ownership validation
        - task validation
        - execution wrapping
        - result validation
        - result normalization
        - centralized error handling
        - observability integration
        - cleanup lifecycle

    Specialized agents own only domain-specific behavior
    through ``run(context)``.
    """

    # =========================================================
    # Metadata Defaults
    # =========================================================

    agent_id: str = "base_agent"

    category: str = "research"

    display_name: str = "Base Agent"

    description: str = "Abstract base agent."

    capabilities: list[str] = []

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        services: AgentServices,
    ) -> None:
        """
        Initialize the agent with the shared AgentServices
        container.

        BaseAgent never creates shared infrastructure itself.
        """

        if services is None:
            raise ValueError(
                "AgentServices is required."
            )

        if not isinstance(
            services,
            AgentServices,
        ):
            raise TypeError(
                "services must be an AgentServices instance."
            )

        # =====================================================
        # Canonical Dependency Container
        # =====================================================

        self.services = services

        # =====================================================
        # Convenience References
        #
        # These MUST point to canonical AgentServices
        # capabilities.
        #
        # They MUST NOT construct new infrastructure.
        # =====================================================

        self.llm = services.llm

        self.knowledge = services.knowledge

        self.retrieval = services.retrieval

        self.shared_memory = services.memory

        self.tools = services.tools

        self.mcp = services.mcp

        self.orchestration = services.orchestration

        self.company_research = (
            services.company_research
        )

        self.observability = (
            services.observability
        )

        self.logger = services.logger

        self.metrics = services.metrics

        self.cache = services.cache

        # =====================================================
        # Agent-local Helper
        #
        # AgentTools is allowed only as a lightweight helper.
        #
        # Canonical tool infrastructure remains:
        #
        #     services.tools
        #
        # AgentTools MUST NOT create a second ToolRouter,
        # ToolRegistry, or independent tool infrastructure.
        # =====================================================

        self.agent_tools = AgentTools()

        # =====================================================
        # Lifecycle
        # =====================================================

        self.state = AgentState.CREATED

    # =========================================================
    # Lifecycle
    # =========================================================

    async def initialize(self) -> None:
        """
        Initialize the agent.

        Shared infrastructure is already injected through
        AgentServices.

        Specialized agents may override this method when
        they require additional initialization.

        Initialization should NOT create replacement shared
        infrastructure.
        """

        self.state = AgentState.INITIALIZING

    async def cleanup(self) -> None:
        """
        Cleanup hook executed after agent execution.

        Cleanup failures are intentionally isolated from the
        execution result.

        Specialized agents may override this method for
        agent-specific cleanup, but should not destroy shared
        infrastructure owned by AgentServices.
        """

        return None

    # =========================================================
    # Generic Execution Boundary
    # =========================================================

    async def execute(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Execute the agent against the canonical AgentContext.

        This is the universal execution boundary.

        Lifecycle:

            1. validate AgentContext
            2. validate AgentServices ownership
            3. establish current agent
            4. initialize agent
            5. validate task
            6. execute specialized run(context)
            7. validate AgentResult
            8. normalize result metadata
            9. update lifecycle state
           10. register result in context
           11. record observability
           12. cleanup
           13. return AgentResult

        Unexpected execution failures are normalized into
        AgentResult.failure(...).

        Specialized agents should implement only run(context).
        """

        # =====================================================
        # Validate Context BEFORE entering execution boundary
        # =====================================================

        self._validate_context(context)

        try:
            # =================================================
            # Establish Current Agent
            # =================================================

            context.set_current_agent(
                self.agent_id
            )

            # =================================================
            # Validate Canonical Services
            # =================================================

            self._validate_services(context)

            # =================================================
            # Initialize
            # =================================================

            await self.initialize()

            # =================================================
            # Validate Task
            # =================================================

            if not await self.validate_task(
                context
            ):
                raise ValueError(
                    f"Task validation failed "
                    f"for agent '{self.agent_id}'."
                )

            # =================================================
            # Enter Running State
            # =================================================

            self.state = AgentState.RUNNING

            # =================================================
            # Execute Specialized Agent Logic
            # =================================================

            result = await self.run(
                context
            )

            # =================================================
            # Validate Result Contract
            # =================================================

            self._validate_result(
                result
            )

            # =================================================
            # Normalize Result Metadata
            # =================================================

            self._normalize_result(
                context,
                result,
            )

            # =================================================
            # Update Lifecycle State
            # =================================================

            self._update_state_from_result(
                result
            )

            # =================================================
            # Register Result With Context
            # =================================================

            context.add_result(
                result
            )

            # =================================================
            # Observability
            # =================================================

            await self._record_execution_success(
                context,
                result,
            )

            return result

        except Exception as exc:
            # =================================================
            # Centralized Failure Handling
            # =================================================

            return self._handle_execution_error(
                context=context,
                exc=exc,
            )

        finally:
            # =================================================
            # Cleanup
            #
            # Cleanup MUST NOT replace the original result or
            # exception.
            # =================================================

            await self._safe_cleanup()

    # =========================================================
    # Specialized Agent Contract
    # =========================================================

    @abstractmethod
    async def run(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Execute specialized agent logic.

        AgentContext is the ONLY runtime input.

        Specialized agents MUST NOT:

            - construct AgentContext
            - construct AgentServices
            - construct shared infrastructure
            - receive Task directly
            - duplicate generic execution handling
            - duplicate generic error normalization

        Specialized agents SHOULD consume dependencies through:

            self.services.<capability>

        and return:

            AgentResult
        """

        raise NotImplementedError

    # =========================================================
    # Context Validation
    # =========================================================

    def _validate_context(
        self,
        context: AgentContext,
    ) -> None:
        """
        Validate the canonical runtime context.
        """

        if context is None:
            raise ValueError(
                "AgentContext is required."
            )

        if not isinstance(
            context,
            AgentContext,
        ):
            raise TypeError(
                "context must be an AgentContext instance."
            )

    # =========================================================
    # Services Validation
    # =========================================================

    def _validate_services(
        self,
        context: AgentContext,
    ) -> None:
        """
        Ensure AgentContext uses the SAME AgentServices
        instance injected into this agent.

        AgentServices is a shared dependency container and
        should never be silently replaced inside BaseAgent.
        """

        context_services = getattr(
            context,
            "services",
            None,
        )

        if context_services is None:
            raise RuntimeError(
                "AgentContext.services is required. "
                "The execution layer must propagate the "
                "canonical AgentServices instance."
            )

        if context_services is not self.services:
            raise RuntimeError(
                "AgentContext.services does not match "
                "the AgentServices instance injected "
                "into BaseAgent."
            )

    # =========================================================
    # Task Validation
    # =========================================================

    async def validate_task(
        self,
        context: AgentContext,
    ) -> bool:
        """
        Validate canonical task information stored in
        AgentContext.

        Specialized agents NEVER receive Task directly.

        Canonical task fields are:

            context.task_id
            context.task_type
            context.assigned_executor

        Specialized agents may override this method to add
        domain-specific validation.
        """

        # -----------------------------------------------------
        # Task identity is required
        # -----------------------------------------------------

        if not context.task_id:
            return False

        # -----------------------------------------------------
        # Task classification is required
        # -----------------------------------------------------

        if not context.task_type:
            return False

        # -----------------------------------------------------
        # Validate executor routing when supplied
        # -----------------------------------------------------

        assigned_executor = (
            context.assigned_executor
        )

        if (
            assigned_executor
            and assigned_executor != self.agent_id
        ):
            return False

        return True

    # =========================================================
    # Result Validation
    # =========================================================

    def _validate_result(
        self,
        result: Any,
    ) -> None:
        """
        Validate the specialized agent result.
        """

        if not isinstance(
            result,
            AgentResult,
        ):
            raise TypeError(
                f"Agent '{self.agent_id}' returned "
                f"{type(result).__name__}; "
                "expected AgentResult."
            )

    # =========================================================
    # Result Normalization
    # =========================================================

    def _normalize_result(
        self,
        context: AgentContext,
        result: AgentResult,
    ) -> None:
        """
        Normalize canonical metadata onto the result.

        Specialized agents should not need to repeatedly
        populate infrastructure-owned metadata such as:

            agent_name
            task_id
        """

        if not result.agent_name:
            result.agent_name = self.agent_id

        if not result.task_id:
            result.task_id = (
                context.task_id
            )

    # =========================================================
    # State Management
    # =========================================================

    def _update_state_from_result(
        self,
        result: AgentResult,
    ) -> None:
        """
        Convert AgentResult status into agent lifecycle state.
        """

        if result.status == AgentStatus.COMPLETED:
            self.state = AgentState.COMPLETED

        elif result.status == AgentStatus.FAILED:
            self.state = AgentState.FAILED

        else:
            # Unknown/intermediate statuses are treated as
            # completed at this generic boundary unless a
            # specialized lifecycle implementation says
            # otherwise.
            self.state = AgentState.COMPLETED

    # =========================================================
    # Successful Execution Observability
    # =========================================================

    async def _record_execution_success(
        self,
        context: AgentContext,
        result: AgentResult,
    ) -> None:
        """
        Record successful execution through the canonical
        observability capability when available.

        Both synchronous and asynchronous implementations
        are supported.

        Observability failures MUST never cause an otherwise
        successful agent execution to fail.
        """

        try:
            observability = (
                self.services.observability
            )

            if observability is None:
                return

            record = getattr(
                observability,
                "record_agent_execution",
                None,
            )

            if record is None:
                return

            payload = {
                "agent": self.agent_id,
                "task_id": context.task_id,
                "research_id": context.research_id,
                "status": str(
                    result.status
                ),
            }

            value = record(
                payload
            )

            if inspect.isawaitable(
                value
            ):
                await value

        except Exception:
            # Observability must never break agent execution.
            return

    # =========================================================
    # Error Handling
    # =========================================================

    def _handle_execution_error(
        self,
        context: AgentContext,
        exc: Exception,
    ) -> AgentResult:
        """
        Centralized generic execution error handling.

        Specialized agents should not need their own generic
        try/except blocks around run(context).
        """

        self.state = AgentState.FAILED

        task_id = str(
            context.task_id
            or ""
        )

        result = AgentResult.failure(
            agent_name=self.agent_id,
            task_id=task_id,
            error=(
                f"Agent '{self.agent_id}' failed: "
                f"{exc}"
            ),
        )

        # -----------------------------------------------------
        # Register failure in canonical context
        # -----------------------------------------------------

        try:
            context.add_result(
                result
            )
        except Exception:
            # Result registration must never mask the original
            # execution failure.
            pass

        # -----------------------------------------------------
        # Log failure
        # -----------------------------------------------------

        try:
            logger = self.logger

            if logger is not None:
                logger.exception(
                    "Agent execution failed | "
                    "agent=%s | task_id=%s | research_id=%s",
                    self.agent_id,
                    context.task_id,
                    context.research_id,
                    exc_info=exc,
                )

        except Exception:
            # Logging must never mask the original failure.
            pass

        return result

    # =========================================================
    # Safe Cleanup
    # =========================================================

    async def _safe_cleanup(
        self,
    ) -> None:
        """
        Execute cleanup while isolating cleanup failures.

        Cleanup belongs to the agent lifecycle but MUST NOT
        overwrite the actual execution result.

        If cleanup itself fails, the failure is logged and the
        lifecycle state is preserved as-is.
        """

        try:
            await self.cleanup()

        except Exception as exc:
            try:
                logger = self.logger

                if logger is not None:
                    logger.exception(
                        "Agent cleanup failed | "
                        "agent=%s | error=%s",
                        self.agent_id,
                        exc,
                        exc_info=exc,
                    )

            except Exception:
                # Cleanup logging must never propagate.
                pass

    # =========================================================
    # Representation
    # =========================================================

    def __repr__(self) -> str:
        """
        Provide a useful debugging representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"agent_id={self.agent_id!r}, "
            f"state={self.state!r}"
            ")"
        )