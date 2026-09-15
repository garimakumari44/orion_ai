# metrics/throughput.py

import time
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class ThroughputMetric:

    name: str
    count: int
    window_seconds: float


class ThroughputTracker:
    """
    Measures system throughput.

    Examples:
    - requests/minute
    - agent executions/sec
    - tool calls/minute
    """

    def __init__(self):

        self.events = defaultdict(list)


    def record(
        self,
        name: str
    ):

        self.events[name].append(
            time.time()
        )


    def calculate(
        self,
        name: str,
        window_seconds: int = 60
    ):

        now = time.time()

        timestamps = [
            t
            for t in self.events[name]
            if now - t <= window_seconds
        ]


        self.events[name] = timestamps


        return ThroughputMetric(
            name=name,
            count=len(timestamps),
            window_seconds=window_seconds
        )



    def requests_per_second(
        self,
        name: str
    ):

        metric = self.calculate(
            name,
            60
        )


        if metric.window_seconds == 0:
            return 0


        return round(
            metric.count /
            metric.window_seconds,
            4
        )