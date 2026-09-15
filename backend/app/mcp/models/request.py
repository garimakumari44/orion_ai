from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class MCPRequest(BaseModel):
    """
    Base MCP request model.

    Every MCP message contains:
    - request id
    - method name
    - parameters
    """

    id: str = Field(
        ...,
        description="Unique request identifier"
    )

    method: str = Field(
        ...,
        description="MCP operation name"
    )

    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Request parameters"
    )


class ToolRequest(BaseModel):
    """
    Request to execute an MCP tool.

    Example:

    {
        "tool": "github_search",
        "arguments": {
            "query": "transformers"
        }
    }
    """

    tool: str = Field(
        ...,
        description="Tool name to execute"
    )

    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to tool"
    )


class ResourceRequest(BaseModel):
    """
    Request to retrieve a resource.

    Example:

    {
        "uri": "file://project/readme.md"
    }
    """

    uri: str = Field(
        ...,
        description="Resource URI"
    )


class PromptRequest(BaseModel):
    """
    Request to retrieve a prompt template.

    Example:

    {
        "name": "code_review",
        "arguments": {
            "language": "python"
        }
    }
    """

    name: str = Field(
        ...,
        description="Prompt name"
    )

    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Prompt variables"
    )


class InitializeRequest(BaseModel):
    """
    MCP initialization handshake request.

    Sent when client connects.

    Example:

    {
        "client_name": "orion-agent",
        "version": "1.0"
    }
    """

    client_name: str

    version: str


class CapabilityRequest(BaseModel):
    """
    Request for server capabilities.

    Used during discovery phase.
    """

    capability_type: Optional[str] = None