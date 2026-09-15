from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MCPError(BaseModel):
    """
    Represents an MCP execution error.
    """

    code: str = Field(
        description="Machine-readable error code"
    )

    message: str = Field(
        description="Human-readable error message"
    )

    details: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    """
    Standard response returned by an MCP server.

    Example:

    {
        "request_id": "abc123",
        "success": true,
        "data": {
            "result": "github repository found"
        }
    }
    """

    request_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    success: bool = True

    data: Optional[Any] = None

    error: Optional[MCPError] = None

    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


    @classmethod
    def success_response(
        cls,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> "MCPResponse":
        """
        Create successful MCP response.
        """

        return cls(
            request_id=request_id or str(uuid4()),
            success=True,
            data=data,
            metadata=metadata or {},
        )


    @classmethod
    def error_response(
        cls,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> "MCPResponse":
        """
        Create failed MCP response.
        """

        return cls(
            request_id=request_id or str(uuid4()),
            success=False,
            error=MCPError(
                code=code,
                message=message,
                details=details,
            ),
        )