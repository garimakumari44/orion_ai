"""
Timing and performance utilities.

Used for:
- LLM latency measurement
- Retrieval timing
- Agent execution profiling
- Observability metrics
"""

from __future__ import annotations

import time
import asyncio

from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass, field


@dataclass
class TimerResult:
    """
    Timer result container.
    """

    name: str
    duration: float

    @property
    def milliseconds(self):
        return self.duration * 1000


class Timer:
    """
    Simple execution timer.

    Example:

        with Timer("llm_call"):
            response = client.chat()

    """

    def __init__(
        self,
        name: str = "operation",
    ):
        self.name = name
        self.start_time = None
        self.end_time = None


    def start(self):
        self.start_time = time.perf_counter()


    def stop(self):

        self.end_time = time.perf_counter()

        return TimerResult(
            name=self.name,
            duration=self.elapsed(),
        )


    def elapsed(self):

        if not self.start_time:
            return 0

        end = (
            self.end_time
            or time.perf_counter()
        )

        return end - self.start_time


    def __enter__(self):

        self.start()

        return self


    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ):

        self.stop()



@contextmanager
def measure_time(
    name: str,
):
    """
    Context manager timing helper.

    Example:

        with measure_time("embedding"):
            create_embedding()
    """

    start = time.perf_counter()

    try:
        yield

    finally:

        duration = (
            time.perf_counter()
            - start
        )

        print(
            f"{name}: {duration:.4f}s"
        )



@asynccontextmanager
async def async_measure_time(
    name: str,
):
    """
    Async timing context.

    Example:

        async with async_measure_time("llm"):
            await llm.generate()
    """

    start = time.perf_counter()

    try:
        yield

    finally:

        duration = (
            time.perf_counter()
            - start
        )

        print(
            f"{name}: {duration:.4f}s"
        )



class LatencyTracker:
    """
    Track multiple operation latencies.

    Example:

        tracker.record(
            "retrieval",
            0.25
        )
    """

    def __init__(self):

        self.metrics = {}


    def record(
        self,
        name: str,
        duration: float,
    ):

        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append(
            duration
        )


    def average(
        self,
        name: str,
    ):

        values = self.metrics.get(
            name,
            []
        )

        if not values:
            return 0

        return sum(values) / len(values)


    def latest(
        self,
        name: str,
    ):

        values = self.metrics.get(
            name,
            []
        )

        if not values:
            return 0

        return values[-1]


    def reset(self):

        self.metrics.clear()