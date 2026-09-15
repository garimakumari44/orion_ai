"""
app/db/models/research.py

Research project persistence model.

A Research represents one research workspace initiated by a user.

Identity
--------
Research.id is a UUID.

Ownership
---------
user_id remains an integer foreign key.

Company / Industry
------------------
Company and industry identifiers remain integers when stored
inside metadata_json / related application services.

Lifecycle
---------
Research stores lightweight lifecycle and execution metadata.

Generated research output is persisted separately in
ResearchResult.
"""

from __future__ import annotations

import uuid

from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.database import Base


class Research(Base):
    """
    Research project.

    One Research represents one research workspace.

    Primary key:
        UUID

    Important:
        company_id and industry_id are NOT the Research primary key.
        They remain application-level integer identifiers where
        applicable.
    """

    __tablename__ = "research"

    # ============================================================
    # Primary Key
    # ============================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ============================================================
    # Ownership
    # ============================================================

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # ============================================================
    # Research Information
    # ============================================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    intent: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    research_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="created",
        nullable=False,
        index=True,
    )

    # ============================================================
    # Research Target
    # ============================================================

    company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    ticker: Mapped[str | None] = mapped_column(
        String(25),
        nullable=True,
        index=True,
    )

    industry: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ============================================================
    # Execution
    # ============================================================

    execution_plan_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # ============================================================
    # Metadata
    # ============================================================

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # ============================================================
    # Timestamps
    # ============================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ============================================================
    # Research Result
    # ============================================================

    result: Mapped["ResearchResult | None"] = relationship(
        "ResearchResult",
        back_populates="research",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # ============================================================
    # Saved Artifacts
    # ============================================================

    saved_artifacts: Mapped[list["SavedArtifact"]] = relationship(
        "SavedArtifact",
        back_populates="research",
        cascade="all, delete-orphan",
    )

    # ============================================================
    # Derived Company ID
    # ============================================================

    @property
    def company_id(self) -> int | None:
        """
        Company ID is stored inside metadata_json.

        This remains an integer because company identifiers are
        separate from the UUID-based Research identifier.
        """

        metadata = self.metadata_json or {}

        value = metadata.get("company_id")

        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            f"<Research "
            f"id={self.id} "
            f"status={self.status} "
            f"title='{self.title}'>"
        )