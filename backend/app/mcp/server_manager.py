from __future__ import annotations

from typing import Dict, Any, Optional

from app.mcp.config import MCPConfig
from app.mcp.client import MCPClient


class MCPServerManager:
    """
    Manages MCP server lifecycle.

    Responsibilities:
    - Create MCP clients
    - Connect servers
    - Disconnect servers
    - Route requests
    """


    def __init__(self):

        self._servers: Dict[str, MCPClient] = {}



    async def register_server(
        self,
        name: str,
        config: MCPConfig
    ) -> MCPClient:
        """
        Register and connect an MCP server.
        """

        if name in self._servers:
            return self._servers[name]


        client = MCPClient(
            config=config
        )


        await client.connect()


        self._servers[name] = client


        return client



    async def remove_server(
        self,
        name: str
    ):

        client = self._servers.get(name)

        if not client:
            return


        await client.disconnect()


        del self._servers[name]



    def get_server(
        self,
        name: str
    ) -> Optional[MCPClient]:

        return self._servers.get(name)



    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ):

        server = self.get_server(server_name)


        if not server:
            raise RuntimeError(
                f"MCP server '{server_name}' not found"
            )


        return await server.call_tool(
            tool_name,
            arguments
        )



    def list_servers(self):

        return list(
            self._servers.keys()
        )