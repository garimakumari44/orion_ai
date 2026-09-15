"""
Version tracking models.

Supports document history, rollback,
diff tracking, and audit trails.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field

from .base import BaseModel


class ChangeType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    MERGED = "merged"
    SPLIT = "split"
    IMPORTED = "imported"
    RESTORED = "restored"


class Version(BaseModel):
    """
    Single document version.
    """

    version: int

    created_at: datetime = Field(default_factory=datetime.utcnow)

    author: Optional[str] = None

    message: Optional[str] = None

    checksum: Optional[str] = None

    metadata: Dict[str, str] = Field(default_factory=dict)


class Change(BaseModel):
    """
    One change event.
    """

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    change_type: ChangeType

    user: Optional[str] = None

    description: Optional[str] = None

    previous_version: Optional[int] = None

    new_version: Optional[int] = None


class VersionHistory(BaseModel):
    """
    Full version history for a document.
    """

    document_id: str

    current_version: int = 1

    versions: List[Version] = Field(default_factory=list)

    changes: List[Change] = Field(default_factory=list)

    def latest(self) -> Optional[Version]:

        if not self.versions:
            return None

        return max(
            self.versions,
            key=lambda v: v.version,
        )

    def get(self, version: int) -> Optional[Version]:

        for item in self.versions:
            if item.version == version:
                return item

        return None

    def add_version(
        self,
        author: Optional[str] = None,
        message: Optional[str] = None,
        checksum: Optional[str] = None,
    ) -> Version:

        version = Version(
            version=self.current_version,
            author=author,
            message=message,
            checksum=checksum,
        )

        self.versions.append(version)

        self.changes.append(
            Change(
                change_type=ChangeType.UPDATED,
                user=author,
                new_version=self.current_version,
                previous_version=self.current_version - 1,
                description=message,
            )
        )

        self.current_version += 1

        return version

    def rollback(self, version: int) -> bool:

        if self.get(version) is None:
            return False

        self.current_version = version

        self.changes.append(
            Change(
                change_type=ChangeType.RESTORED,
                previous_version=self.latest().version if self.latest() else None,
                new_version=version,
                description=f"Rollback to version {version}",
            )
        )

        return True

    @property
    def total_versions(self) -> int:
        return len(self.versions)

    @property
    def total_changes(self) -> int:
        return len(self.changes)