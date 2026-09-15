"""
Provider-independent tool calling models.

These models standardize tool/function definitions and tool calls
across OpenAI, Anthropic, Gemini, Ollama, Azure OpenAI, and OpenRouter.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ToolType(str, Enum):
    """
    Supported tool types.
    """

    FUNCTION = "function"


class ToolFunction(BaseModel):
    """
    Callable function exposed to the LLM.
    """

    name: str

    description: str = ""

    parameters: Dict[str, Any] = Field(default_factory=dict)


class ToolDefinition(BaseModel):
    """
    Tool exposed to the model.
    """

    type: ToolType = ToolType.FUNCTION

    function: ToolFunction


class ToolCallFunction(BaseModel):
    """
    Function selected by the model.
    """

    name: str

    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    """
    Tool invocation returned by an LLM.
    """

    id: Optional[str] = None

    type: ToolType = ToolType.FUNCTION

    function: ToolCallFunction


class ToolResult(BaseModel):
    """
    Result returned after executing a tool.
    """

    tool_call_id: Optional[str] = None

    name: str

    output: Any

    success: bool = True

    error: Optional[str] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)