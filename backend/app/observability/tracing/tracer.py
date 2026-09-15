"""
Tracer manager.

Responsible for:

- Creating traces
- Creating spans
- Managing active spans
- Exporting trace data
"""


from typing import Dict, Optional
from contextvars import ContextVar
import uuid

from .spans import Span


# Current active span
_current_span: ContextVar[
    Optional[Span]
] = ContextVar(
    "current_span",
    default=None
)



def generate_trace_id():

    return uuid.uuid4().hex



class Tracer:

    """
    Main tracing interface.

    Example:

        tracer = Tracer()

        with tracer.start_span(
            "llm_call"
        ) as span:

            span.set_attribute(
                "model",
                "gpt-4"
            )

    """

    def __init__(self):

        self.traces = {}



    def start_trace(
        self,
        name: str
    ):
        """
        Start root trace.
        """

        trace_id = generate_trace_id()


        span = Span(
            name=name,
            trace_id=trace_id
        )


        self.traces[
            trace_id
        ] = []


        self.traces[
            trace_id
        ].append(span)


        _current_span.set(span)


        return span



    def start_span(
        self,
        name: str,
        attributes: Optional[dict]=None
    ):
        """
        Create child span.
        """

        parent = (
            _current_span.get()
        )


        trace_id = (
            parent.trace_id
            if parent
            else generate_trace_id()
        )


        span = Span(
            name=name,
            trace_id=trace_id,
            parent_span_id=(
                parent.span_id
                if parent
                else None
            )
        )


        if attributes:
            span.attributes.update(
                attributes
            )


        if trace_id not in self.traces:
            self.traces[
                trace_id
            ] = []


        self.traces[
            trace_id
        ].append(span)


        _current_span.set(span)


        return span



    def get_current_span(
        self
    ):
        """
        Returns active span.
        """

        return _current_span.get()



    def end_span(
        self,
        span: Span
    ):

        span.finish()


        # restore parent
        if span.parent_span_id:

            for s in self.traces[
                span.trace_id
            ]:

                if (
                    s.span_id ==
                    span.parent_span_id
                ):
                    _current_span.set(s)
                    return


        _current_span.set(None)



    def export_trace(
        self,
        trace_id: str
    ):

        spans = self.traces.get(
            trace_id,
            []
        )


        return [
            span.to_dict()
            for span in spans
        ]



# Global tracer instance

tracer = Tracer()