"""
app/agents/base/registry.py

Canonical application-level registry for specialized agents.

Architecture:

    ResearchPlanner
          |
          v
      capability
          |
          v
      agent_name
          |
          v
     AgentMetadata
          |
          v
      agent_class
          |
          v
     AgentManager
          |
          v
    Specialized Agent

Responsibilities:

- Register agents
- Resolve agents by name
- Resolve agents by capability
- Find agents by category
- List registered agents
- List capabilities
- Expose registry metadata
- Validate registry consistency

The registry does NOT:

- create AgentContext
- create AgentServices
- instantiate agents
- execute agents
- execute tasks
- manage research lifecycle
- construct infrastructure
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional, Type

from .metadata import AgentMetadata


logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Application-level registry for specialized agents.

    Canonical mappings:

        agent_name -> AgentMetadata

        capability -> agent_name

    The registry stores agent classes and metadata only.

    Runtime agent construction belongs exclusively to
    AgentManager.
    """

    # ========================================================================
    # Initialization
    # ========================================================================

    def __init__(self) -> None:
        """
        Create an isolated registry.

        Each registry instance owns independent state.
        """

        # --------------------------------------------------------------------
        # Agent name -> AgentMetadata
        # --------------------------------------------------------------------

        self._agents: Dict[str, AgentMetadata] = {}

        # --------------------------------------------------------------------
        # Capability -> Agent name
        # --------------------------------------------------------------------

        self._capability_to_agent: Dict[str, str] = {}

    # ========================================================================
    # Normalization
    # ========================================================================

    @staticmethod
    def _normalize(
        value: str,
        field_name: str,
    ) -> str:
        """
        Normalize and validate a registry identifier.
        """

        if value is None:
            raise ValueError(
                f"{field_name} cannot be None"
            )

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string, "
                f"got {type(value).__name__}"
            )

        value = value.strip()

        if not value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return value

    # ========================================================================
    # Registration
    # ========================================================================

    def register(
        self,
        *,
        agent_name: str,
        agent_class: Type[Any],
        category: str,
        display_name: Optional[str] = None,
        description: str = "",
        capabilities: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        enabled: bool = True,
    ) -> AgentMetadata:
        """
        Register an agent class and its metadata.

        IMPORTANT:

        This method stores the class only.

        It NEVER instantiates the agent.

        AgentManager owns runtime construction.
        """

        # --------------------------------------------------------------------
        # Normalize primary fields
        # --------------------------------------------------------------------

        agent_name = self._normalize(
            agent_name,
            "agent_name",
        )

        category = self._normalize(
            category,
            "category",
        )

        # --------------------------------------------------------------------
        # Validate class
        # --------------------------------------------------------------------

        if not isinstance(agent_class, type):
            raise TypeError(
                "agent_class must be a class, "
                f"got {type(agent_class).__name__}"
            )

        # --------------------------------------------------------------------
        # Display name
        # --------------------------------------------------------------------

        if display_name is not None:
            if not isinstance(display_name, str):
                raise TypeError(
                    "display_name must be a string or None"
                )

            display_name = display_name.strip()

            if not display_name:
                display_name = None

        # --------------------------------------------------------------------
        # Description
        # --------------------------------------------------------------------

        if not isinstance(description, str):
            raise TypeError(
                "description must be a string"
            )

        description = description.strip()

        # --------------------------------------------------------------------
        # Enabled
        # --------------------------------------------------------------------

        if not isinstance(enabled, bool):
            raise TypeError(
                "enabled must be a boolean"
            )

        # --------------------------------------------------------------------
        # Prevent duplicate agent registration
        # --------------------------------------------------------------------

        if agent_name in self._agents:
            raise ValueError(
                f"Agent '{agent_name}' is already registered."
            )

        # --------------------------------------------------------------------
        # Normalize capabilities
        # --------------------------------------------------------------------

        resolved_capabilities: List[str] = []

        for capability in capabilities or []:
            normalized = self._normalize(
                capability,
                "capability",
            )

            if normalized not in resolved_capabilities:
                resolved_capabilities.append(normalized)

        # --------------------------------------------------------------------
        # Normalize dependencies
        # --------------------------------------------------------------------

        resolved_dependencies: List[str] = []

        for dependency in dependencies or []:
            normalized = self._normalize(
                dependency,
                "dependency",
            )

            if normalized not in resolved_dependencies:
                resolved_dependencies.append(normalized)

        # --------------------------------------------------------------------
        # Validate capability ownership BEFORE mutation
        # --------------------------------------------------------------------

        for capability in resolved_capabilities:

            existing_agent = (
                self._capability_to_agent.get(
                    capability
                )
            )

            if (
                existing_agent is not None
                and existing_agent != agent_name
            ):
                raise ValueError(
                    f"Capability '{capability}' is already "
                    f"mapped to agent '{existing_agent}', "
                    f"cannot remap to '{agent_name}'."
                )

        # --------------------------------------------------------------------
        # Create metadata
        # --------------------------------------------------------------------

        metadata = AgentMetadata(
            agent_id=agent_name,
            agent_class=agent_class,
            category=category,
            display_name=display_name,
            description=description,
            capabilities=resolved_capabilities,
            dependencies=resolved_dependencies,
            enabled=enabled,
        )

        # --------------------------------------------------------------------
        # Commit agent
        # --------------------------------------------------------------------

        self._agents[agent_name] = metadata

        # --------------------------------------------------------------------
        # Commit capability mappings
        # --------------------------------------------------------------------

        for capability in resolved_capabilities:
            self._capability_to_agent[
                capability
            ] = agent_name

        logger.info(
            "Agent registered | "
            "agent_name=%s | "
            "category=%s | "
            "capabilities=%s | "
            "enabled=%s",
            agent_name,
            category,
            resolved_capabilities,
            enabled,
        )

        return metadata

    # ========================================================================
    # Bulk Registration
    # ========================================================================

    def register_many(
        self,
        agents: Iterable[Dict[str, Any]],
    ) -> None:
        """
        Register multiple agents.

        Each configuration dictionary must be accepted by
        register().
        """

        if agents is None:
            return

        for config in agents:

            if not isinstance(config, dict):
                raise TypeError(
                    "Each agent registration must be "
                    "a dictionary."
                )

            self.register(**config)

    # ========================================================================
    # Agent Lookup
    # ========================================================================

    def get(
        self,
        agent_name: str,
    ) -> AgentMetadata:
        """
        Resolve an agent name to AgentMetadata.
        """

        agent_name = self._normalize(
            agent_name,
            "agent_name",
        )

        metadata = self._agents.get(
            agent_name
        )

        if metadata is None:
            raise KeyError(
                f"Unknown agent '{agent_name}'."
            )

        return metadata

    def get_class(
        self,
        agent_name: str,
    ) -> Type[Any]:
        """
        Resolve an agent name to its registered class.

        The class is returned but never instantiated.
        """

        return self.get(
            agent_name
        ).agent_class

    def exists(
        self,
        agent_name: str,
    ) -> bool:
        """
        Return True when an agent is registered.
        """

        if not isinstance(
            agent_name,
            str,
        ):
            return False

        return (
            agent_name.strip()
            in self._agents
        )

    # ========================================================================
    # Agent Name Lookup
    # ========================================================================

    def get_agent(
        self,
        agent_name: str,
    ) -> AgentMetadata:
        """
        Explicit alias for get().
        """

        return self.get(
            agent_name
        )

    def get_agent_for_name(
        self,
        agent_name: str,
    ) -> AgentMetadata:
        """
        Resolve:

            agent_name -> AgentMetadata
        """

        return self.get(
            agent_name
        )

    # ========================================================================
    # Capability Lookup
    # ========================================================================

    def get_agent_name_for_capability(
        self,
        capability: str,
    ) -> str:
        """
        Resolve:

            capability -> agent_name
        """

        capability = self._normalize(
            capability,
            "capability",
        )

        agent_name = (
            self._capability_to_agent.get(
                capability
            )
        )

        if agent_name is None:
            raise KeyError(
                f"No agent registered for "
                f"capability '{capability}'."
            )

        return agent_name

    def get_agent_for_capability(
        self,
        capability: str,
    ) -> AgentMetadata:
        """
        Resolve:

            capability
                |
                v
            agent_name
                |
                v
            AgentMetadata
        """

        agent_name = (
            self.get_agent_name_for_capability(
                capability
            )
        )

        return self.get(
            agent_name
        )

    def capability_exists(
        self,
        capability: str,
    ) -> bool:
        """
        Return True when a capability is registered.
        """

        if not isinstance(
            capability,
            str,
        ):
            return False

        return (
            capability.strip()
            in self._capability_to_agent
        )

    # ========================================================================
    # Agent Listing
    # ========================================================================

    def get_all(
        self,
    ) -> List[AgentMetadata]:
        """
        Return all registered agent metadata.
        """

        return list(
            self._agents.values()
        )

    def list_agent_names(
        self,
    ) -> List[str]:
        """
        Return all registered agent names.
        """

        return list(
            self._agents.keys()
        )

    def list_agent_ids(
        self,
    ) -> List[str]:
        """
        Backward-compatible alias for list_agent_names().
        """

        return self.list_agent_names()

    def list_capabilities(
        self,
    ) -> List[str]:
        """
        Return all registered capabilities.
        """

        return list(
            self._capability_to_agent.keys()
        )

    # ========================================================================
    # Category
    # ========================================================================

    def get_by_category(
        self,
        category: str,
    ) -> List[AgentMetadata]:
        """
        Find agents by category.
        """

        category = self._normalize(
            category,
            "category",
        )

        return [
            agent
            for agent in self._agents.values()
            if agent.category == category
        ]

    # ========================================================================
    # Capability
    # ========================================================================

    def get_by_capability(
        self,
        capability: str,
    ) -> List[AgentMetadata]:
        """
        Find agents exposing a capability.

        Capability ownership is unique, therefore this returns
        zero or one agent.
        """

        capability = self._normalize(
            capability,
            "capability",
        )

        agent_name = (
            self._capability_to_agent.get(
                capability
            )
        )

        if agent_name is None:
            return []

        metadata = self._agents.get(
            agent_name
        )

        if metadata is None:
            return []

        return [metadata]

    # ========================================================================
    # Canonical Resolution
    # ========================================================================

    def resolve(
        self,
        *,
        capability: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> AgentMetadata:
        """
        Resolve an agent using exactly one key.

        Supported:

            capability -> agent

            agent_name -> agent
        """

        provided = [
            capability is not None,
            agent_name is not None,
        ]

        if sum(provided) != 1:
            raise ValueError(
                "Exactly one of capability or "
                "agent_name must be provided."
            )

        if capability is not None:
            return self.get_agent_for_capability(
                capability
            )

        return self.get(
            agent_name  # type: ignore[arg-type]
        )

    # ========================================================================
    # Full Capability Resolution
    # ========================================================================

    def resolve_capability(
        self,
        capability: str,
    ) -> Dict[str, str]:
        """
        Return complete capability resolution.

        Example:

            {
                "capability": "company.research",
                "agent_name": "company",
            }
        """

        normalized_capability = self._normalize(
            capability,
            "capability",
        )

        agent_name = (
            self.get_agent_name_for_capability(
                normalized_capability
            )
        )

        return {
            "capability": normalized_capability,
            "agent_name": agent_name,
        }

    # ========================================================================
    # Enabled Agents
    # ========================================================================

    def is_enabled(
        self,
        agent_name: str,
    ) -> bool:
        """
        Return whether an agent is enabled.
        """

        return bool(
            self.get(
                agent_name
            ).enabled
        )

    def get_enabled_by_capability(
        self,
        capability: str,
    ) -> List[AgentMetadata]:
        """
        Return enabled agents exposing a capability.
        """

        return [
            agent
            for agent in self.get_by_capability(
                capability
            )
            if agent.enabled
        ]

    def get_enabled_by_category(
        self,
        category: str,
    ) -> List[AgentMetadata]:
        """
        Return enabled agents in a category.
        """

        return [
            agent
            for agent in self.get_by_category(
                category
            )
            if agent.enabled
        ]

    # ========================================================================
    # Registry Description
    # ========================================================================

    def describe(
        self,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Return a serializable registry description.
        """

        return {
            agent_name: {
                "agent_name": metadata.agent_id,
                "agent_id": metadata.agent_id,
                "category": metadata.category,
                "display_name": metadata.display_name,
                "description": metadata.description,
                "capabilities": list(
                    metadata.capabilities
                ),
                "dependencies": list(
                    metadata.dependencies
                ),
                "enabled": metadata.enabled,
            }
            for agent_name, metadata
            in self._agents.items()
        }

    # ========================================================================
    # Registry Validation
    # ========================================================================

    def validate(self) -> None:
        """
        Validate registry invariants.

        Called during application startup after all agents
        have been registered.
        """

        # --------------------------------------------------------------------
        # Capability -> agent references must be valid.
        # --------------------------------------------------------------------

        for (
            capability,
            agent_name,
        ) in self._capability_to_agent.items():

            if agent_name not in self._agents:
                raise RuntimeError(
                    f"Capability '{capability}' references "
                    f"unknown agent '{agent_name}'."
                )

        # --------------------------------------------------------------------
        # Every agent capability must point back to that agent.
        # --------------------------------------------------------------------

        for metadata in self._agents.values():

            if not metadata.agent_id:
                raise RuntimeError(
                    "Registered agent has no agent_id."
                )

            if metadata.agent_id not in self._agents:
                raise RuntimeError(
                    f"Agent metadata '{metadata.agent_id}' "
                    "is not present in the registry."
                )

            if not metadata.capabilities:
                raise RuntimeError(
                    f"Agent '{metadata.agent_id}' has no "
                    "registered capabilities."
                )

            for capability in metadata.capabilities:

                mapped_agent = (
                    self._capability_to_agent.get(
                        capability
                    )
                )

                if mapped_agent != metadata.agent_id:
                    raise RuntimeError(
                        f"Capability '{capability}' for agent "
                        f"'{metadata.agent_id}' maps to "
                        f"'{mapped_agent}', expected "
                        f"'{metadata.agent_id}'."
                    )

        logger.debug(
            "Agent registry validation passed | "
            "agents=%d | capabilities=%d",
            len(self._agents),
            len(self._capability_to_agent),
        )

    # ========================================================================
    # Clear
    # ========================================================================

    def clear(self) -> None:
        """
        Remove all registrations.

        Primarily useful for tests and controlled
        application reinitialization.
        """

        self._agents.clear()
        self._capability_to_agent.clear()

        logger.info(
            "AgentRegistry cleared"
        )