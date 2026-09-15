"""
app/db/models/industry_classification_source.py

SQLAlchemy ORM model for external industry classification sources.

Responsibilities
----------------
- Store external industry classification information.
- Associate external classifications with canonical Industry records.
- Support classification systems such as:
    - SIC
    - NAICS
    - GICS
    - ICB
    - Yahoo
    - Web
- Preserve external classification codes and descriptions.

Relationship
------------

Industry
    |
    +--> IndustryClassificationSource
            |
            +--> classification_system
            +--> code
            +--> name
            +--> description
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.industry import Industry


class IndustryClassificationSource(Base):
    """
    External classification information associated with an Industry.

    Examples
    --------
    classification_system = "SIC"
    code = "7372"

    classification_system = "NAICS"
    code = "511210"

    classification_system = "GICS"
    code = "45102010"

    classification_system = "ICB"
    code = "9533"

    classification_system = "Yahoo"
    code = "software"

    classification_system = "Web"
    code = "software-industry"
    """

    __tablename__ = "industry_classification_sources"

    __table_args__ = (
        UniqueConstraint(
            "industry_id",
            "classification_system",
            "code",
            name="uq_industry_classification_source",
        ),
        Index(
            "ix_industry_classification_sources_industry_id",
            "industry_id",
        ),
        Index(
            "ix_industry_classification_sources_system",
            "classification_system",
        ),
        Index(
            "ix_industry_classification_sources_code",
            "code",
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
    )

    industry: Mapped["Industry"] = relationship(
        "Industry",
        back_populates="classification_sources",
    )

    # ============================================================
    # Classification
    # ============================================================

    classification_system: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ============================================================
    # Timestamp
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
            f"<IndustryClassificationSource("
            f"id={self.id!r}, "
            f"industry_id={self.industry_id!r}, "
            f"system={self.classification_system!r}, "
            f"code={self.code!r}"
            f")>"
        )