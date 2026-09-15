"""
Timing utilities for observability.

Used for measuring:

- LLM latency
- Retrieval latency
- Agent execution time
- Tool execution duration
"""

import time
import asyncio
import functools
from contextlib import contextmanager


class Timer:
    """
    Simple execution timer.
    """


    def __init__(self):

        self.start_time = None
        self.end_time = None
        self.duration = None



    def start(self):

        self.start_time = time.perf_counter()

        return self



    def stop(self):

        self.end_time = time.perf_counter()

        self.duration = (
            self.end_time -
            self.start_time
        )

        return self.duration



    def elapsed(self):

        if self.start_time is None:
            return 0

        return time.perf_counter() - self.start_time



@contextmanager
def timer():

    """
    Context manager.

    Example:

    with timer() as t:
        process()

    print(t.duration)
    """

    t = Timer()

    t.start()

    try:
        yield t

    finally:
        t.stop()



def measure_time(func):
    """
    Decorator for synchronous functions.

    Example:

    @measure_time
    def retrieve():
        pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        start = time.perf_counter()

        result = func(*args, **kwargs)

        duration = (
            time.perf_counter()
            - start
        )

        return {
            "result": result,
            "latency_ms": duration * 1000
        }


    return wrapper



def async_measure_time(func):
    """
    Decorator for async functions.

    Used for:

    - LLM calls
    - API requests
    - Agent execution
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):

        start = time.perf_counter()

        result = await func(
            *args,
            **kwargs
        )

        duration = (
            time.perf_counter()
            - start
        )


        return {
            "result": result,
            "latency_ms": duration * 1000
        }


    return wrapper



class LatencyTracker:
    """
    Collect latency statistics.
    """


    def __init__(self):

        self.samples = []



    def record(self, latency_ms: float):

        self.samples.append(
            latency_ms
        )



    def count(self):

        return len(self.samples)



    def average(self):

        if not self.samples:
            return 0

        return sum(self.samples) / len(self.samples)



    def max_latency(self):

        if not self.samples:
            return 0

        return max(self.samples)



    def min_latency(self):

        if not self.samples:
            return 0

        return min(self.samples)



    def summary(self):

        return {

            "count": self.count(),

            "avg_ms": self.average(),

            "max_ms": self.max_latency(),

            "min_ms": self.min_latency()
        }