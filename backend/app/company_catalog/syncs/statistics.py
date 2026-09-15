from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SyncStatistics:
    """
    Statistics collected during a synchronization run.
    """

    processed: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0

    @property
    def successful(self) -> int:
        """
        Total successful operations.
        """
        return self.created + self.updated + self.skipped

    def as_dict(self) -> dict[str, int]:
        """
        Serialize statistics.
        """
        return {
            "processed": self.processed,
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
            "failed": self.failed,
            "successful": self.successful,
        }