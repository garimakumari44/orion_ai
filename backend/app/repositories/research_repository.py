from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.research import Research


class ResearchRepository:
    """
    Repository for Research projects.

    Research.id is a UUID.

    Responsibilities:
    - Persist research projects
    - Retrieve research projects
    - Update project status
    - Store execution metadata

    Does NOT:
    - Parse requests
    - Build execution plans
    - Execute agents
    """

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db

    # =====================================================
    # Create Research
    # =====================================================

    async def create(
        self,
        research: Research,
    ) -> Research:

        self.db.add(research)

        await self.db.commit()

        await self.db.refresh(research)

        return research

    # =====================================================
    # Get By ID
    # =====================================================

    async def get_by_id(
        self,
        research_id: UUID,
    ) -> Research | None:

        if research_id is None:
            raise ValueError(
                "research_id is required."
            )

        result = await self.db.execute(
            select(Research).where(
                Research.id == research_id
            )
        )

        return result.scalar_one_or_none()

    # =====================================================
    # List Research
    # =====================================================

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> Sequence[Research]:

        result = await self.db.execute(
            select(Research)
            .order_by(Research.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()

    # =====================================================
    # Update Status
    # =====================================================

    async def update_status(
        self,
        research: Research,
        status: str,
    ) -> Research:

        research.status = status

        await self.db.commit()

        await self.db.refresh(research)

        return research

    # =====================================================
    # Save Execution Plan
    # =====================================================

    async def save_execution_plan(
        self,
        research: Research,
        execution_plan_id: str,
    ) -> Research:

        research.execution_plan_id = execution_plan_id

        await self.db.commit()

        await self.db.refresh(research)

        return research

    # =====================================================
    # Update Metadata
    # =====================================================

    async def update_metadata(
        self,
        research: Research,
        metadata: dict,
    ) -> Research:

        research.metadata_json = metadata

        await self.db.commit()

        await self.db.refresh(research)

        return research

    # =====================================================
    # Delete
    # =====================================================

    async def delete(
        self,
        research: Research,
    ) -> None:

        await self.db.delete(research)

        await self.db.commit()