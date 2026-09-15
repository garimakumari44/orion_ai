"""
Execution Profiling Module

Measures runtime performance.

Tracks:
- Execution duration
- Success/failure
- Metadata
"""


import time
import traceback

from dataclasses import dataclass
from typing import Dict, Any



@dataclass
class ExecutionStats:

    name: str

    duration_ms: float

    success: bool

    error: str | None

    timestamp: float




class ExecutionProfiler:
    """
    Execution profiler.

    Example:

        profiler = ExecutionProfiler()

        with profiler.track("llm_call"):

            response = model.generate()
    """



    def __init__(self):

        self.records = []



    class Tracker:


        def __init__(
            self,
            profiler,
            name
        ):

            self.profiler = profiler
            self.name = name



        def __enter__(self):

            self.start = time.perf_counter()

            return self



        def __exit__(
            self,
            exc_type,
            exc,
            tb
        ):


            duration = (

                time.perf_counter()
                -
                self.start

            ) * 1000



            self.profiler.records.append(

                ExecutionStats(

                    name=
                        self.name,


                    duration_ms=
                        duration,


                    success=
                        exc is None,


                    error=
                        str(exc)
                        if exc
                        else None,


                    timestamp=
                        time.time()
                )

            )


            return False



    def track(
        self,
        name: str
    ):

        return self.Tracker(
            self,
            name
        )



    def latest(self):

        if not self.records:

            return None


        item = self.records[-1]


        return {


            "operation":
                item.name,


            "duration_ms":
                round(
                    item.duration_ms,
                    2
                ),


            "success":
                item.success,


            "error":
                item.error,


            "timestamp":
                item.timestamp
        }



    def summary(self):

        total = len(
            self.records
        )


        failures = sum(

            1
            for r in self.records
            if not r.success

        )


        avg = (

            sum(
                r.duration_ms
                for r in self.records
            )
            /
            total

            if total
            else 0

        )


        return {

            "total_executions":
                total,


            "failures":
                failures,


            "average_latency_ms":
                round(
                    avg,
                    2
                )

        }