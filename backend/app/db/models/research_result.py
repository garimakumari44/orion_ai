"""
app/db/models/research_result.py

Persistent storage model for completed research output.

A ResearchResult represents the canonical generated output
of one Research execution.

Research.id:
    UUID

ResearchResult.id:
    Integer

ResearchResult.research_id:
    UUID foreign key -> research.id
"""

from __future__ import annotations

import uuid

from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.database import Base


class ResearchResult(Base):
    """
    Final persisted output of a research execution.

    There is exactly one canonical ResearchResult for each
    Research project.
    """

    __tablename__ = "research_results"

    __table_args__ = (
        UniqueConstraint(
            "research_id",
            name="uq_research_results_research_id",
        ),
    )

    # ============================================================
    # Primary Key
    # ============================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ============================================================
    # Research Relationship
    #
    # IMPORTANT:
    # research.id is UUID, therefore this MUST also be UUID.
    # ============================================================

    research_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "research.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    research: Mapped["Research"] = relationship(
        "Research",
        back_populates="result",
        lazy="select",
    )

    # ============================================================
    # Executive Summary
    # ============================================================

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # Research Overview
    # ============================================================

    overview: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    # ============================================================
    # Evidence
    # ============================================================

    evidence: Mapped[list[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # ============================================================
    # Documents
    # ============================================================

    documents: Mapped[list[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # ============================================================
    # Insights
    # ============================================================

    insights: Mapped[list[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # ============================================================
    # Report Sections
    # ============================================================

    sections: Mapped[dict[str, Any] | list[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # ============================================================
    # Raw Agent Results
    # ============================================================

    agent_results: Mapped[list[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # ============================================================
    # Citations
    # ============================================================

    citations: Mapped[list[Any]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # ============================================================
    # Timestamp
    # ============================================================

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            f"<ResearchResult "
            f"id={self.id} "
            f"research_id={self.research_id}>"
        )