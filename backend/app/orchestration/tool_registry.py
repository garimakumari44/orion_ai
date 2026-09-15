"""
app/orchestration/tool_registry.py

Central registry for all tools available to Orion.

Supports:
- Native Python tools
- MCP adapter tools
- Capability discovery
- Unified tool lookup

Does NOT:
- Execute tools
- Select tools
- Apply policies
"""

from __future__ import annotations

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
)

from app.orchestration.capability import Capability
from app.tools.base.base_tool import BaseTool

if TYPE_CHECKING:
    from app.tools.mcp_adapters.base import MCPAdapter


class ToolRegistry:

    def __init__(
        self,
        mcp_adapter: Optional["MCPAdapter"] = None,
    ) -> None:

        # Native Orion tools
        self._tools: Dict[
            str,
            BaseTool,
        ] = {}

        # MCP tools
        self._mcp_tools: Dict[
            str,
            "MCPAdapter",
        ] = {}

        # Capability -> tool names
        self._capability_index: Dict[
            Capability,
            List[str],
        ] = defaultdict(list)

        self.mcp_adapter = mcp_adapter

    # =========================================================
    # Native Registration
    # =========================================================

    def register(
        self,
        tool: BaseTool,
    ) -> None:

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' already registered."
            )

        if tool.name in self._mcp_tools:
            raise ValueError(
                f"Tool '{tool.name}' already registered as MCP tool."
            )

        self._tools[
            tool.name
        ] = tool

        self._register_capabilities(
            tool.name,
            getattr(
                tool,
                "capabilities",
                [],
            ),
        )

    # =========================================================
    # MCP Registration
    # =========================================================

    async def discover_mcp_tools(
        self,
    ) -> None:

        if self.mcp_adapter is None:

            raise RuntimeError(
                "MCP adapter is not configured."
            )

        tools = await self.mcp_adapter.discover_tools()

        for tool in tools:
            self.register_mcp_tool(tool)

    def register_mcp_tool(
        self,
        tool: "MCPAdapter",
    ) -> None:

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' already registered as native tool."
            )

        if tool.name in self._mcp_tools:
            return

        self._mcp_tools[
            tool.name
        ] = tool

        self._register_capabilities(
            tool.name,
            getattr(
                tool,
                "capabilities",
                [],
            ),
        )

    # =========================================================
    # Capability Index
    # =========================================================

    def _register_capabilities(
        self,
        tool_name: str,
        capabilities: List[Capability],
    ) -> None:

        for capability in capabilities:

            if tool_name not in self._capability_index[
                capability
            ]:

                self._capability_index[
                    capability
                ].append(tool_name)

    # =========================================================
    # Unregister
    # =========================================================

    def unregister(
        self,
        tool_name: str,
    ) -> None:

        self._tools.pop(
            tool_name,
            None,
        )

        self._mcp_tools.pop(
            tool_name,
            None,
        )

        for capability, tools in list(
            self._capability_index.items()
        ):

            if tool_name in tools:
                tools.remove(tool_name)

            if not tools:
                del self._capability_index[
                    capability
                ]

    # =========================================================
    # Lookup
    # =========================================================

    def get(
        self,
        tool_name: str,
    ) -> Optional[Any]:

        local_tool = self._tools.get(
            tool_name
        )

        if local_tool is not None:
            return local_tool

        return self._mcp_tools.get(
            tool_name
        )

    def get_local_tool(
        self,
        tool_name: str,
    ) -> Optional[BaseTool]:

        return self._tools.get(
            tool_name
        )

    def get_mcp_tool(
        self,
        tool_name: str,
    ) -> Optional["MCPAdapter"]:

        return self._mcp_tools.get(
            tool_name
        )

    # =========================================================
    # Capability Search
    # =========================================================

    def find_by_capability(
        self,
        capability: Capability,
    ) -> List[Any]:

        tool_names = self._capability_index.get(
            capability,
            [],
        )

        tools = []

        for name in tool_names:

            tool = self.get(name)

            if tool is not None:
                tools.append(tool)

        return tools

    # =========================================================
    # Inspection
    # =========================================================

    def all_tools(
        self,
    ) -> Dict[str, List[Any]]:

        return {
            "local": list(
                self._tools.values()
            ),
            "mcp": list(
                self._mcp_tools.values()
            ),
        }

    def get_all_local_tools(
        self,
    ) -> List[BaseTool]:

        return list(
            self._tools.values()
        )

    def get_all_mcp_tools(
        self,
    ) -> List[Any]:

        return list(
            self._mcp_tools.values()
        )

    def tool_names(
        self,
    ) -> List[str]:

        return (
            list(
                self._tools.keys()
            )
            +
            list(
                self._mcp_tools.keys()
            )
        )

    def has_tool(
        self,
        tool_name: str,
    ) -> bool:

        return (
            tool_name in self._tools
            or
            tool_name in self._mcp_tools
        )

    def clear(
        self,
    ) -> None:

        self._tools.clear()
        self._mcp_tools.clear()
        self._capability_index.clear()

    # =========================================================
    # Magic Methods
    # =========================================================

    def __len__(
        self,
    ) -> int:

        return (
            len(self._tools)
            +
            len(self._mcp_tools)
        )

    def __contains__(
        self,
        tool_name: str,
    ) -> bool:

        return self.has_tool(
            tool_name
        )