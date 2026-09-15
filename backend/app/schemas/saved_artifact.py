from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.saved_artifact import SaveDestination


class SavedArtifactCreate(BaseModel):
    """
    Request body for creating a saved artifact.

    Research.id is a UUID, so research_id must be a UUID.
    """

    research_id: UUID

    destination: SaveDestination

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )

    description: str | None = None


class SavedArtifactResponse(BaseModel):
    """
    Response returned for a saved artifact.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    research_id: UUID

    destination: SaveDestination

    title: str

    description: str | None

    created_at: datetime

    updated_at: datetime | None = None


class SavedArtifactListResponse(BaseModel):
    """
    Response returned when listing saved artifacts.
    """

    items: list[SavedArtifactResponse]

    total: int