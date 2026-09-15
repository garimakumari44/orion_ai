"""
Standard Tool Result Object

Every tool returns this structure.

Example:

SEC Tool
    |
    returns
    |
ToolResult(
    success=True,
    data={
        "filing": "10-K",
        "year":2025
    }
)

"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime


@dataclass
class ToolResult:
    """
    Universal response format for tools.
    """

    success: bool

    tool_name: str

    data: Optional[Any] = None

    error: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    citations: List[str] = field(
        default_factory=list
    )

    timestamp: str = field(
        default_factory=lambda:
        datetime.utcnow().isoformat()
    )


    # -----------------------------
    # Success Factory
    # -----------------------------

    @classmethod
    def success_result(
        cls,
        tool_name: str,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None,
        citations: Optional[List[str]] = None
    ):

        return cls(

            success=True,

            tool_name=tool_name,

            data=data,

            metadata=metadata or {},

            citations=citations or []

        )


    # -----------------------------
    # Failure Factory
    # -----------------------------

    @classmethod
    def failure(
        cls,
        tool_name: str,
        error: str
    ):

        return cls(

            success=False,

            tool_name=tool_name,

            error=error

        )


    # -----------------------------
    # Serialization
    # -----------------------------

    def to_dict(self) -> Dict[str, Any]:

        return {

            "success": self.success,

            "tool_name": self.tool_name,

            "data": self.data,

            "error": self.error,

            "metadata": self.metadata,

            "citations": self.citations,

            "timestamp": self.timestamp

        }


    def __bool__(self):

        return self.success