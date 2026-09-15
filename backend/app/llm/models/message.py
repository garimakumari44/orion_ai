"""
Provider-independent chat message models.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """
    Standard chat message roles supported across providers.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class MessageContent(BaseModel):
    """
    Structured content block.

    Useful for multimodal models where a message may contain
    text, images, audio, etc.
    """

    type: str = "text"

    text: Optional[str] = None

    data: Optional[Any] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    """
    Provider-independent chat message.
    """

    role: MessageRole

    content: Optional[str] = None

    name: Optional[str] = None

    tool_call_id: Optional[str] = None

    contents: List[MessageContent] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def text(self) -> str:
        """
        Returns the plain text content.
        """

        if self.content:
            return self.content

        texts = [
            block.text
            for block in self.contents
            if block.type == "text" and block.text
        ]

        return "\n".join(texts)

    def is_system(self) -> bool:
        return self.role == MessageRole.SYSTEM

    def is_user(self) -> bool:
        return self.role == MessageRole.USER

    def is_assistant(self) -> bool:
        return self.role == MessageRole.ASSISTANT

    def is_tool(self) -> bool:
        return self.role == MessageRole.TOOL