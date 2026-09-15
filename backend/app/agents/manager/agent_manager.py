
"""
app/agents/manager/agent_manager.py

Agent Manager

Central runtime manager for all registered agents.

Canonical execution architecture:

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
       /      \
      v        v
AgentRegistry AgentServices
      |
      v
  BaseAgent
      |
      v
Specialized Agent

IMPORTANT CONTEXT RULE
----------------------

ExecutionEngine creates exactly ONE AgentContext for an execution.

That SAME object must travel through:

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
          v
Specialized Agent

AgentManager MUST NEVER create or reconstruct AgentContext.

AgentManager only:

- receives the existing AgentContext
- validates it
- enriches runtime state
- forwards the same object
- stores results on that same object

OWNERSHIP
---------

ExecutionEngine
    -> owns AgentContext lifecycle

ResearchService
    -> owns research lifecycle/state

Worker
    -> owns task execution boundary
    -> attaches task/execution metadata to AgentContext

AgentManager
    -> resolves agents
    -> injects AgentServices
    -> validates context
    -> executes agent lifecycle
    -> propagates canonical AgentContext

BaseAgent
    -> owns common agent lifecycle

Specialized Agent
    -> implements domain-specific execute logic
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional, Type

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_services import AgentServices
from app.agents.base.base_agent import BaseAgent
from app.agents.base.registry import AgentRegistry

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Central runtime manager for registered agents.

    Responsibilities
    ----------------
    - Register agents
    - Resolve agents
    - Construct agents
    - Inject shared AgentServices
    - Validate AgentContext
    - Execute agent lifecycle
    - Propagate canonical AgentContext
    - Validate AgentResult
    - Expose agent metadata

    AgentManager does NOT:

    - Create AgentContext
    - Reconstruct AgentContext
    - Convert AgentContext to dictionaries
    - Create research records
    - Own research lifecycle
    - Build execution plans
    - Decide research strategy
    - Construct individual services
    - Build agent-specific task dictionaries
    """

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        services: AgentServices,
        registry: Optional[AgentRegistry] = None,
    ) -> None:
        """
        Initialize AgentManager.

        Parameters
        ----------
        services:
            Application-level shared AgentServices.

        registry:
            Application-level AgentRegistry.

            The application should normally provide the
            populated canonical registry during startup.
        """

        if services is None:
            raise ValueError(
                "AgentServices is required."
            )

        if not isinstance(services, AgentServices):
            raise TypeError(
                "services must be an AgentServices instance, "
                f"got {type(services).__name__}."
            )

        self.services = services

        # Explicit None check is intentional.
        #
        # Do NOT use:
        #
        #     registry or AgentRegistry()
        #
        # because a valid registry may implement false-y
        # truthiness.

        self.registry = (
            registry
            if registry is not None
            else AgentRegistry()
        )

        logger.info(
            "AgentManager initialized | "
            "registry=%s | "
            "services=%s | "
            "registry_id=%s | "
            "services_id=%s",
            type(self.registry).__name__,
            type(self.services).__name__,
            id(self.registry),
            id(self.services),
        )

    # =========================================================
    # Context Validation
    # =========================================================

    @staticmethod
    def _require_context(
        context: AgentContext | None,
    ) -> AgentContext:
        """
        Validate the canonical AgentContext.

        IMPORTANT:

        This method NEVER creates a context.

        ExecutionEngine owns context creation.

        AgentManager only validates that the object supplied
        by the execution layer is the expected AgentContext.
        """

        if context is None:
            raise ValueError(
                "AgentManager requires an AgentContext. "
                "ExecutionEngine must create the shared "
                "AgentContext before execution."
            )

        if not isinstance(context, AgentContext):
            raise TypeError(
                "AgentManager requires an AgentContext "
                f"instance, got {type(context).__name__}."
            )

        return context

    # =========================================================
    # Registration
    # =========================================================

    def register(
        self,
        name: str,
        agent_class: Type[BaseAgent],
        *,
        category: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[list[str]] = None,
        dependencies: Optional[list[str]] = None,
        enabled: bool = True,
    ) -> None:
        """
        Register an agent with AgentRegistry.
        """

        if not isinstance(name, str):
            raise TypeError(
                "Agent name must be a string, "
                f"got {type(name).__name__}."
            )

        name = name.strip()

        if not name:
            raise ValueError(
                "Agent name cannot be empty."
            )

        if not isinstance(agent_class, type):
            raise TypeError(
                "agent_class must be a class, "
                f"got {type(agent_class).__name__}."
            )

        if not issubclass(agent_class, BaseAgent):
            raise TypeError(
                f"{agent_class.__name__} must inherit "
                "from BaseAgent."
            )

        if self.registry.exists(name):
            raise ValueError(
                f"Agent '{name}' is already registered."
            )

        resolved_category = (
            category
            if category is not None
            else getattr(
                agent_class,
                "category",
                "general",
            )
        )

        resolved_display_name = (
            display_name
            if display_name is not None
            else getattr(
                agent_class,
                "display_name",
                getattr(
                    agent_class,
                    "name",
                    name,
                ),
            )
        )

        resolved_description = (
            description
            if description is not None
            else getattr(
                agent_class,
                "description",
                "",
            )
        )

        resolved_capabilities = (
            list(capabilities)
            if capabilities is not None
            else list(
                getattr(
                    agent_class,
                    "capabilities",
                    [],
                )
            )
        )

        resolved_dependencies = (
            list(dependencies)
            if dependencies is not None
            else list(
                getattr(
                    agent_class,
                    "dependencies",
                    [],
                )
            )
        )

        self.registry.register(
            agent_name=name,
            agent_class=agent_class,
            category=resolved_category,
            display_name=resolved_display_name,
            description=resolved_description,
            capabilities=resolved_capabilities,
            dependencies=resolved_dependencies,
            enabled=enabled,
        )

        logger.info(
            "Registered agent | "
            "agent_name=%s | "
            "class=%s | "
            "category=%s | "
            "capabilities=%s | "
            "enabled=%s",
            name,
            agent_class.__name__,
            resolved_category,
            resolved_capabilities,
            enabled,
        )

    # =========================================================
    # Register Many
    # =========================================================

    def register_many(
        self,
        agents: Dict[str, Type[BaseAgent]],
    ) -> None:
        """
        Register multiple agents.
        """

        if agents is None:
            return

        if not isinstance(agents, dict):
            raise TypeError(
                "agents must be a dictionary mapping "
                "agent names to agent classes."
            )

        for name, agent_class in agents.items():
            self.register(
                name,
                agent_class,
            )

    # =========================================================
    # Lookup
    # =========================================================

    def has_agent(
        self,
        name: str,
    ) -> bool:
        """Return True if an agent is registered."""

        if not isinstance(name, str):
            return False

        return self.registry.exists(name.strip())

    # =========================================================

    def get_agent_class(
        self,
        name: str,
    ) -> Type[BaseAgent]:
        """Resolve an agent class from the registry."""

        if not isinstance(name, str):
            raise TypeError(
                "Agent name must be a string."
            )

        name = name.strip()

        if not name:
            raise ValueError(
                "Agent name cannot be empty."
            )

        if not self.registry.exists(name):
            raise ValueError(
                f"Agent '{name}' is not registered."
            )

        agent_class = self.registry.get_class(name)

        if not isinstance(agent_class, type):
            raise TypeError(
                f"Registry returned invalid class for "
                f"agent '{name}'."
            )

        if not issubclass(agent_class, BaseAgent):
            raise TypeError(
                f"Registered agent '{name}' does not "
                "inherit from BaseAgent."
            )

        return agent_class

    # =========================================================
    # Agent Construction
    # =========================================================

    def get_agent(
        self,
        name: str,
        **kwargs: Any,
    ) -> BaseAgent:
        """
        Construct a registered agent.

        AgentManager owns injection of the canonical
        AgentServices instance.

        Specialized agents may receive additional constructor
        arguments, but they cannot override AgentServices.
        """

        agent_class = self.get_agent_class(name)

        if "services" in kwargs:
            raise TypeError(
                "The 'services' constructor argument is owned "
                "by AgentManager and cannot be overridden."
            )

        constructor_kwargs: Dict[str, Any] = {
            "services": self.services,
            **kwargs,
        }

        try:
            agent = agent_class(**constructor_kwargs)

        except TypeError as exc:
            logger.exception(
                "Failed to initialize agent | "
                "agent=%s | "
                "class=%s",
                name,
                agent_class.__name__,
            )

            raise TypeError(
                f"Could not initialize agent "
                f"'{name}': {exc}"
            ) from exc

        if not isinstance(agent, BaseAgent):
            raise TypeError(
                f"Agent '{name}' did not produce "
                "a BaseAgent instance."
            )

        if getattr(agent, "services", None) is not self.services:
            raise RuntimeError(
                f"Agent '{name}' was not initialized "
                "with the canonical AgentServices instance."
            )

        logger.debug(
            "Agent constructed | "
            "agent=%s | "
            "class=%s | "
            "services_id=%s",
            name,
            agent_class.__name__,
            id(self.services),
        )

        return agent

    # =========================================================
    # Agent Validation
    # =========================================================

    async def validate_agent(
        self,
        agent: BaseAgent,
        context: AgentContext,
    ) -> bool:
        """
        Validate whether an agent can execute the supplied
        canonical AgentContext.
        """

        if not isinstance(agent, BaseAgent):
            raise TypeError(
                "agent must be a BaseAgent instance."
            )

        context = self._require_context(context)

        try:
            return bool(
                await agent.validate_task(context)
            )

        except Exception:
            logger.exception(
                "Agent validation failed | "
                "agent=%s | "
                "task_id=%r | "
                "context_id=%s",
                getattr(
                    agent,
                    "agent_id",
                    "unknown",
                ),
                getattr(
                    context,
                    "task_id",
                    None,
                ),
                id(context),
            )

            return False

    # =========================================================
    # Canonical Execution
    # =========================================================

    async def execute(
        self,
        agent_name: str,
        context: AgentContext,
        agent_kwargs: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """
        Execute an agent using the canonical AgentContext.

        PRIMARY RUNTIME ENTRYPOINT.

        This method NEVER:

        - creates AgentContext
        - reconstructs AgentContext
        - converts AgentContext to dict

        The exact object supplied by Worker is forwarded
        directly through the agent lifecycle.
        """

        if not isinstance(agent_name, str):
            raise TypeError(
                "agent_name must be a string."
            )

        agent_name = agent_name.strip()

        if not agent_name:
            raise ValueError(
                "agent_name is required."
            )

        context = self._require_context(context)

        resolved_agent_kwargs = (
            dict(agent_kwargs)
            if agent_kwargs is not None
            else {}
        )

        logger.info(
            "AgentManager.execute | "
            "agent=%s | "
            "context_id=%s | "
            "research_id=%r | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "industry=%r | "
            "task_id=%r",
            agent_name,
            id(context),
            context.research_id,
            getattr(
                context,
                "company_id",
                None,
            ),
            context.company,
            context.ticker,
            context.industry,
            getattr(
                context,
                "task_id",
                None,
            ),
        )

        if not self.has_agent(agent_name):
            raise ValueError(
                f"Agent '{agent_name}' is not registered."
            )

        agent = self.get_agent(
            agent_name,
            **resolved_agent_kwargs,
        )

        context.set_current_agent(agent_name)

        return await self.execute_agent(
            agent,
            context,
            agent_name=agent_name,
        )

    # =========================================================
    # Execute Existing Agent
    # =========================================================

    async def execute_agent(
        self,
        agent: BaseAgent,
        context: AgentContext,
        *,
        agent_name: Optional[str] = None,
    ) -> AgentResult:
        """
        Execute an already-instantiated BaseAgent.

        Common lifecycle:

            validate
                ↓
            initialize
                ↓
             execute
                ↓
          validate result
                ↓
           store result
                ↓
            cleanup

        No AgentContext reconstruction occurs.
        """

        if not isinstance(agent, BaseAgent):
            raise TypeError(
                "agent must be a BaseAgent instance."
            )

        context = self._require_context(context)

        resolved_agent_name = (
            agent_name
            or getattr(
                agent,
                "agent_id",
                None,
            )
            or getattr(
                agent,
                "name",
                None,
            )
            or agent.__class__.__name__
        )

        context.set_current_agent(
            resolved_agent_name
        )

        # =====================================================
        # Validate
        # =====================================================

        is_valid = await self.validate_agent(
            agent,
            context,
        )

        if not is_valid:
            raise ValueError(
                f"Agent validation failed "
                f"for '{resolved_agent_name}'."
            )

        # =====================================================
        # Initialize
        # =====================================================

        try:
            await agent.initialize()

        except Exception as exc:
            logger.exception(
                "Agent initialization failed | "
                "agent=%s | "
                "context_id=%s",
                resolved_agent_name,
                id(context),
            )

            raise RuntimeError(
                f"Agent '{resolved_agent_name}' "
                f"initialization failed: {exc}"
            ) from exc

        # =====================================================
        # Execute
        # =====================================================

        logger.info(
            "AgentManager context before execution | "
            "agent=%s | "
            "context_object_id=%s | "
            "research_id=%r | "
            "task_id=%r",
            resolved_agent_name,
            id(context),
            context.research_id,
            getattr(
                context,
                "task_id",
                None,
            ),
        )

        try:
            result = await agent.execute(
                context=context
            )

        except Exception as exc:
            logger.exception(
                "Agent execution failed | "
                "agent=%s | "
                "context_id=%s | "
                "research_id=%r | "
                "task_id=%r",
                resolved_agent_name,
                id(context),
                context.research_id,
                getattr(
                    context,
                    "task_id",
                    None,
                ),
            )

            raise RuntimeError(
                f"Agent '{resolved_agent_name}' "
                f"execution failed: {exc}"
            ) from exc

        # =====================================================
        # Validate result
        # =====================================================

        if not isinstance(result, AgentResult):
            raise TypeError(
                f"Agent '{resolved_agent_name}' returned "
                f"{type(result).__name__}; "
                "expected AgentResult."
            )

        # =====================================================
        # Store result
        # =====================================================

        context.add_result(result)

        # =====================================================
        # Cleanup
        # =====================================================

        try:
            await agent.cleanup()

        except Exception as exc:
            logger.exception(
                "Agent cleanup failed | "
                "agent=%s | "
                "context_id=%s",
                resolved_agent_name,
                id(context),
            )

            try:
                context.set_metadata(
                    "cleanup_error",
                    str(exc),
                )

            except Exception:
                logger.exception(
                    "Failed to store agent cleanup error "
                    "in AgentContext | agent=%s",
                    resolved_agent_name,
                )

        # =====================================================
        # Completed
        # =====================================================

        logger.info(
            "Agent completed | "
            "agent=%s | "
            "task_id=%r | "
            "status=%s | "
            "context_id=%s | "
            "research_id=%r",
            resolved_agent_name,
            getattr(
                context,
                "task_id",
                None,
            ),
            getattr(
                result,
                "status",
                "unknown",
            ),
            id(context),
            context.research_id,
        )

        return result

    # =========================================================
    # Agent Information
    # =========================================================

    def list_agents(
        self,
    ) -> Iterable[str]:
        """Return all registered agent names."""

        return [
            metadata.agent_id
            for metadata in self.registry.get_all()
        ]

    # =========================================================

    def get_agent_info(
        self,
        name: str,
    ) -> Dict[str, Any]:
        """Return metadata for a registered agent."""

        metadata = self.registry.get(name)

        return {
            "agent_id": metadata.agent_id,
            "agent_name": metadata.agent_id,
            "name": (
                metadata.display_name
                or metadata.agent_id
            ),
            "display_name": metadata.display_name,
            "description": metadata.description,
            "category": metadata.category,
            "capabilities": list(
                metadata.capabilities
            ),
            "dependencies": list(
                metadata.dependencies
            ),
            "enabled": metadata.enabled,
            "class": metadata.agent_class.__name__,
        }

    # =========================================================

    def list_agent_info(
        self,
    ) -> list[Dict[str, Any]]:
        """
        Return metadata for all registered agents.

        A malformed agent entry does not prevent metadata
        for the remaining agents from being returned.
        """

        result: list[Dict[str, Any]] = []

        for metadata in self.registry.get_all():
            try:
                result.append(
                    self.get_agent_info(
                        metadata.agent_id
                    )
                )

            except Exception:
                logger.exception(
                    "Failed to load metadata "
                    "for agent '%s'",
                    metadata.agent_id,
                )

        return result

