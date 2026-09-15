"""
CPU Profiling Module

Tracks:
- System CPU usage
- Process CPU usage
- CPU count
- Load information

Used by:
- Observability Manager
- Resource Monitor
- Alert System
"""


import os
import time
import psutil
from dataclasses import dataclass
from typing import Dict


@dataclass
class CPUStats:
    """
    CPU metric container.
    """

    system_usage: float
    process_usage: float
    cpu_count: int
    timestamp: float



class CPUProfiler:
    """
    CPU profiler for AI services.

    Example:
        profiler = CPUProfiler()

        stats = profiler.collect()

        print(stats)
    """


    def __init__(self):
        self.process = psutil.Process(os.getpid())


    def system_cpu_usage(self) -> float:
        """
        Returns total machine CPU usage percentage.
        """

        return psutil.cpu_percent(
            interval=1
        )


    def process_cpu_usage(self) -> float:
        """
        Returns current process CPU usage.
        """

        return self.process.cpu_percent(
            interval=0.1
        )


    def cpu_count(self) -> int:
        """
        Returns available CPU cores.
        """

        return psutil.cpu_count(
            logical=True
        )


    def load_average(self):
        """
        Returns system load.

        Not available on Windows.
        """

        try:
            return os.getloadavg()

        except AttributeError:
            return None



    def collect(self) -> CPUStats:
        """
        Collect complete CPU metrics.
        """

        return CPUStats(

            system_usage=self.system_cpu_usage(),

            process_usage=self.process_cpu_usage(),

            cpu_count=self.cpu_count(),

            timestamp=time.time()
        )



    def snapshot(self) -> Dict:
        """
        Dictionary format for logging/exporting.
        """

        stats = self.collect()


        return {

            "cpu": {

                "system_usage":
                    stats.system_usage,

                "process_usage":
                    stats.process_usage,

                "cores":
                    stats.cpu_count,

            },

            "timestamp":
                stats.timestamp
        }