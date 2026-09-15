# metrics/latency.py

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class LatencyMetric:
    """
    Represents latency measurement for any operation.
    """

    name: str
    start_time: float
    end_time: Optional[float] = None
    metadata: Dict = field(default_factory=dict)

    @property
    def duration_ms(self) -> Optional[float]:
        if self.end_time is None:
            return None

        return round(
            (self.end_time - self.start_time) * 1000,
            2
        )


class LatencyTracker:
    """
    Tracks latency of system components.

    Example:
        with latency.track("llm_call"):
            response = client.chat()

    """

    def __init__(self):
        self.metrics = []


    def start(
        self,
        name: str,
        metadata: Optional[Dict] = None
    ):
        return LatencyMetric(
            name=name,
            start_time=time.perf_counter(),
            metadata=metadata or {}
        )


    def stop(
        self,
        metric: LatencyMetric
    ):

        metric.end_time = time.perf_counter()

        self.metrics.append(metric)

        return metric


    def track(
        self,
        name: str,
        metadata: Optional[Dict] = None
    ):

        tracker = self


        class TimerContext:

            def __enter__(self):

                self.metric = tracker.start(
                    name,
                    metadata
                )

                return self.metric


            def __exit__(
                self,
                exc_type,
                exc,
                traceback
            ):

                tracker.stop(
                    self.metric
                )


        return TimerContext()



    def get_metrics(self):

        return [
            {
                "name": metric.name,
                "latency_ms": metric.duration_ms,
                "metadata": metric.metadata
            }
            for metric in self.metrics
        ]