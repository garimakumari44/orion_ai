"""
Failure Alert Engine

Tracks:
- API failures
- LLM failures
- Agent crashes
- Tool failures
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class FailureAlert:

    component: str
    error_type: str
    error_message: str
    severity: str
    timestamp: datetime

    metadata: dict = field(
        default_factory=dict
    )


class FailureMonitor:
    """
    Detects and classifies failures.
    """


    def __init__(
        self,
        failure_threshold: int = 5
    ):

        self.failure_threshold = failure_threshold

        self.failure_history = {}



    def record_failure(
        self,
        component: str,
        exception: Exception,
        metadata: Optional[dict] = None
    ) -> FailureAlert:


        error_type = type(exception).__name__


        self.failure_history.setdefault(
            component,
            []
        )


        self.failure_history[component].append(
            datetime.utcnow()
        )


        severity = self._severity(
            component
        )


        return FailureAlert(

            component=component,

            error_type=error_type,

            error_message=str(exception),

            severity=severity,

            timestamp=datetime.utcnow(),

            metadata=metadata or {}

        )



    def _severity(
        self,
        component: str
    ) -> str:


        failures = len(
            self.failure_history.get(
                component,
                []
            )
        )


        if failures >= self.failure_threshold * 3:
            return "critical"


        if failures >= self.failure_threshold:
            return "warning"


        return "info"



    def get_failure_count(
        self,
        component: str
    ) -> int:

        return len(
            self.failure_history.get(
                component,
                []
            )
        )