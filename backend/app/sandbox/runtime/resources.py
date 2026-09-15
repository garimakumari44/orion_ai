"""
Runtime resource limits.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import signal


@dataclass(slots=True)
class ResourceLimits:
    """
    Resource limits for one execution.
    """

    cpu_seconds: int = 30

    memory_mb: int = 2048

    disk_mb: int = 2048

    timeout_seconds: int = 60

    max_processes: int = 10

    max_open_files: int = 128

    max_output_bytes: int = 10 * 1024 * 1024


class ResourceManager:
    """
    Applies runtime resource limits.

    NOTE:
    Most limits require platform-specific support.
    """

    def __init__(self, limits: ResourceLimits):
        self.limits = limits

    def apply(self) -> None:
        """
        Apply supported limits.

        Unix:
            Uses resource module.

        Windows:
            No-op (future Job Object support).
        """

        try:
            import resource
        except ImportError:
            return

        resource.setrlimit(
            resource.RLIMIT_CPU,
            (
                self.limits.cpu_seconds,
                self.limits.cpu_seconds,
            ),
        )

        resource.setrlimit(
            resource.RLIMIT_AS,
            (
                self.limits.memory_mb * 1024 * 1024,
                self.limits.memory_mb * 1024 * 1024,
            ),
        )

        resource.setrlimit(
            resource.RLIMIT_NOFILE,
            (
                self.limits.max_open_files,
                self.limits.max_open_files,
            ),
        )

    def timeout_signal(self):
        """
        Configure timeout alarm (Unix only).
        """

        if hasattr(signal, "alarm"):
            signal.alarm(self.limits.timeout_seconds)