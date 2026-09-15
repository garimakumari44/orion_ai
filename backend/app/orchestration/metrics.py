"""
metrics.py

Execution statistics and telemetry for the orchestration layer.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from threading import Lock
from time import perf_counter
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Per Tool Metrics
# ---------------------------------------------------------------------------

@dataclass
class ToolMetrics:
    tool_name: str
    executions: int = 0
    successes: int = 0
    failures: int = 0
    retries: int = 0
    fallbacks: int = 0
    total_latency: float = 0.0

    @property
    def average_latency(self) -> float:
        if self.executions == 0:
            return 0.0
        return self.total_latency / self.executions

    @property
    def success_rate(self) -> float:
        if self.executions == 0:
            return 0.0
        return self.successes / self.executions


# ---------------------------------------------------------------------------
# Metrics Collector
# ---------------------------------------------------------------------------

class MetricsCollector:
    """
    Collects execution telemetry for orchestration.

    Thread-safe.

    Example:

        metrics.execution_started("github")

        ...
        metrics.execution_finished(
            "github",
            success=True,
            latency=0.41
        )
    """

    def __init__(self) -> None:
        self._lock = Lock()

        self.total_executions = 0
        self.total_successes = 0
        self.total_failures = 0
        self.total_retries = 0
        self.total_fallbacks = 0
        self.total_latency = 0.0
        self.active_executions = 0

        self.error_counter = Counter()

        self.tool_metrics: Dict[str, ToolMetrics] = defaultdict(
            lambda: ToolMetrics(tool_name="")
        )

        self._start_times: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def execution_started(self, execution_id: str) -> None:
        with self._lock:
            self.active_executions += 1
            self._start_times[execution_id] = perf_counter()

    def execution_finished(
        self,
        execution_id: str,
        tool_name: str,
        success: bool,
        latency: Optional[float] = None,
        error: Optional[Exception] = None,
    ) -> None:
        with self._lock:

            self.active_executions -= 1
            self.total_executions += 1

            if latency is None:
                start = self._start_times.pop(execution_id, None)
                if start is not None:
                    latency = perf_counter() - start
                else:
                    latency = 0.0
            else:
                self._start_times.pop(execution_id, None)

            self.total_latency += latency

            metrics = self.tool_metrics[tool_name]

            if metrics.tool_name == "":
                metrics.tool_name = tool_name

            metrics.executions += 1
            metrics.total_latency += latency

            if success:
                self.total_successes += 1
                metrics.successes += 1
            else:
                self.total_failures += 1
                metrics.failures += 1

                if error:
                    self.error_counter[type(error).__name__] += 1

    # ------------------------------------------------------------------
    # Retry / Fallback
    # ------------------------------------------------------------------

    def record_retry(self, tool_name: str) -> None:
        with self._lock:
            self.total_retries += 1

            metrics = self.tool_metrics[tool_name]
            if metrics.tool_name == "":
                metrics.tool_name = tool_name

            metrics.retries += 1

    def record_fallback(self, tool_name: str) -> None:
        with self._lock:
            self.total_fallbacks += 1

            metrics = self.tool_metrics[tool_name]
            if metrics.tool_name == "":
                metrics.tool_name = tool_name

            metrics.fallbacks += 1

    # ------------------------------------------------------------------
    # Derived Metrics
    # ------------------------------------------------------------------

    @property
    def average_latency(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.total_latency / self.total_executions

    @property
    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.total_successes / self.total_executions

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def tool_report(self) -> Dict[str, dict]:
        return {
            name: asdict(metrics)
            | {
                "average_latency": metrics.average_latency,
                "success_rate": metrics.success_rate,
            }
            for name, metrics in self.tool_metrics.items()
        }

    def snapshot(self) -> dict:
        return {
            "total_executions": self.total_executions,
            "active_executions": self.active_executions,
            "successes": self.total_successes,
            "failures": self.total_failures,
            "success_rate": self.success_rate,
            "average_latency": self.average_latency,
            "total_retries": self.total_retries,
            "total_fallbacks": self.total_fallbacks,
            "errors": dict(self.error_counter),
            "tools": self.tool_report(),
        }

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def reset(self) -> None:
        with self._lock:
            self.total_executions = 0
            self.total_successes = 0
            self.total_failures = 0
            self.total_retries = 0
            self.total_fallbacks = 0
            self.total_latency = 0.0
            self.active_executions = 0

            self.error_counter.clear()
            self.tool_metrics.clear()
            self._start_times.clear()


# Singleton instance used across orchestration
metrics = MetricsCollector()