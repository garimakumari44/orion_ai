from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class WorkerStatus(str, Enum):
    """Possible lifecycle states of a worker."""

    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass
class WorkerState:
    """
    Runtime state of a worker.

    This object is managed by the StateManager and used by the
    Scheduler/Dispatcher to determine worker availability.
    """

    worker_id: str
    status: WorkerStatus = WorkerStatus.IDLE

    current_task_id: Optional[str] = None

    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    last_heartbeat: datetime = field(default_factory=datetime.utcnow)

    error_message: Optional[str] = None

    @property
    def is_available(self) -> bool:
        """Returns True if the worker can accept a new task."""
        return self.status == WorkerStatus.IDLE

    @property
    def is_busy(self) -> bool:
        """Returns True if the worker is executing a task."""
        return self.status == WorkerStatus.BUSY

    def assign_task(self, task_id: str) -> None:
        """Assign a task to the worker."""
        self.current_task_id = task_id
        self.status = WorkerStatus.BUSY
        self.started_at = datetime.utcnow()
        self.finished_at = None
        self.error_message = None
        self.touch()

    def complete_task(self) -> None:
        """Mark the current task as completed."""
        self.current_task_id = None
        self.status = WorkerStatus.IDLE
        self.finished_at = datetime.utcnow()
        self.touch()

    def fail(self, error: str) -> None:
        """Mark the worker as failed."""
        self.status = WorkerStatus.FAILED
        self.error_message = error
        self.finished_at = datetime.utcnow()
        self.touch()

    def wait(self) -> None:
        """Place the worker into a waiting state."""
        self.status = WorkerStatus.WAITING
        self.touch()

    def stop(self) -> None:
        """Stop the worker."""
        self.status = WorkerStatus.STOPPED
        self.touch()

    def reset(self) -> None:
        """Reset the worker to an idle state."""
        self.status = WorkerStatus.IDLE
        self.current_task_id = None
        self.started_at = None
        self.finished_at = None
        self.error_message = None
        self.touch()

    def touch(self) -> None:
        """Update the heartbeat timestamp."""
        self.last_heartbeat = datetime.utcnow()