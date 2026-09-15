"""
monitoring/resource_monitor.py

System resource monitoring.
"""

import os
import psutil
from dataclasses import dataclass


@dataclass
class ResourceMonitor:
    """
    Collects machine and process metrics.
    """


    process = psutil.Process(
        os.getpid()
    )


    def cpu_usage(self):
        """
        System CPU percentage.
        """

        return psutil.cpu_percent(
            interval=0.5
        )


    def memory_usage(self):
        """
        System memory metrics.
        """

        memory = psutil.virtual_memory()

        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent
        }


    def disk_usage(self):
        """
        Disk utilization.
        """

        disk = psutil.disk_usage("/")

        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }


    def process_memory(self):
        """
        Current application memory.
        """

        memory = self.process.memory_info()

        return {
            "rss": memory.rss,
            "vms": memory.vms
        }


    def process_cpu(self):
        """
        CPU consumed by application.
        """

        return self.process.cpu_percent()


    def threads(self):
        """
        Active thread count.
        """

        return self.process.num_threads()


    def collect(self):
        """
        Collect complete resource snapshot.
        """

        return {

            "cpu": {
                "system": self.cpu_usage(),
                "process": self.process_cpu()
            },


            "memory": {
                "system": self.memory_usage(),
                "process": self.process_memory()
            },


            "disk": self.disk_usage(),


            "threads": self.threads()

        }



resource_monitor = ResourceMonitor()