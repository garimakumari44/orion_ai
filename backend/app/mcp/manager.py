"""
app/mcp/manager.py

Central MCP orchestration layer.

Responsibilities:
- Register MCP servers
- Remove MCP servers
- Execute MCP tools
- Monitor MCP server health
- Expose server discovery
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from app.mcp.server_manager import MCPServerManager
from app.mcp.health import MCPHealthMonitor
from app.mcp.config import MCPConfig


logger = logging.getLogger(__name__)


class MCPManager:
    """
    Central MCP orchestration service.

    Used by:
    - Tool Registry
    - Agents
    - Execution Engine
    - Planner
    """

    def __init__(
        self,
        server_manager: MCPServerManager | None = None,
        health_monitor: MCPHealthMonitor | None = None,
    ) -> None:

        self.server_manager = (
            server_manager
            if server_manager is not None
            else MCPServerManager()
        )

        self.health_monitor = (
            health_monitor
            if health_monitor is not None
            else MCPHealthMonitor()
        )

    # =========================================================
    # Server Management
    # =========================================================

    async def add_server(
        self,
        name: str,
        config: MCPConfig,
    ):

        logger.info(
            "Registering MCP server: %s",
            name,
        )

        client = await self.server_manager.register_server(
            name,
            config,
        )

        self.health_monitor.register_server(
            name
        )

        return client

    async def remove_server(
        self,
        name: str,
    ):

        logger.info(
            "Removing MCP server: %s",
            name,
        )

        await self.server_manager.remove_server(
            name
        )

    def get_server(
        self,
        name: str,
    ):

        return self.server_manager.get_server(
            name
        )

    def list_servers(self):

        return self.server_manager.list_servers()

    # =========================================================
    # Tool Execution
    # =========================================================

    async def execute_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ):

        return await self.server_manager.call_tool(
            server_name,
            tool_name,
            arguments,
        )

    # =========================================================
    # Health
    # =========================================================

    async def health_check(
        self,
        server_name: str,
    ):

        server = self.server_manager.get_server(
            server_name
        )

        if server is None:

            raise RuntimeError(
                f"MCP server '{server_name}' is not registered."
            )

        return await self.health_monitor.check_health(
            server_name,
            server.ping,
        )