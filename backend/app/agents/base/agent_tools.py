"""
app/agents/base/agent_tools.py

Agent Tools
===========

Thin agent-level facade over the centralized tool system.

Architecture:

    Agent
      |
      v
    AgentTools
      |
      v
    ToolRouter
      |
      +--> ToolRegistry
      |
      +--> ToolSelector
      |
      +--> ToolExecutor
              |
              v
          Actual Tool


MCP remains available separately:

    Agent
      |
      +--> AgentTools / ToolRouter
      |
      +--> MCPManager


Design Principles
-----------------

1. AgentTools MUST NOT own the global tool registry.

2. AgentTools MUST NOT execute tools directly with:

       tool.run(...)

3. Tool registration belongs to the centralized ToolRegistry.

4. Tool selection belongs to ToolSelector / ToolRouter.

5. Tool execution belongs to ToolExecutor.

6. AgentTools is a thin convenience abstraction for agents.

7. AgentTools may maintain agent-local preferences or permissions,
   but must not duplicate the global tool registry.
"""

from __future__ import annotations

from typing import Any, Optional


class AgentTools:
    """
    Thin agent-facing facade for centralized tool execution.

    Agents should normally use:

        await self.agent_tools.execute(
            "company_search",
            query="Apple Inc.",
        )

    The request is delegated to the centralized ToolRouter.

    AgentTools does not own the global tool registry.
    """

    def __init__(
        self,
        tool_router: Optional[Any] = None,
    ) -> None:
        """
        Initialize the agent tool facade.

        Parameters
        ----------
        tool_router:
            Centralized ToolRouter responsible for routing,
            selecting, and executing tools.
        """

        self._tool_router = tool_router

    # =========================================================
    # Router Management
    # =========================================================

    @property
    def router(self) -> Any:
        """
        Return the centralized ToolRouter.
        """

        return self._tool_router

    def set_router(
        self,
        tool_router: Any,
    ) -> None:
        """
        Attach or replace the centralized ToolRouter.

        This method is primarily useful during dependency
        injection or runtime initialization.
        """

        if tool_router is None:
            raise ValueError(
                "tool_router is required"
            )

        self._tool_router = tool_router

    def has_router(self) -> bool:
        """
        Return True when a ToolRouter is available.
        """

        return self._tool_router is not None

    # =========================================================
    # Tool Execution
    # =========================================================

    async def execute(
        self,
        name: str,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a tool through the centralized ToolRouter.

        Flow:

            Agent
              |
              v
            AgentTools
              |
              v
            ToolRouter
              |
              v
            ToolRegistry
              |
              v
            ToolSelector
              |
              v
            ToolExecutor
              |
              v
            Actual Tool

        Parameters
        ----------
        name:
            Name or identifier of the requested tool.

        kwargs:
            Tool input parameters.

        Returns
        -------
        Any
            Result returned by the centralized tool system.
        """

        if not name:
            raise ValueError(
                "tool name is required"
            )

        if self._tool_router is None:
            raise RuntimeError(
                "ToolRouter is not configured for this agent"
            )

        return await self._tool_router.execute(
            tool_name=name,
            **kwargs,
        )

    # =========================================================
    # Tool Discovery
    # =========================================================

    async def get(
        self,
        name: str,
    ) -> Any:
        """
        Retrieve tool metadata or a registered tool through
        the centralized ToolRouter.

        This does not execute the tool.

        The exact ToolRouter API may expose `get_tool()`.
        """

        if not name:
            raise ValueError(
                "tool name is required"
            )

        if self._tool_router is None:
            raise RuntimeError(
                "ToolRouter is not configured for this agent"
            )

        get_tool = getattr(
            self._tool_router,
            "get_tool",
            None,
        )

        if get_tool is None:
            raise NotImplementedError(
                "ToolRouter does not expose get_tool()"
            )

        return await get_tool(
            tool_name=name,
        )

    async def available_tools(
        self,
    ) -> list[Any]:
        """
        Return tools available to this agent through the
        centralized ToolRouter.

        This method intentionally does not maintain a local
        duplicate registry.
        """

        if self._tool_router is None:
            raise RuntimeError(
                "ToolRouter is not configured for this agent"
            )

        list_tools = getattr(
            self._tool_router,
            "list_tools",
            None,
        )

        if list_tools is None:
            raise NotImplementedError(
                "ToolRouter does not expose list_tools()"
            )

        return await list_tools()

    # =========================================================
    # Intent-Based Execution
    # =========================================================

    async def execute_for_capability(
        self,
        capability: str,
        **kwargs: Any,
    ) -> Any:
        """
        Request tool execution by capability rather than
        an explicit tool name.

        Example:

            await self.agent_tools.execute_for_capability(
                "company_financials",
                ticker="AAPL",
            )

        ToolRouter / ToolSelector determines the appropriate
        registered tool.

        This method should only be used if the centralized
        ToolRouter supports capability-based selection.
        """

        if not capability:
            raise ValueError(
                "capability is required"
            )

        if self._tool_router is None:
            raise RuntimeError(
                "ToolRouter is not configured for this agent"
            )

        execute_for_capability = getattr(
            self._tool_router,
            "execute_for_capability",
            None,
        )

        if execute_for_capability is None:
            raise NotImplementedError(
                "ToolRouter does not expose "
                "execute_for_capability()"
            )

        return await execute_for_capability(
            capability=capability,
            **kwargs,
        )