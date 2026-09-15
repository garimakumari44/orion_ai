from __future__ import annotations

from typing import Any, Dict, List, Optional

from .session import MCPSession
from .transport import BaseTransport
from .exceptions import (
    MCPConnectionError,
    MCPToolExecutionError
)


class MCPClient:
    """
    High-level client for communicating with MCP servers.

    Responsibilities
    ----------------
    - Establish connections
    - Maintain an active session
    - Execute tools
    - Access resources
    - List server capabilities

    This is the primary entry point used by the orchestration layer.
    """

    def __init__(self, transport: BaseTransport):
        self.transport = transport
        self.session: Optional[MCPSession] = None

    async def connect(self) -> None:
        """
        Connect to the MCP server.
        """
        await self.transport.connect()

        self.session = MCPSession(self.transport)

        await self.session.initialize()

    async def disconnect(self) -> None:
        """
        Close the active session.
        """
        if self.session:
            await self.session.close()

        await self.transport.disconnect()

    @property
    def connected(self) -> bool:
        """
        Returns whether an active session exists.
        """
        return self.session is not None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Return all tools exposed by the server.
        """
        self._ensure_connected()

        return await self.session.list_tools()

    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a tool on the MCP server.
        """
        self._ensure_connected()

        try:
            return await self.session.call_tool(
                name=name,
                arguments=arguments,
            )

        except Exception as exc:
            raise MCPToolExecutionError(str(exc)) from exc

    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        List available resources.
        """
        self._ensure_connected()

        return await self.session.list_resources()

    async def read_resource(
        self,
        uri: str,
    ) -> Dict[str, Any]:
        """
        Read a resource from the server.
        """
        self._ensure_connected()

        return await self.session.read_resource(uri)

    def _ensure_connected(self) -> None:
        """
        Ensure an active session exists.
        """
        if self.session is None:
            raise MCPConnectionError(
                "MCP client is not connected."
            )