"""
app/agents/base/agent_memory.py

Agent Memory Facade

AgentMemory does NOT implement its own memory storage.

It provides a stable interface for agents while delegating all
memory operations to the centralized MemoryService.

Architecture:

    Agent
      |
      v
    AgentMemory
      |
      v
    MemoryService
      |
      +-- Working Memory
      +-- Episodic Memory
      +-- Semantic Memory
      +-- Vector Memory

Responsibilities
----------------
AgentMemory is responsible for:

- providing an agent-friendly memory API
- attaching agent/research/task context
- delegating reads and writes to MemoryService
- keeping memory concerns out of BaseAgent
- maintaining compatibility with agents that expect AgentMemory

AgentMemory is NOT responsible for:

- storing memory itself
- implementing vector search
- implementing embeddings
- implementing semantic memory
- implementing episodic memory
- implementing persistence
- maintaining a second in-memory dictionary
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class AgentMemory:
    """
    Agent-facing facade over the centralized MemoryService.

    Parameters
    ----------
    memory_service:
        Centralized memory service responsible for actual storage
        and retrieval.

    agent_id:
        Identifier of the current agent.

    research_id:
        Optional research execution identifier.

    task_id:
        Optional execution task identifier.

    user_id:
        Optional user identifier.
    """

    def __init__(
        self,
        memory_service: Any,
        *,
        agent_id: Optional[str] = None,
        research_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:

        if memory_service is None:
            raise ValueError(
                "AgentMemory requires a centralized MemoryService. "
                "AgentMemory must not create its own memory storage."
            )

        self.memory_service = memory_service

        self.agent_id = agent_id
        self.research_id = research_id
        self.task_id = task_id
        self.user_id = user_id

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    @property
    def context(self) -> Dict[str, Optional[str]]:
        """
        Memory scope/context associated with this agent.
        """

        return {
            "agent_id": self.agent_id,
            "research_id": self.research_id,
            "task_id": self.task_id,
            "user_id": self.user_id,
        }

    def update_context(
        self,
        *,
        agent_id: Optional[str] = None,
        research_id: Optional[str] = None,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Update the memory scope.

        Useful when an AgentMemory instance is created before the
        execution context is fully populated.
        """

        if agent_id is not None:
            self.agent_id = agent_id

        if research_id is not None:
            self.research_id = research_id

        if task_id is not None:
            self.task_id = task_id

        if user_id is not None:
            self.user_id = user_id

    # ------------------------------------------------------------------
    # Generic memory API
    # ------------------------------------------------------------------

    async def get(
        self,
        key: str,
        *,
        memory_type: str = "working",
        default: Any = None,
    ) -> Any:
        """
        Retrieve memory through the centralized MemoryService.

        `memory_type` may be:

        - working
        - episodic
        - semantic
        - vector

        The exact implementation is delegated to MemoryService.
        """

        result = await self.memory_service.get(
            key=key,
            memory_type=memory_type,
            context=self.context,
        )

        if result is None:
            return default

        return result

    async def set(
        self,
        key: str,
        value: Any,
        *,
        memory_type: str = "working",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Store memory through the centralized MemoryService.
        """

        return await self.memory_service.set(
            key=key,
            value=value,
            memory_type=memory_type,
            metadata=metadata or {},
            context=self.context,
        )

    async def delete(
        self,
        key: str,
        *,
        memory_type: str = "working",
    ) -> Any:
        """
        Delete memory through the centralized MemoryService.
        """

        return await self.memory_service.delete(
            key=key,
            memory_type=memory_type,
            context=self.context,
        )

    async def clear(
        self,
        *,
        memory_type: Optional[str] = None,
    ) -> Any:
        """
        Clear memory through the centralized MemoryService.

        If memory_type is None, the MemoryService decides whether
        all memory associated with this scope should be cleared.
        """

        return await self.memory_service.clear(
            memory_type=memory_type,
            context=self.context,
        )

    # ------------------------------------------------------------------
    # Working Memory
    # ------------------------------------------------------------------

    async def get_working(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Read short-lived execution state.
        """

        return await self.get(
            key,
            memory_type="working",
            default=default,
        )

    async def set_working(
        self,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Write short-lived execution state.
        """

        return await self.set(
            key,
            value,
            memory_type="working",
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Episodic Memory
    # ------------------------------------------------------------------

    async def remember_episode(
        self,
        event: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Record an execution/event experience.

        This delegates to the episodic memory implementation.
        """

        return await self.memory_service.remember_episode(
            event=event,
            metadata=metadata or {},
            context=self.context,
        )

    async def get_episodes(
        self,
        *,
        limit: int = 10,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Retrieve episodic memories relevant to this agent context.
        """

        return await self.memory_service.get_episodes(
            limit=limit,
            metadata=metadata or {},
            context=self.context,
        )

    # ------------------------------------------------------------------
    # Semantic Memory
    # ------------------------------------------------------------------

    async def get_semantic(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve durable semantic knowledge.
        """

        return await self.get(
            key,
            memory_type="semantic",
            default=default,
        )

    async def set_semantic(
        self,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Store durable semantic knowledge.
        """

        return await self.set(
            key,
            value,
            memory_type="semantic",
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Vector Memory
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        *,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Perform semantic/vector memory retrieval.

        The AgentMemory facade does not know how embeddings,
        vector indexes, ranking, or retrieval work.
        """

        return await self.memory_service.search(
            query=query,
            limit=limit,
            filters=filters or {},
            context=self.context,
        )