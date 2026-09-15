from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.mcp.client import MCPClient
from app.mcp.session import MCPSession

from app.execution.models.task_result import TaskResult


logger = logging.getLogger(__name__)


class MCPAdapter:
    """
    Adapter between Orion orchestration layer and MCP protocol.

    Responsibilities:
    - Connect to MCP servers
    - Discover MCP tools
    - Execute MCP capabilities
    - Normalize MCP responses
    """


    def __init__(
        self,
        client: MCPClient,
    ):
        self.client = client
        self.session: Optional[MCPSession] = None


    async def connect(self):
        """
        Establish MCP session.
        """

        logger.info(
            "Connecting MCP adapter..."
        )

        self.session = await self.client.connect()

        logger.info(
            "MCP adapter connected"
        )


    async def disconnect(self):
        """
        Close MCP session.
        """

        if self.session:
            await self.session.close()

            logger.info(
                "MCP adapter disconnected"
            )


    async def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discover available MCP tools.

        Example response:

        [
            {
                "name": "search_web",
                "description": "Search internet",
                "parameters": {}
            }
        ]

        """

        if not self.session:
            raise RuntimeError(
                "MCP session not initialized"
            )


        tools = await self.session.list_tools()

        return tools



    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> TaskResult:
        """
        Execute MCP tool.

        Called by orchestration service.

        Example:

        execute_tool(
            "search_web",
            {
                "query":"latest AI papers"
            }
        )

        """


        if not self.session:
            raise RuntimeError(
                "MCP session not initialized"
            )


        logger.info(
            f"Executing MCP tool: {tool_name}"
        )


        try:

            response = await self.session.call_tool(
                name=tool_name,
                arguments=arguments
            )


            return TaskResult(
                success=True,
                output=response,
                error=None
            )


        except Exception as e:

            logger.exception(
                "MCP tool execution failed"
            )


            return TaskResult(
                success=False,
                output=None,
                error=str(e)
            )



    async def get_resource(
        self,
        resource_uri: str,
    ):
        """
        Fetch MCP resources.

        Example:
        file://docs/report.pdf
        database://customer/123
        """

        if not self.session:
            raise RuntimeError(
                "MCP session not initialized"
            )


        return await self.session.read_resource(
            resource_uri
        )



    async def get_prompts(self):
        """
        Retrieve MCP prompts.
        """

        if not self.session:
            raise RuntimeError(
                "MCP session not initialized"
            )


        return await self.session.list_prompts()