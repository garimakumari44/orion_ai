from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Company(Base):
    """
    Canonical company identity record.

    A Company represents the stable identity of a public/private
    company used throughout the research system.

    External providers may enrich this record with additional
    metadata, but the database model remains provider-neutral.
    """

    __tablename__ = "companies"

    # =========================================================
    # Primary Identity
    # =========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    legal_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    # =========================================================
    # Market Identity
    # =========================================================

    ticker: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
    )

    exchange: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    # =========================================================
    # Regulatory / Global Identifiers
    # =========================================================

    cik: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
    )

    lei: Mapped[Optional[str]] = mapped_column(
        String(25),
        unique=True,
        nullable=True,
        index=True,
    )

    figi: Mapped[Optional[str]] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
    )

    isin: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
    )

    # =========================================================
    # Classification
    # =========================================================

    sector: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    industry: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    sub_industry: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    # =========================================================
    # Geography
    # =========================================================

    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    headquarters: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    founded_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # =========================================================
    # Company Profile
    # =========================================================

    website: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    logo_url: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )

    # =========================================================
    # Search
    # =========================================================

    search_aliases: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Comma-separated aliases for search.",
    )

    # =========================================================
    # Status
    # =========================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        server_default="true",
        index=True,
    )

    # =========================================================
    # Audit
    # =========================================================

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

    # =========================================================
    # Representation
    # =========================================================

    def __repr__(self) -> str:
        return (
            f"<Company("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"ticker='{self.ticker}'"
            f")>"
        )