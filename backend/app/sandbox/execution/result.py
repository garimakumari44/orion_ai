"""
Standard execution result models.

Every execution backend (Python, Bash, SQL, Notebook)
returns an ExecutionResult object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Artifact:
    """
    File generated during execution.
    """

    name: str
    path: Path
    mime_type: str | None = None
    size: int | None = None


@dataclass
class ExecutionMetrics:
    """
    Runtime statistics.
    """

    execution_time: float = 0.0
    cpu_time: float = 0.0
    peak_memory_mb: float = 0.0


@dataclass
class ExecutionResult:
    """
    Unified execution response.
    """

    success: bool

    stdout: str = ""
    stderr: str = ""

    exit_code: int = 0

    result: Any | None = None

    artifacts: list[Artifact] = field(default_factory=list)

    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)

    started_at: datetime | None = None
    finished_at: datetime | None = None

    exception: str | None = None
    traceback: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_output(self) -> bool:
        return bool(self.stdout.strip())

    @property
    def has_error(self) -> bool:
        return bool(self.stderr.strip())

    @property
    def duration(self) -> float:
        return self.metrics.execution_time

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "result": self.result,
            "artifacts": [
                {
                    "name": a.name,
                    "path": str(a.path),
                    "mime_type": a.mime_type,
                    "size": a.size,
                }
                for a in self.artifacts
            ],
            "metrics": {
                "execution_time": self.metrics.execution_time,
                "cpu_time": self.metrics.cpu_time,
                "peak_memory_mb": self.metrics.peak_memory_mb,
            },
            "started_at": self.started_at.isoformat()
            if self.started_at
            else None,
            "finished_at": self.finished_at.isoformat()
            if self.finished_at
            else None,
            "exception": self.exception,
            "traceback": self.traceback,
            "metadata": self.metadata,
        }