"""
Core memory model.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================
# Enums
# ============================================================


class MemoryType(str, Enum):
    """Type of stored memory."""

    CONVERSATION = "conversation"
    RESEARCH = "research"
    PREFERENCE = "preference"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    CACHE = "cache"
    SYSTEM = "system"
    WORKING = "working"

    PROJECT = "project"
    GOAL = "goal"


class MemorySource(str, Enum):
    """Origin of memory."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"
    IMPORT = "import"


# ============================================================
# Content
# ============================================================


class MemoryContent(BaseModel):
    """Actual memory payload."""

    summary: str | None = None

    text: str | None = None

    data: dict[str, Any] = Field(default_factory=dict)

    embedding: list[float] | None = None


# ============================================================
# Metadata
# ============================================================


class MemoryMetadata(BaseModel):
    """Persistent metadata."""

    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    access_count: int = 0

    last_accessed: datetime | None = None

    expires_at: datetime | None = None

    tags: list[str] = Field(default_factory=list)

    namespace: str = "default"

    version: int = 1
    similarity: float = 0.0

    ranking_score: float = 0.0

    boost: float = 0.0


# ============================================================
# Memory
# ============================================================


class Memory(BaseModel):
    """
    Persistent memory object.

    This model only contains information that should
    actually be stored in the memory database.

    Query-specific retrieval information belongs to
    RetrievedMemory or RankedMemory.
    """

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    id: str

    user_id: str | None = None

    type: MemoryType

    source: MemorySource = MemorySource.USER

    # --------------------------------------------------------
    # Content
    # --------------------------------------------------------

    content: MemoryContent

    metadata: MemoryMetadata = Field(default_factory=MemoryMetadata)

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    parent_id: str | None = None

    related_ids: list[str] = Field(default_factory=list)

    # --------------------------------------------------------
    # Persistence
    # --------------------------------------------------------

    persistent_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    archived: bool = False

    # --------------------------------------------------------
    # Time
    # --------------------------------------------------------

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    
    similarity: float | None = Field(
        default=None,
        description="Vector search similarity score"
    )
    boost: float | None = Field(
    default=None,
    description="Ranking boost applied during retrieval"
)
    ranking_score: float | None = Field(
    default=None,
    description="Final ranking score after retrieval and ranking"
)

    # ========================================================
    # Convenience Properties
    # ========================================================

    @property
    def importance(self) -> float:
        return self.metadata.importance

    @importance.setter
    def importance(self, value: float):
        self.metadata.importance = value

    @property
    def confidence(self):
        return self.metadata.confidence

    @confidence.setter
    def confidence(self, value):
        self.metadata.confidence = value

    @property
    def access_count(self):
        return self.metadata.access_count

    @access_count.setter
    def access_count(self, value):
        self.metadata.access_count = value

    @property
    def last_accessed(self):
        return self.metadata.last_accessed

    @last_accessed.setter
    def last_accessed(self, value):
        self.metadata.last_accessed = value

    @property
    def expires_at(self):
        return self.metadata.expires_at

    @expires_at.setter
    def expires_at(self, value):
        self.metadata.expires_at = value

    @property
    def tags(self):
        return self.metadata.tags

    @tags.setter
    def tags(self, value):
        self.metadata.tags = value

    @property
    def namespace(self):
        return self.metadata.namespace

    @namespace.setter
    def namespace(self, value):
        self.metadata.namespace = value

    @property
    def version(self):
        return self.metadata.version

    @version.setter
    def version(self, value):
        self.metadata.version = value

    # ========================================================
    # Helpers
    # ========================================================

    def touch(self):
        """Update access statistics."""

        now = datetime.now(UTC)

        self.metadata.access_count += 1
        self.metadata.last_accessed = now
        self.updated_at = now

    def archive(self):
        """Archive memory."""

        self.archived = True
        self.updated_at = datetime.now(UTC)

    def update_persistent_score(self, score: float):
        """Update long-term memory quality."""

        self.persistent_score = max(0.0, min(1.0, score))
        self.updated_at = datetime.now(UTC)