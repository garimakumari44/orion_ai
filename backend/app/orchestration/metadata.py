"""
Common metadata models used throughout the orchestration layer.

Every task, tool execution, and execution result can carry Metadata,
providing tracing, auditing, prioritization, and execution context.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ============================================================
# Metadata Source
# ============================================================

class MetadataSource(str, Enum):
    USER = "user"
    PLANNER = "planner"
    EXECUTOR = "executor"
    TOOL = "tool"
    SYSTEM = "system"


# ============================================================
# Priority
# ============================================================

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================
# Metadata
# ============================================================

class Metadata(BaseModel):
    """
    Shared metadata attached to orchestration objects.
    """

    # Unique identifier

    id: str = Field(default_factory=lambda: str(uuid4()))

    # Workflow identifiers

    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    parent_task_id: Optional[str] = None

    # Source of this object

    source: MetadataSource = MetadataSource.SYSTEM

    # Execution priority

    priority: Priority = Priority.NORMAL

    # Retry information

    retry_count: int = 0

    # Arbitrary labels

    tags: List[str] = Field(default_factory=list)

    # Extra information

    attributes: Dict[str, str] = Field(default_factory=dict)

    # Timestamps

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }

    def touch(self) -> None:
        """
        Update modification timestamp.
        """
        self.updated_at = datetime.now(timezone.utc)

    def increment_retry(self) -> None:
        """
        Increase retry count.
        """
        self.retry_count += 1
        self.touch()

    def add_tag(self, tag: str) -> None:
        """
        Add a tag if it doesn't already exist.
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag if present.
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.touch()

    def set_attribute(self, key: str, value: str) -> None:
        """
        Add or update an attribute.
        """
        self.attributes[key] = value
        self.touch()

    def remove_attribute(self, key: str) -> None:
        """
        Remove an attribute.
        """
        if key in self.attributes:
            del self.attributes[key]
            self.touch()