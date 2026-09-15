# models/event.py

from datetime import datetime
from typing import Dict, Any, Optional

from enum import Enum

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """
    Categories of system events.
    """

    INFO = "info"

    WARNING = "warning"

    ERROR = "error"

    LLM_REQUEST = "llm_request"

    LLM_RESPONSE = "llm_response"

    AGENT_STARTED = "agent_started"

    AGENT_COMPLETED = "agent_completed"

    TOOL_EXECUTION = "tool_execution"

    RETRIEVAL = "retrieval"

    SYSTEM = "system"



class EventSeverity(str, Enum):
    """
    Event importance level.
    """

    LOW = "low"

    MEDIUM = "medium"

    HIGH = "high"

    CRITICAL = "critical"



class Event(BaseModel):
    """
    Represents an observable system event.

    Example:

    User Query
        |
        Event:
            type=LLM_REQUEST
            model=llama
            tokens=1200
    """

    event_id: str


    event_type: EventType


    severity: EventSeverity = EventSeverity.LOW


    timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )


    service_name: str = "ai-platform"


    component: Optional[str] = None


    trace_id: Optional[str] = None


    message: str



    payload: Dict[str, Any] = Field(
        default_factory=dict
    )


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )



    def attach_trace(
        self,
        trace_id: str
    ):
        """
        Connect event with distributed trace.
        """

        self.trace_id = trace_id