"""
Observability configuration.

Controls:
- Logging
- Tracing
- Metrics
- External integrations
"""


from dataclasses import dataclass
import os


@dataclass
class ObservabilityConfig:

    service_name: str = "ai-platform"

    environment: str = (
        os.getenv(
            "ENVIRONMENT",
            "development"
        )
    )


    enable_logging: bool = True


    enable_metrics: bool = True


    enable_tracing: bool = True


    log_level: str = (
        os.getenv(
            "LOG_LEVEL",
            "INFO"
        )
    )


    # OpenTelemetry

    otel_endpoint: str | None = (
        os.getenv(
            "OTEL_EXPORTER_ENDPOINT"
        )
    )


    # Langfuse / Phoenix / external tools

    langfuse_enabled: bool = (
        os.getenv(
            "LANGFUSE_ENABLED",
            "false"
        ).lower()
        == "true"
    )


    def as_dict(self):

        return {

            "service_name": self.service_name,

            "environment": self.environment,

            "logging": self.enable_logging,

            "metrics": self.enable_metrics,

            "tracing": self.enable_tracing,

            "log_level": self.log_level,

            "langfuse": self.langfuse_enabled

        }