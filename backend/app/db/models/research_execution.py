from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.database import Base



class ResearchExecution(Base):

    __tablename__ = "research_execution"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )


    research_id: Mapped[int] = mapped_column(
        ForeignKey(
            "research.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )


    current_agent: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


    current_task: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    state: Mapped[str] = mapped_column(
        String(50),
        default="created",
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )