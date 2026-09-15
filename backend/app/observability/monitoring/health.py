"""
health.py

Application health monitoring.

Provides:
- Health status checks
- Readiness checks
- Liveness checks
- Dependency health aggregation
"""


from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """
    Represents a single health check.
    """

    def __init__(
        self,
        name: str,
        status: HealthStatus,
        message: str = "",
        metadata: Dict[str, Any] | None = None
    ):
        self.name = name
        self.status = status
        self.message = message
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "metadata": self.metadata
        }


class HealthManager:
    """
    Central health monitoring manager.

    Example:
        health = HealthManager()

        health.register(
            HealthCheck(
                "database",
                HealthStatus.HEALTHY
            )
        )

        health.status()
    """

    def __init__(self):

        self.checks: Dict[str, HealthCheck] = {}

        self.started_at = datetime.now(
            timezone.utc
        )


    def register(
        self,
        check: HealthCheck
    ):
        """
        Add or update health check.
        """

        self.checks[check.name] = check



    def remove(
        self,
        name: str
    ):
        """
        Remove health check.
        """

        self.checks.pop(
            name,
            None
        )



    def evaluate_status(
        self
    ) -> HealthStatus:
        """
        Calculate overall system health.
        """

        if not self.checks:
            return HealthStatus.HEALTHY


        statuses = [
            check.status
            for check in self.checks.values()
        ]


        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY


        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED


        return HealthStatus.HEALTHY



    def status(
        self
    ) -> Dict[str, Any]:
        """
        Return complete health report.
        """

        return {

            "status":
                self.evaluate_status().value,


            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),


            "uptime_since":
                self.started_at.isoformat(),


            "checks":
                [
                    check.to_dict()
                    for check in self.checks.values()
                ]
        }



    def is_ready(self):
        """
        Kubernetes readiness probe.

        Returns True when service
        can accept traffic.
        """

        return (
            self.evaluate_status()
            != HealthStatus.UNHEALTHY
        )



    def is_alive(self):
        """
        Kubernetes liveness probe.

        Indicates process is running.
        """

        return True