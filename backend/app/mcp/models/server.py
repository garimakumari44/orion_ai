from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .metadata import ServerMetadata


class MCPServer(BaseModel):
    """
    Represents an MCP Server.

    This model describes:
    - server identity
    - metadata
    - capabilities
    - available resources
    - available tools
    - available prompts
    """

    id: str = Field(
        ...,
        description="Unique identifier for the MCP server"
    )

    name: str = Field(
        ...,
        description="Human readable server name"
    )

    version: str = Field(
        default="1.0.0",
        description="Server version"
    )

    metadata: Optional[ServerMetadata] = Field(
        default=None,
        description="Server metadata information"
    )

    capabilities: Dict[str, bool] = Field(
        default_factory=dict,
        description="Supported MCP capabilities"
    )

    tools: List[str] = Field(
        default_factory=list,
        description="Available tools exposed by this server"
    )

    resources: List[str] = Field(
        default_factory=list,
        description="Available resources exposed by this server"
    )

    prompts: List[str] = Field(
        default_factory=list,
        description="Available prompts exposed by this server"
    )

    endpoint: Optional[str] = Field(
        default=None,
        description="Connection endpoint of MCP server"
    )

    status: str = Field(
        default="unknown",
        description="Current server status"
    )


    def supports(self, capability: str) -> bool:
        """
        Check whether this MCP server supports a capability.

        Example:
            server.supports("tools")
        """

        return self.capabilities.get(
            capability,
            False
        )


    def add_tool(self, tool_name: str):
        """
        Register a new tool.
        """

        if tool_name not in self.tools:
            self.tools.append(tool_name)


    def add_resource(self, resource_name: str):
        """
        Register a new resource.
        """

        if resource_name not in self.resources:
            self.resources.append(resource_name)


    def add_prompt(self, prompt_name: str):
        """
        Register a new prompt.
        """

        if prompt_name not in self.prompts:
            self.prompts.append(prompt_name)


    def is_available(self) -> bool:
        """
        Check if server is ready.
        """

        return self.status == "active"