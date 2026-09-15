from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SaveDestination(str, enum.Enum):
    LIBRARY = "library"
    RESEARCH = "research"
    REPORTS = "reports"


class SavedArtifact(Base):
    __tablename__ = "saved_artifacts"

    # ---------------------------------------------------------
    # Primary key
    # ---------------------------------------------------------

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ---------------------------------------------------------
    # Research foreign key
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # Research.id is UUID.
    #

    research_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "research.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ---------------------------------------------------------
    # Destination
    # ---------------------------------------------------------

    destination: Mapped[SaveDestination] = mapped_column(
        Enum(
            SaveDestination,
            name="save_destination",
            native_enum=True,
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
        ),
        nullable=False,
        index=True,
    )

    # ---------------------------------------------------------
    # Artifact metadata
    # ---------------------------------------------------------

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ---------------------------------------------------------
    # Timestamps
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Relationship
    # ---------------------------------------------------------

    research = relationship(
        "Research",
        back_populates="saved_artifacts",
    )