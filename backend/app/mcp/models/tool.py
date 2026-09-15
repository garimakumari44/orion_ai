from __future__ import annotations

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """
    Defines a single tool input parameter.
    """

    name: str = Field(
        ...,
        description="Parameter name"
    )

    type: str = Field(
        ...,
        description="Parameter data type"
    )

    description: Optional[str] = Field(
        default=None,
        description="What this parameter represents"
    )

    required: bool = Field(
        default=True,
        description="Whether this parameter is mandatory"
    )


class ToolDefinition(BaseModel):
    """
    MCP Tool metadata.

    Represents a capability exposed by an MCP server.
    """

    id: str = Field(
        ...,
        description="Unique tool identifier"
    )

    name: str = Field(
        ...,
        description="Human readable tool name"
    )

    description: str = Field(
        ...,
        description="What the tool does"
    )

    server_id: Optional[str] = Field(
        default=None,
        description="MCP server exposing this tool"
    )

    version: str = Field(
        default="1.0",
        description="Tool version"
    )

    category: Optional[str] = Field(
        default=None,
        description="Tool category e.g search, database, analytics"
    )

    parameters: List[ToolParameter] = Field(
        default_factory=list,
        description="Accepted input parameters"
    )

    input_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON schema for tool input validation"
    )

    output_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="Expected output format"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional tool information"
    )

    enabled: bool = Field(
        default=True,
        description="Whether tool can currently be used"
    )


    def can_accept(self, arguments: Dict[str, Any]) -> bool:
        """
        Validate whether provided arguments match tool requirements.
        """

        for parameter in self.parameters:
            if parameter.required and parameter.name not in arguments:
                return False

        return True