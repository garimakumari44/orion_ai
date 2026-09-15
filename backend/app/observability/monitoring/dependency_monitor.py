"""
monitoring/dependency_monitor.py

External dependency health monitoring.

Tracks:
- API availability
- Database connectivity
- Service latency
- Dependency failures
"""

import time
import asyncio
from dataclasses import dataclass, field
from typing import Callable, Dict, Any


@dataclass
class DependencyStatus:
    """
    Stores dependency health information.
    """

    name: str

    healthy: bool = False

    latency_ms: float = 0.0

    error_count: int = 0

    last_error: str | None = None

    last_checked: float | None = None



class DependencyMonitor:
    """
    Monitors external system dependencies.
    """


    def __init__(self):

        self.dependencies: Dict[
            str,
            DependencyStatus
        ] = {}



    def register(
        self,
        name: str
    ):
        """
        Register dependency.
        """

        self.dependencies[name] = DependencyStatus(
            name=name
        )



    def check(
        self,
        name: str,
        checker: Callable[[], Any]
    ):
        """
        Execute dependency health check.
        """

        if name not in self.dependencies:
            self.register(name)


        dependency = self.dependencies[name]


        start = time.perf_counter()


        try:

            result = checker()


            latency = (
                time.perf_counter() - start
            ) * 1000


            dependency.healthy = True

            dependency.latency_ms = round(
                latency,
                2
            )

            dependency.last_error = None


        except Exception as error:


            dependency.healthy = False

            dependency.error_count += 1

            dependency.last_error = str(error)



        dependency.last_checked = time.time()


        return dependency



    async def async_check(
        self,
        name: str,
        checker
    ):

        """
        Async dependency check.
        """

        if name not in self.dependencies:
            self.register(name)


        dependency = self.dependencies[name]


        start = time.perf_counter()


        try:

            await checker()


            latency = (
                time.perf_counter() - start
            ) * 1000


            dependency.healthy = True

            dependency.latency_ms = round(
                latency,
                2
            )


            dependency.last_error = None


        except Exception as error:

            dependency.healthy = False

            dependency.error_count += 1

            dependency.last_error = str(error)



        dependency.last_checked = time.time()


        return dependency



    def status(self):
        """
        Return all dependency states.
        """

        return {

            name: {

                "healthy": dependency.healthy,

                "latency_ms": dependency.latency_ms,

                "errors": dependency.error_count,

                "last_error": dependency.last_error,

                "last_checked": dependency.last_checked

            }

            for name, dependency
            in self.dependencies.items()

        }



dependency_monitor = DependencyMonitor()