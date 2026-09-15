from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import uuid
import json


# ============================================================
# Message Types
# ============================================================

class MessageType(str, Enum):
    """
    MCP message categories.
    """

    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    EVENT = "event"


# ============================================================
# MCP Methods
# ============================================================

class MCPMethod(str, Enum):
    """
    Operations supported by MCP protocol.
    """

    INITIALIZE = "initialize"

    LIST_TOOLS = "list_tools"
    CALL_TOOL = "call_tool"

    LIST_RESOURCES = "list_resources"
    READ_RESOURCE = "read_resource"

    LIST_PROMPTS = "list_prompts"
    GET_PROMPT = "get_prompt"


# ============================================================
# Base Message
# ============================================================

@dataclass
class MCPMessage:
    """
    Base MCP message.

    Every message exchanged between
    client and server follows this structure.
    """

    type: MessageType

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    payload: Dict[str, Any] = field(
        default_factory=dict
    )


    def to_dict(self) -> Dict[str, Any]:
        """
        Convert message to JSON-compatible dictionary.
        """

        return {
            "id": self.id,
            "type": self.type.value,
            "payload": self.payload,
        }


    def to_json(self) -> str:
        """
        Serialize message.
        """

        return json.dumps(
            self.to_dict()
        )


    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any]
    ) -> "MCPMessage":

        return cls(
            id=data.get("id"),
            type=MessageType(
                data.get("type")
            ),
            payload=data.get(
                "payload",
                {}
            )
        )


    @classmethod
    def from_json(
        cls,
        data: str
    ) -> "MCPMessage":

        return cls.from_dict(
            json.loads(data)
        )



# ============================================================
# Request Message
# ============================================================

@dataclass
class MCPRequest(MCPMessage):
    """
    Client -> Server request.
    """

    method: MCPMethod = MCPMethod.INITIALIZE


    def __post_init__(self):

        self.type = MessageType.REQUEST



    def to_dict(self):

        data = super().to_dict()

        data["method"] = self.method.value

        return data



# ============================================================
# Response Message
# ============================================================

@dataclass
class MCPResponse(MCPMessage):
    """
    Server -> Client response.
    """

    success: bool = True


    def __post_init__(self):

        self.type = MessageType.RESPONSE



    def to_dict(self):

        data = super().to_dict()

        data["success"] = self.success

        return data



# ============================================================
# Error Message
# ============================================================

@dataclass
class MCPError(MCPMessage):
    """
    Error returned by MCP server.
    """

    error_code: str = "UNKNOWN_ERROR"

    message: str = ""


    def __post_init__(self):

        self.type = MessageType.ERROR



    def to_dict(self):

        data = super().to_dict()

        data.update(
            {
                "error_code": self.error_code,
                "message": self.message,
            }
        )

        return data



# ============================================================
# Helpers
# ============================================================

def create_request(
    method: MCPMethod,
    payload: Optional[Dict[str, Any]] = None
) -> MCPRequest:
    """
    Create MCP request.
    """

    return MCPRequest(
        method=method,
        payload=payload or {}
    )



def create_response(
    request_id: str,
    result: Any
) -> MCPResponse:
    """
    Create MCP response.
    """

    return MCPResponse(
        id=request_id,
        payload={
            "result": result
        }
    )



def create_error(
    request_id: str,
    code: str,
    message: str
) -> MCPError:
    """
    Create MCP error response.
    """

    return MCPError(
        id=request_id,
        error_code=code,
        message=message
    )