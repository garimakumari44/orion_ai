from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .models.metadata  import ServerMetadata
from .models.resource import Resource
from .models.prompt import Prompt
from .registry import MCPRegistry


logger = logging.getLogger(__name__)


class MCPDiscovery:
    """
    Discovers MCP servers and their capabilities.

    Responsibilities:
    - Register MCP servers
    - Fetch server metadata
    - Discover tools
    - Discover resources
    - Discover prompts
    """


    def __init__(self, registry: MCPRegistry,):
        # server_name -> metadata
        self.servers: Dict[str, ServerMetadata] = {}

        # server_name -> tools
        self.tools: Dict[str, List[dict]] = {}

        # server_name -> resources
        self.resources: Dict[str, List[Resource]] = {}

        # server_name -> prompts
        self.prompts: Dict[str, List[Prompt]] = {}
        
        self.registry = registry


    async def register_server(
        self,
        server_name: str,
        metadata: ServerMetadata
    ):
        """
        Register an MCP server.

        Example:
        github-mcp
        browser-mcp
        database-mcp
        """

        logger.info(
            "Registering MCP server: %s",
            server_name
        )

        self.servers[server_name] = metadata


    async def discover_tools(
        self,
        server_name: str,
        client
    ) -> List[dict]:
        """
        Discover tools exposed by MCP server.

        Example:

        github-mcp exposes:

        [
            {
                "name": "search_repo",
                "description": "Search Github repository"
            }
        ]

        """

        logger.info(
            "Discovering tools from %s",
            server_name
        )


        response = await client.list_tools()


        tools = response.get(
            "tools",
            []
        )


        self.tools[server_name] = tools


        return tools



    async def discover_resources(
        self,
        server_name: str,
        client
    ) -> List[Resource]:
        """
        Discover resources exposed by MCP server.

        Example:

        - files
        - documents
        - database tables
        """

        logger.info(
            "Discovering resources from %s",
            server_name
        )


        response = await client.list_resources()


        resources = response.get(
            "resources",
            []
        )


        self.resources[server_name] = resources


        return resources



    async def discover_prompts(
        self,
        server_name: str,
        client
    ) -> List[Prompt]:
        """
        Discover reusable MCP prompts.
        """

        logger.info(
            "Discovering prompts from %s",
            server_name
        )


        response = await client.list_prompts()


        prompts = response.get(
            "prompts",
            []
        )


        self.prompts[server_name] = prompts


        return prompts



    def get_server(
        self,
        server_name: str
    ) -> Optional[ServerMetadata]:
        """
        Retrieve server metadata.
        """

        return self.servers.get(server_name)



    def get_tools(
        self,
        server_name: str
    ) -> List[dict]:
        """
        Return discovered tools.
        """

        return self.tools.get(
            server_name,
            []
        )



    def get_resources(
        self,
        server_name: str
    ) -> List[Resource]:
        """
        Return discovered resources.
        """

        return self.resources.get(
            server_name,
            []
        )



    def get_prompts(
        self,
        server_name: str
    ) -> List[Prompt]:
        """
        Return discovered prompts.
        """

        return self.prompts.get(
            server_name,
            []
        )



    def list_servers(self) -> List[str]:
        """
        Return available MCP servers.
        """

        return list(
            self.servers.keys()
        )