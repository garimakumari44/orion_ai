from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PromptArgument(BaseModel):
    """
    Represents a variable that a prompt accepts.

    Example:
    {
        "name": "repository",
        "description": "GitHub repository URL",
        "required": true
    }
    """

    name: str = Field(
        ...,
        description="Name of the prompt argument"
    )

    description: Optional[str] = Field(
        default=None,
        description="Explanation of the argument"
    )

    required: bool = Field(
        default=False,
        description="Whether this argument is mandatory"
    )


class Prompt(BaseModel):
    """
    MCP Prompt definition.

    A prompt is a reusable instruction template
    exposed by an MCP server.
    """

    name: str = Field(
        ...,
        description="Unique prompt identifier"
    )

    description: Optional[str] = Field(
        default=None,
        description="Human readable description"
    )

    arguments: List[PromptArgument] = Field(
        default_factory=list,
        description="Arguments accepted by this prompt"
    )

    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional prompt metadata"
    )


class PromptMessage(BaseModel):
    """
    Actual rendered prompt message.

    Example:

    role:
        user

    content:
        Analyze repository github.com/example/project
    """

    role: str = Field(
        ...,
        description="Message role (system/user/assistant)"
    )

    content: str = Field(
        ...,
        description="Prompt text content"
    )


class PromptTemplate(BaseModel):
    """
    Template used to generate a final prompt.

    Example:

    template:
        "Analyze repository {repo}"
    """

    name: str

    template: str

    variables: List[str] = Field(
        default_factory=list
    )