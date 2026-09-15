"""
Latency Alert Engine

Detects latency violations across:
- LLM calls
- API requests
- Agent execution
- Tool execution
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LatencyAlert:
    """
    Represents a latency threshold violation.
    """

    service: str
    latency_ms: float
    threshold_ms: float
    severity: str
    timestamp: datetime
    message: str


class LatencyMonitor:
    """
    Monitors latency metrics and generates alerts.
    """

    def __init__(
        self,
        default_threshold_ms: int = 3000
    ):
        self.default_threshold_ms = default_threshold_ms


    def check(
        self,
        service: str,
        latency_ms: float,
        threshold_ms: Optional[int] = None
    ) -> Optional[LatencyAlert]:

        threshold = (
            threshold_ms
            if threshold_ms
            else self.default_threshold_ms
        )


        if latency_ms <= threshold:
            return None


        severity = self._calculate_severity(
            latency_ms,
            threshold
        )


        return LatencyAlert(
            service=service,
            latency_ms=latency_ms,
            threshold_ms=threshold,
            severity=severity,
            timestamp=datetime.utcnow(),
            message=(
                f"{service} latency exceeded "
                f"{threshold}ms threshold"
            )
        )


    def _calculate_severity(
        self,
        latency_ms: float,
        threshold_ms: float
    ) -> str:

        ratio = latency_ms / threshold_ms


        if ratio >= 3:
            return "critical"

        if ratio >= 2:
            return "warning"

        return "info"