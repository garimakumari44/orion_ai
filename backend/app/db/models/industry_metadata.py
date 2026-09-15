"""
app/db/models/industry_metadata.py

SQLAlchemy ORM model for normalized industry metadata.

Responsibilities
----------------
- Store normalized metadata associated with an Industry.
- Support multiple metadata records per Industry.
- Preserve metadata provenance through source.
- Support both scalar and structured JSON metadata.

Relationship
------------

Industry
    |
    +--> IndustryMetadata
            |
            +--> key
            +--> value
            +--> value_json
            +--> source
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.industry import Industry


class IndustryMetadata(Base):
    """
    Metadata associated with a canonical Industry.

    One Industry can have many metadata records.

    Examples
    --------
    key = "market_size"
    value = "$500B"

    key = "growth_rate"
    value = "8.5%"

    key = "characteristics"
    value_json = {
        "cyclical": False,
        "capital_intensive": True,
    }
    """

    __tablename__ = "industry_metadata"

    __table_args__ = (
        Index(
            "ix_industry_metadata_industry_id",
            "industry_id",
        ),
        Index(
            "ix_industry_metadata_key",
            "key",
        ),
        Index(
            "ix_industry_metadata_source",
            "source",
        ),
    )

    # ============================================================
    # Identity
    # ============================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # ============================================================
    # Industry relationship
    # ============================================================

    industry_id: Mapped[int] = mapped_column(
        ForeignKey(
            "industries.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=False,
    )

    industry: Mapped["Industry"] = relationship(
        "Industry",
        back_populates="metadata_records",
    )

    # ============================================================
    # Metadata key
    # ============================================================

    key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ============================================================
    # Scalar metadata value
    # ============================================================

    value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # Structured metadata value
    # ============================================================

    value_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # ============================================================
    # Metadata provenance
    # ============================================================

    source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ============================================================
    # Timestamps
    # ============================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            f"<IndustryMetadata("
            f"id={self.id!r}, "
            f"industry_id={self.industry_id!r}, "
            f"key={self.key!r}"
            f")>"
        )