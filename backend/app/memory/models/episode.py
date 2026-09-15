"""
Episode models.

An episode represents a sequence of related events that should be
stored together in episodic memory.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EpisodeStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class EpisodeStep(BaseModel):
    """
    Single step inside an episode.
    """

    id: str

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    action: str

    observation: str | None = None

    result: Any = None

    metadata: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Episode(BaseModel):
    """
    Episodic memory object.

    Example:
        User asks to research OpenAI.
        Search happens.
        Documents retrieved.
        Report generated.

    Entire workflow becomes one episode.
    """

    id: str

    title: str

    description: str | None = None

    user_id: str | None = None

    status: EpisodeStatus = EpisodeStatus.ACTIVE

    steps: list[EpisodeStep] = Field(default_factory=list)

    summary: str | None = None

    tags: list[str] = Field(default_factory=list)

    related_memory_ids: list[str] = Field(default_factory=list)

    started_at: datetime = Field(default_factory=datetime.utcnow)

    completed_at: datetime | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def step_count(self) -> int:
        """Return the number of recorded steps."""
        return len(self.steps)

    def add_step(self, step: EpisodeStep) -> None:
        """Append a new step to the episode."""
        self.steps.append(step)

    def complete(self, summary: str | None = None) -> None:
        """Mark the episode as completed."""
        self.status = EpisodeStatus.COMPLETED
        self.completed_at = datetime.utcnow()

        if summary:
            self.summary = summary