"""
Memory Profiling Module

Tracks memory consumption
for AI applications.

Used for:
- LLM inference monitoring
- Agent memory tracking
- Leak detection
"""


import os
import time
import psutil

from dataclasses import dataclass
from typing import Dict



@dataclass
class MemoryStats:
    """
    Memory metrics container.
    """

    system_used_mb: float
    system_available_mb: float
    process_rss_mb: float
    process_vms_mb: float
    timestamp: float




class MemoryProfiler:
    """
    Memory profiler.

    Example:

        memory = MemoryProfiler()

        print(memory.snapshot())
    """



    def __init__(self):

        self.process = psutil.Process(
            os.getpid()
        )



    def system_memory(self):
        """
        Returns system RAM information.
        """

        return psutil.virtual_memory()



    def process_memory(self):
        """
        Returns current process memory.
        """

        return self.process.memory_info()



    def collect(self) -> MemoryStats:
        """
        Collect memory metrics.
        """

        system = self.system_memory()

        process = self.process_memory()


        return MemoryStats(

            system_used_mb=
                system.used / (1024 ** 2),


            system_available_mb=
                system.available / (1024 ** 2),


            process_rss_mb=
                process.rss / (1024 ** 2),


            process_vms_mb=
                process.vms / (1024 ** 2),


            timestamp=time.time()
        )



    def snapshot(self) -> Dict:
        """
        Export metrics.
        """

        stats = self.collect()


        return {


            "memory": {


                "system_used_mb":
                    round(
                        stats.system_used_mb,
                        2
                    ),


                "system_available_mb":
                    round(
                        stats.system_available_mb,
                        2
                    ),


                "process_rss_mb":
                    round(
                        stats.process_rss_mb,
                        2
                    ),


                "process_vms_mb":
                    round(
                        stats.process_vms_mb,
                        2
                    )

            },


            "timestamp":
                stats.timestamp
        }