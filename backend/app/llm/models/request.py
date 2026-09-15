"""
Provider-independent request models.

These models define the data sent to any LLM provider.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .message import ChatMessage
from .tool_call import ToolDefinition


class LLMRequest(BaseModel):
    """
    Standard request object for text generation.
    """

    model: str

    messages: List[ChatMessage]

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
    )

    max_tokens: Optional[int] = None

    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    frequency_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
    )

    presence_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
    )

    stop: Optional[List[str]] = None

    stream: bool = False

    seed: Optional[int] = None

    user: Optional[str] = None

    tools: List[ToolDefinition] = Field(default_factory=list)

    tool_choice: Optional[str] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)

    extra: Dict[str, Any] = Field(default_factory=dict)