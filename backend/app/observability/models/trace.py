# models/trace.py

from datetime import datetime
from typing import Dict, Optional, List, Any
from enum import Enum

from pydantic import BaseModel, Field


class SpanType(str, Enum):
    """
    Type of execution span.
    """

    LLM = "llm"
    AGENT = "agent"
    TOOL = "tool"
    RETRIEVAL = "retrieval"
    DATABASE = "database"
    API = "api"
    SYSTEM = "system"


class SpanStatus(str, Enum):
    """
    Span execution status.
    """

    STARTED = "started"
    SUCCESS = "success"
    FAILED = "failed"


class TraceContext(BaseModel):
    """
    Distributed tracing context.
    """

    trace_id: str = Field(
        ...,
        description="Unique trace identifier"
    )

    parent_span_id: Optional[str] = None


class Span(BaseModel):
    """
    Individual execution unit inside a trace.

    Example:
        User Query
            |
            ├── Planner Agent
            |
            ├── Retrieval
            |
            ├── LLM Call
            |
            └── Response Generation
    """

    span_id: str

    trace_id: str

    name: str

    span_type: SpanType

    status: SpanStatus = SpanStatus.STARTED


    start_time: datetime = Field(
        default_factory=datetime.utcnow
    )

    end_time: Optional[datetime] = None


    duration_ms: Optional[float] = None


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )


    attributes: Dict[str, Any] = Field(
        default_factory=dict
    )


    error: Optional[str] = None



class Trace(BaseModel):
    """
    Complete distributed trace.

    Represents one complete AI request lifecycle.
    """

    trace_id: str


    request_id: Optional[str] = None


    service_name: str = "ai-platform"


    operation_name: str


    started_at: datetime = Field(
        default_factory=datetime.utcnow
    )


    completed_at: Optional[datetime] = None


    spans: List[Span] = Field(
        default_factory=list
    )


    total_latency_ms: Optional[float] = None


    success: bool = True


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )



    def add_span(self, span: Span):
        """
        Add span to trace.
        """

        self.spans.append(span)



    def calculate_latency(self):

        if self.completed_at:

            self.total_latency_ms = (
                self.completed_at -
                self.started_at
            ).total_seconds() * 1000