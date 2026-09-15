"""
Research memory models.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResearchStatus(str, Enum):
    """Research lifecycle."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchSource(BaseModel):
    """
    Source used during research.
    """

    title: str

    url: str | None = None

    source_type: str = "web"

    author: str | None = None

    published_at: datetime | None = None

    score: float = 0.0

    metadata: dict[str, Any] = Field(default_factory=dict)


class ResearchFinding(BaseModel):
    """
    Important finding extracted during research.
    """

    title: str

    summary: str

    evidence: list[str] = Field(default_factory=list)

    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    metadata: dict[str, Any] = Field(default_factory=dict)


class ResearchMemory(BaseModel):
    """
    Stores completed research sessions for future retrieval.
    """

    id: str

    user_id: str | None = None

    query: str

    objective: str | None = None

    status: ResearchStatus = ResearchStatus.PENDING

    summary: str | None = None

    findings: list[ResearchFinding] = Field(default_factory=list)

    sources: list[ResearchSource] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    completed_at: datetime | None = None

    @property
    def source_count(self) -> int:
        """Number of sources used."""
        return len(self.sources)

    @property
    def finding_count(self) -> int:
        """Number of extracted findings."""
        return len(self.findings)

    def add_source(self, source: ResearchSource) -> None:
        """Add a research source."""
        self.sources.append(source)

    def add_finding(self, finding: ResearchFinding) -> None:
        """Add an extracted finding."""
        self.findings.append(finding)

    def complete(self, summary: str | None = None) -> None:
        """Mark the research session as completed."""
        self.status = ResearchStatus.COMPLETED
        self.completed_at = datetime.utcnow()

        if summary:
            self.summary = summary