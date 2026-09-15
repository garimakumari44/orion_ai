from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .models.metadata import ServerMetadata
from .models.resource import Resource
from .models.prompt import Prompt


logger = logging.getLogger(__name__)


class MCPRegistry:
    """
    Central registry for MCP capabilities.

    Stores:
    - tools
    - resources
    - prompts
    - server metadata
    """

    def __init__(self):
        self.tools: Dict[str, ServerMetadata] = {}
        self.resources: Dict[str, Resource] = {}
        self.prompts: Dict[str, Prompt] = {}

        logger.info("MCP Registry initialized")


    # -------------------------
    # Tool Registration
    # -------------------------

    def register_tool(
        self,
        tool: ServerMetadata
    ) -> None:
        """
        Register an MCP tool.
        """

        if tool.name in self.tools:
            logger.warning(
                "Tool already registered: %s",
                tool.name
            )

        self.tools[tool.name] = tool

        logger.info(
            "Registered MCP tool: %s",
            tool.name
        )


    def unregister_tool(
        self,
        tool_name: str
    ) -> None:
        """
        Remove a tool from registry.
        """

        self.tools.pop(
            tool_name,
            None
        )


    def get_tool(
        self,
        tool_name: str
    ) -> Optional[ServerMetadata]:
        """
        Retrieve a tool.
        """

        return self.tools.get(tool_name)



    def list_tools(self) -> List[ServerMetadata]:
        """
        Return all registered tools.
        """

        return list(
            self.tools.values()
        )



    # -------------------------
    # Resource Registration
    # -------------------------

    def register_resource(
        self,
        resource: Resource
    ) -> None:
        """
        Register MCP resource.
        """

        self.resources[resource.name] = resource

        logger.info(
            "Registered resource: %s",
            resource.name
        )


    def get_resource(
        self,
        name: str
    ) -> Optional[Resource]:

        return self.resources.get(name)



    def list_resources(
        self
    ) -> List[Resource]:

        return list(
            self.resources.values()
        )



    # -------------------------
    # Prompt Registration
    # -------------------------

    def register_prompt(
        self,
        prompt: Prompt
    ) -> None:
        """
        Register reusable MCP prompt.
        """

        self.prompts[prompt.name] = prompt

        logger.info(
            "Registered prompt: %s",
            prompt.name
        )


    def get_prompt(
        self,
        name: str
    ) -> Optional[Prompt]:

        return self.prompts.get(name)



    def list_prompts(
        self
    ) -> List[Prompt]:

        return list(
            self.prompts.values()
        )



    # -------------------------
    # Discovery
    # -------------------------

    def discover(
        self
    ) -> dict:
        """
        Return MCP capability discovery information.

        Used during MCP handshake.
        """

        return {
            "tools": [
                tool.model_dump()
                for tool in self.tools.values()
            ],

            "resources": [
                resource.model_dump()
                for resource in self.resources.values()
            ],

            "prompts": [
                prompt.model_dump()
                for prompt in self.prompts.values()
            ]
        }



    # -------------------------
    # Health
    # -------------------------

    def clear(self):
        """
        Remove all registered capabilities.
        """

        self.tools.clear()
        self.resources.clear()
        self.prompts.clear()


    def size(self) -> dict:
        """
        Registry statistics.
        """

        return {
            "tools": len(self.tools),
            "resources": len(self.resources),
            "prompts": len(self.prompts)
        }