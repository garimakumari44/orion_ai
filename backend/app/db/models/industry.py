"""
app/db/models/industry.py

Canonical Industry database model.

Responsibilities
----------------
- Store canonical industry classifications.
- Provide a stable industry identity.
- Support industry catalog and research services.
- Store normalized industry metadata.
- Support hierarchical industry relationships.
- Store optional external classification identifiers.

Architecture
------------

IndustryCatalogService
        |
        v
IndustryCatalogRepository
        |
        v
Industry
        |
        +--> IndustryMetadata
        |
        +--> IndustryClassificationSource

IMPORTANT
---------

Industry is NOT the same as sector.

    sector != industry

The `sector` field is retained only as optional external/
classification metadata. It must never be used as a substitute
for the canonical industry identity.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.industry_classification_source import (
        IndustryClassificationSource,
    )
    from app.db.models.industry_metadata import IndustryMetadata


class Industry(Base):
    """
    Canonical industry classification record.

    Examples
    --------
    - Software
    - Semiconductors
    - Aerospace & Defense
    - Biotechnology
    - Banks
    - Oil & Gas

    An industry may optionally belong to a parent industry,
    allowing hierarchical classifications.

    Canonical identity
    ------------------

    code
        Stable internal industry identifier.

    name
        Human-readable canonical industry name.

    slug
        URL-safe normalized identifier.

    Hierarchy
    ---------

    parent_id optionally points to another Industry.

    level=0
        Top-level industry.

    level>0
        Child/sub-industry.

    Sector
    ------

    `sector` is deliberately stored separately.

    It MUST NOT be used by application services as a fallback
    for `industry`.
    """

    __tablename__ = "industries"

    __table_args__ = (
        UniqueConstraint(
            "code",
            name="uq_industries_code",
        ),
        UniqueConstraint(
            "slug",
            name="uq_industries_slug",
        ),
        CheckConstraint(
            "level >= 0",
            name="ck_industries_level_nonnegative",
        ),
        Index(
            "ix_industries_name",
            "name",
        ),
        Index(
            "ix_industries_parent_id",
            "parent_id",
        ),
        Index(
            "ix_industries_active",
            "is_active",
        ),
        Index(
            "ix_industries_sic_code",
            "sic_code",
        ),
        Index(
            "ix_industries_naics_code",
            "naics_code",
        ),
        Index(
            "ix_industries_gics_code",
            "gics_code",
        ),
        Index(
            "ix_industries_icb_code",
            "icb_code",
        ),
        Index(
            "ix_industries_sector",
            "sector",
        ),
    )

    # ========================================================
    # Identity
    # ========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Canonical internal industry code.",
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Canonical industry name.",
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="URL-safe normalized industry identifier.",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ========================================================
    # Classification hierarchy
    # ========================================================

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "industries.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment=(
            "Hierarchy depth. "
            "0 represents a top-level industry."
        ),
    )

    # ========================================================
    # External classification identifiers
    # ========================================================

    sic_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    naics_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    gics_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    icb_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # ========================================================
    # Sector
    # ========================================================

    sector: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment=(
            "Optional external sector classification. "
            "Sector is not the canonical industry identity."
        ),
    )

    # ========================================================
    # Normalized metadata
    # ========================================================

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        nullable=False,
        default=dict,
        server_default="{}",
        comment=(
            "Normalized industry metadata. "
            "Must not replace canonical industry fields."
        ),
    )

    # ========================================================
    # Status
    # ========================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # ========================================================
    # Timestamps
    # ========================================================

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

    # ========================================================
    # Self-referencing hierarchy
    # ========================================================

    parent: Mapped["Industry | None"] = relationship(
        "Industry",
        back_populates="children",
        remote_side="Industry.id",
        foreign_keys="Industry.parent_id",
    )

    children: Mapped[list["Industry"]] = relationship(
        "Industry",
        back_populates="parent",
        foreign_keys="Industry.parent_id",
        passive_deletes=True,
    )

    # ========================================================
    # Industry metadata records
    # ========================================================

    metadata_records: Mapped[
        list["IndustryMetadata"]
    ] = relationship(
        "IndustryMetadata",
        back_populates="industry",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ========================================================
    # Classification sources
    # ========================================================

    classification_sources: Mapped[
        list["IndustryClassificationSource"]
    ] = relationship(
        "IndustryClassificationSource",
        back_populates="industry",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            f"<Industry("
            f"id={self.id!r}, "
            f"code={self.code!r}, "
            f"name={self.name!r}, "
            f"slug={self.slug!r}, "
            f"parent_id={self.parent_id!r}, "
            f"level={self.level!r}, "
            f"is_active={self.is_active!r}"
            f")>"
        )