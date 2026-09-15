import time
from typing import Callable, Any, Dict
from functools import wraps


class LatencyTracker:
    """
    Tracks execution latency of system components.
    """

    def __init__(self):
        self.records = []


    def measure(
        self,
        name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function and record latency.
        """

        start = time.perf_counter()

        result = func(
            *args,
            **kwargs
        )

        end = time.perf_counter()


        latency = (
            end - start
        )


        self.records.append(
            {
                "component": name,
                "latency_ms": latency * 1000
            }
        )

        return result



    def get_metrics(self) -> Dict:
        """
        Return latency statistics.
        """

        if not self.records:
            return {}


        values = [
            x["latency_ms"]
            for x in self.records
        ]


        return {
            "count": len(values),
            "avg_ms": sum(values) / len(values),
            "min_ms": min(values),
            "max_ms": max(values)
        }



def track_latency(name: str):
    """
    Decorator for latency tracking.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            start = time.perf_counter()


            result = func(
                *args,
                **kwargs
            )


            latency = (
                time.perf_counter()
                - start
            )


            print(
                f"{name}: "
                f"{latency*1000:.2f}ms"
            )


            return result

        return wrapper

    return decorator