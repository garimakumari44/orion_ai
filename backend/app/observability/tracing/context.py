"""
Tracing context management.

Provides:
- Current trace id
- Current span
- Context propagation
- Async-safe tracing state
"""


from contextvars import ContextVar
from typing import Optional

from .spans import Span



# Active trace id

_trace_id_context: ContextVar[
    Optional[str]
] = ContextVar(
    "trace_id",
    default=None
)



# Active span

_span_context: ContextVar[
    Optional[Span]
] = ContextVar(
    "active_span",
    default=None
)



def set_trace_id(
    trace_id: str
):
    """
    Set current trace id.
    """

    _trace_id_context.set(
        trace_id
    )



def get_trace_id():
    """
    Get current trace id.
    """

    return _trace_id_context.get()



def set_current_span(
    span: Span
):
    """
    Set active span.
    """

    _span_context.set(
        span
    )



def get_current_span():
    """
    Return active span.
    """

    return _span_context.get()



def clear_context():
    """
    Clear tracing context.

    Used after request completion.
    """

    _trace_id_context.set(
        None
    )

    _span_context.set(
        None
    )



def inject_context(
    headers: dict
):
    """
    Inject tracing information
    into outgoing requests.

    Example:

    Service A
        |
        |
    Service B

    """

    trace_id = get_trace_id()


    if trace_id:

        headers[
            "x-trace-id"
        ] = trace_id


    span = get_current_span()


    if span:

        headers[
            "x-span-id"
        ] = span.span_id


    return headers



def extract_context(
    headers: dict
):
    """
    Extract tracing information
    from incoming requests.
    """

    trace_id = headers.get(
        "x-trace-id"
    )


    if trace_id:

        set_trace_id(
            trace_id
        )


    return trace_id