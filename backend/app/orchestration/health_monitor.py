"""
health_monitor.py

Tracks the health of every tool in the orchestration layer.

Responsibilities
----------------
• Record successful executions
• Record failures
• Measure latency
• Compute success rate
• Disable failing tools temporarily
• Recover tools after cooldown
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import RLock
from typing import Dict



# -------------------------------------------------------------------
# Tool Health
# -------------------------------------------------------------------


@dataclass
class ToolHealth:
    """
    Stores runtime statistics for a tool.
    """

    tool_name: str

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0

    total_latency: float = 0.0

    consecutive_failures: int = 0

    healthy: bool = True

    disabled_until: datetime | None = None

    last_error: str | None = None

    last_updated: datetime = field(default_factory=datetime.utcnow)

    @property
    def average_latency(self) -> float:
        if self.total_calls == 0:
            return 0.0

        return self.total_latency / self.total_calls

    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 1.0

        return self.successful_calls / self.total_calls


# -------------------------------------------------------------------
# Health Monitor
# -------------------------------------------------------------------


class HealthMonitor:
    """
    Tracks runtime health of every tool.

    Example

    monitor.record_success("github", 0.42)

    monitor.record_failure("browser", "timeout")

    if monitor.is_healthy("browser"):
        ...
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        cooldown_seconds: int = 60,
    ):
        self.failure_threshold = failure_threshold
        self.cooldown = timedelta(seconds=cooldown_seconds)

        self._health: Dict[str, ToolHealth] = {}

        self._lock = RLock()

    # --------------------------------------------------------------

    def register_tool(self, tool_name: str):

        with self._lock:
            if tool_name not in self._health:
                self._health[tool_name] = ToolHealth(tool_name)

    # --------------------------------------------------------------

    def record_success(
        self,
        tool_name: str,
        latency: float,
    ):

        with self._lock:

            self.register_tool(tool_name)

            health = self._health[tool_name]

            health.total_calls += 1
            health.successful_calls += 1
            health.total_latency += latency

            health.consecutive_failures = 0
            health.healthy = True
            health.disabled_until = None

            health.last_updated = datetime.utcnow()

    # --------------------------------------------------------------

    def record_failure(
        self,
        tool_name: str,
        error: str,
    ):

        with self._lock:

            self.register_tool(tool_name)

            health = self._health[tool_name]

            health.total_calls += 1
            health.failed_calls += 1

            health.consecutive_failures += 1

            health.last_error = error
            health.last_updated = datetime.utcnow()

            if health.consecutive_failures >= self.failure_threshold:

                health.healthy = False

                health.disabled_until = (
                    datetime.utcnow() + self.cooldown
                )

    # --------------------------------------------------------------

    def is_healthy(self, tool_name: str) -> bool:

        with self._lock:

            self.register_tool(tool_name)

            health = self._health[tool_name]

            if health.healthy:
                return True

            if (
                health.disabled_until is not None
                and datetime.utcnow() >= health.disabled_until
            ):
                health.healthy = True
                health.consecutive_failures = 0
                health.disabled_until = None

                return True

            return False

    # --------------------------------------------------------------

    def get_health(self, tool_name: str) -> ToolHealth:

        self.register_tool(tool_name)

        return self._health[tool_name]

    # --------------------------------------------------------------

    def get_all_health(self):

        return list(self._health.values())

    # --------------------------------------------------------------

    def reset(self, tool_name: str):

        with self._lock:
            self._health[tool_name] = ToolHealth(tool_name)

    # --------------------------------------------------------------

    def reset_all(self):

        with self._lock:

            for name in list(self._health.keys()):
                self._health[name] = ToolHealth(name)