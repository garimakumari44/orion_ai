"""
Unified response model returned by every provider.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .message import ChatMessage
from .usage import TokenUsage
from .tool_call import ToolCall


class Choice(BaseModel):
    """
    One generated completion.
    """

    index: int = 0

    message: ChatMessage

    finish_reason: Optional[str] = None

    tool_calls: List[ToolCall] = Field(default_factory=list)


class LLMResponse(BaseModel):
    """
    Standardized LLM response.
    """

    id: Optional[str] = None

    model: str

    provider: str

    created: datetime = Field(default_factory=datetime.utcnow)

    choices: List[Choice]

    usage: Optional[TokenUsage] = None

    latency_ms: Optional[float] = None

    cost: Optional[float] = None

    raw: Optional[Dict[str, Any]] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def text(self) -> str:
        """
        Convenience accessor.
        """
        if not self.choices:
            return ""

        return self.choices[0].message.content or ""