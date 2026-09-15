from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class TaskResult:
    """
    Result of executing a single task.

    Produced by the Worker after delegating execution
    to the AgentManager.

    This is the canonical execution result exchanged
    throughout the execution layer.
    """

    task_id: str

    success: bool

    execution_id: Optional[str] = None

    trace_id: Optional[str] = None

    output: Any = None

    error: Optional[str] = None

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """
        Execution duration in seconds.
        """
        if self.started_at and self.completed_at:
            return (
                self.completed_at - self.started_at
            ).total_seconds()

        return None