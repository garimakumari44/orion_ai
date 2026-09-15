from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.research import Research
from app.db.models.saved_artifact import (
    SaveDestination,
    SavedArtifact,
)
from app.schemas.saved_artifact import SavedArtifactCreate


class SavedArtifactService:
    """
    Service for persisting and retrieving saved research artifacts.

    ID types
    --------
    Research.id:
        UUID

    SavedArtifact.id:
        UUID

    Destination values
    ------------------
    library
    research
    reports
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================
    # Create
    # =========================================================

    async def create(
        self,
        payload: SavedArtifactCreate,
    ) -> SavedArtifact:
        """
        Create a saved artifact for an existing research workspace.

        Raises
        ------
        ValueError
            If the referenced research workspace does not exist.
        """

        # -----------------------------------------------------
        # Verify research workspace exists
        # -----------------------------------------------------

        research_query = select(Research.id).where(
            Research.id == payload.research_id
        )

        research_result = await self.db.execute(
            research_query
        )

        research_id = research_result.scalar_one_or_none()

        if research_id is None:
            raise ValueError(
                f"Research with id {payload.research_id} "
                "does not exist"
            )

        # -----------------------------------------------------
        # Normalize destination
        # -----------------------------------------------------

        destination = SaveDestination(
            payload.destination.value
        )

        # -----------------------------------------------------
        # Create artifact
        # -----------------------------------------------------

        artifact = SavedArtifact(
            research_id=research_id,
            destination=destination,
            title=payload.title,
            description=payload.description,
        )

        self.db.add(artifact)

        await self.db.commit()

        await self.db.refresh(artifact)

        return artifact

    # =========================================================
    # List
    # =========================================================

    async def list(
        self,
        destination: SaveDestination | None = None,
        research_id: UUID | None = None,
    ) -> tuple[list[SavedArtifact], int]:
        """
        List saved artifacts with optional filters.

        Research IDs are UUIDs.
        """

        # -----------------------------------------------------
        # Main query
        # -----------------------------------------------------

        query = select(SavedArtifact)

        if destination is not None:
            destination = SaveDestination(
                destination.value
            )

            query = query.where(
                SavedArtifact.destination == destination
            )

        if research_id is not None:
            query = query.where(
                SavedArtifact.research_id == research_id
            )

        query = query.order_by(
            SavedArtifact.created_at.desc()
        )

        result = await self.db.execute(query)

        items = list(
            result.scalars().all()
        )

        # -----------------------------------------------------
        # Count query
        # -----------------------------------------------------

        count_query = select(
            func.count(SavedArtifact.id)
        )

        if destination is not None:
            count_query = count_query.where(
                SavedArtifact.destination == destination
            )

        if research_id is not None:
            count_query = count_query.where(
                SavedArtifact.research_id == research_id
            )

        count_result = await self.db.execute(
            count_query
        )

        total = count_result.scalar_one()

        return items, total

    # =========================================================
    # Get
    # =========================================================

    async def get(
        self,
        artifact_id: UUID,
    ) -> SavedArtifact | None:
        """
        Get a saved artifact by UUID.
        """

        query = select(SavedArtifact).where(
            SavedArtifact.id == artifact_id
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    # =========================================================
    # Delete
    # =========================================================

    async def delete(
        self,
        artifact_id: UUID,
    ) -> bool:
        """
        Delete a saved artifact by UUID.

        Returns
        -------
        bool
            True when an artifact was deleted,
            otherwise False.
        """

        result = await self.db.execute(
            delete(SavedArtifact).where(
                SavedArtifact.id == artifact_id
            )
        )

        await self.db.commit()

        return result.rowcount > 0