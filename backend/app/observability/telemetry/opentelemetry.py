"""
OpenTelemetry integration.

Provides:
- Tracing setup
- Span creation
- Trace context management
- Agent / LLM / Tool tracing
"""


from typing import Optional
from contextlib import contextmanager


from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor
)

from opentelemetry.sdk.resources import Resource


try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter
    )

except ImportError:
    OTLPSpanExporter = None



class OpenTelemetryManager:
    """
    Global OpenTelemetry manager.
    """


    def __init__(
        self,
        service_name: str = "ai-platform"
    ):

        self.service_name = service_name

        self.tracer = None



    def initialize(
        self,
        exporter_endpoint: Optional[str] = None
    ):


        resource = Resource.create(
            {
                "service.name":
                    self.service_name
            }
        )


        provider = TracerProvider(
            resource=resource
        )


        if (
            exporter_endpoint
            and OTLPSpanExporter
        ):

            exporter = OTLPSpanExporter(
                endpoint=exporter_endpoint
            )


            processor = BatchSpanProcessor(
                exporter
            )


            provider.add_span_processor(
                processor
            )


        trace.set_tracer_provider(
            provider
        )


        self.tracer = trace.get_tracer(
            self.service_name
        )


        return self.tracer



    @contextmanager
    def span(
        self,
        name: str,
        attributes: dict = None
    ):

        if self.tracer is None:
            self.initialize()


        with self.tracer.start_as_current_span(
            name
        ) as span:


            if attributes:

                for key, value in attributes.items():

                    span.set_attribute(
                        key,
                        value
                    )


            yield span



    def add_event(
        self,
        span,
        name: str,
        attributes: dict = None
    ):

        span.add_event(
            name,
            attributes or {}
        )



    def record_exception(
        self,
        span,
        error: Exception
    ):

        span.record_exception(
            error
        )

        span.set_status(
            trace.Status(
                trace.StatusCode.ERROR
            )
        )



telemetry = OpenTelemetryManager()