"""
Span primitives.

A span represents a single operation inside a trace.

Examples:
- LLM generation span
- Retrieval span
- Tool execution span
- Agent execution span
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import time
import uuid


def generate_id(length: int = 16) -> str:
    return uuid.uuid4().hex[:length]


@dataclass
class Span:
    """
    Represents one traced operation.
    """

    name: str

    trace_id: str

    parent_span_id: Optional[str] = None

    span_id: str = field(
        default_factory=lambda: generate_id()
    )

    start_time: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    end_time: Optional[datetime] = None

    duration_ms: Optional[float] = None

    attributes: Dict[str, Any] = field(
        default_factory=dict
    )

    events: list = field(
        default_factory=list
    )

    status: str = "running"


    def set_attribute(
        self,
        key: str,
        value: Any
    ):
        """
        Add metadata to span.

        Example:
        span.set_attribute(
            "model",
            "gpt-4"
        )
        """

        self.attributes[key] = value



    def add_event(
        self,
        name: str,
        data: Optional[dict] = None
    ):
        """
        Add timestamped event.

        Example:

        tool_started
        retrieval_completed
        """

        self.events.append(
            {
                "name": name,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
                "data": data or {}
            }
        )



    def finish(
        self,
        status: str = "success"
    ):
        """
        Close span.
        """

        self.end_time = datetime.now(
            timezone.utc
        )

        self.duration_ms = (
            self.end_time -
            self.start_time
        ).total_seconds() * 1000


        self.status = status



    def fail(
        self,
        error: Exception
    ):
        """
        Mark span failed.
        """

        self.attributes[
            "error.type"
        ] = type(error).__name__


        self.attributes[
            "error.message"
        ] = str(error)


        self.finish(
            status="error"
        )



    def to_dict(self):
        """
        Serialize span.
        """

        return {

            "trace_id":
                self.trace_id,

            "span_id":
                self.span_id,

            "parent_span_id":
                self.parent_span_id,

            "name":
                self.name,

            "status":
                self.status,

            "duration_ms":
                self.duration_ms,

            "attributes":
                self.attributes,

            "events":
                self.events,

            "start_time":
                self.start_time.isoformat(),

            "end_time":
                (
                    self.end_time.isoformat()
                    if self.end_time
                    else None
                )
        }