"""
monitoring/uptime.py

Service uptime tracking and availability monitoring.
"""

import time
import datetime
from dataclasses import dataclass, field


@dataclass
class UptimeMonitor:
    """
    Tracks application uptime.
    """

    start_time: float = field(default_factory=time.time)
    restart_count: int = 0


    def uptime_seconds(self) -> float:
        """
        Returns uptime in seconds.
        """

        return time.time() - self.start_time


    def uptime_readable(self) -> str:
        """
        Human readable uptime.
        """

        seconds = int(self.uptime_seconds())

        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        return (
            f"{days}d "
            f"{hours}h "
            f"{minutes}m "
            f"{seconds}s"
        )


    def started_at(self) -> str:
        """
        Returns startup timestamp.
        """

        return datetime.datetime.fromtimestamp(
            self.start_time
        ).isoformat()


    def restart(self):
        """
        Record service restart.
        """

        self.restart_count += 1
        self.start_time = time.time()


    def status(self):
        """
        Current uptime status.
        """

        return {
            "started_at": self.started_at(),
            "uptime_seconds": self.uptime_seconds(),
            "uptime": self.uptime_readable(),
            "restart_count": self.restart_count,
            "status": "running"
        }



# Singleton monitor

uptime_monitor = UptimeMonitor()