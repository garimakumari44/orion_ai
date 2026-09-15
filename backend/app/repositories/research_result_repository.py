from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.research_result import ResearchResult


class ResearchResultRepository:
    """
    Repository for the canonical persisted research result.

    Invariants:

    - One ResearchResult per research_id.
    - research_results is the canonical result store.
    - Research.metadata_json is not used for final results.

    Important:
    - ResearchResult.id may remain an integer primary key.
    - ResearchResult.research_id is a UUID foreign key.
    """

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db

    # ============================================================
    # Create
    # ============================================================

    async def create(
        self,
        research_result: ResearchResult,
    ) -> ResearchResult:

        if research_result is None:
            raise ValueError(
                "research_result is required."
            )

        self.db.add(research_result)

        await self.db.commit()
        await self.db.refresh(research_result)

        return research_result

    # ============================================================
    # Get By ID
    #
    # result_id is the ResearchResult primary key.
    # Keep this as int if the DB column is integer.
    # ============================================================

    async def get_by_id(
        self,
        result_id: int,
    ) -> ResearchResult | None:

        if result_id is None:
            raise ValueError(
                "result_id is required."
            )

        result = await self.db.execute(
            select(ResearchResult).where(
                ResearchResult.id == int(result_id)
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # Get By Research ID
    #
    # research_id is UUID.
    # ============================================================

    async def get_by_research_id(
        self,
        research_id: UUID,
    ) -> ResearchResult | None:

        if research_id is None:
            raise ValueError(
                "research_id is required."
            )

        result = await self.db.execute(
            select(ResearchResult).where(
                ResearchResult.research_id == research_id
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # Save / Upsert
    # ============================================================

    async def save(
        self,
        research_id: UUID,
        *,
        summary: str | None = None,
        overview: dict[str, Any] | None = None,
        evidence: list[Any] | None = None,
        documents: list[Any] | None = None,
        insights: list[Any] | None = None,
        sections: dict[str, Any] | list[Any] | None = None,
        agent_results: list[Any] | None = None,
        citations: list[Any] | None = None,
    ) -> ResearchResult:
        """
        Create the canonical ResearchResult if it does not exist,
        otherwise update the existing result.

        None means "do not replace this field".

        research_id is the UUID of the parent Research record.
        """

        if research_id is None:
            raise ValueError(
                "research_id is required."
            )

        existing = await self.get_by_research_id(
            research_id
        )

        if existing is None:

            result = ResearchResult(
                research_id=research_id,

                summary=summary,

                overview=(
                    overview
                    if overview is not None
                    else {}
                ),

                evidence=(
                    evidence
                    if evidence is not None
                    else []
                ),

                documents=(
                    documents
                    if documents is not None
                    else []
                ),

                insights=(
                    insights
                    if insights is not None
                    else []
                ),

                sections=(
                    sections
                    if sections is not None
                    else []
                ),

                agent_results=(
                    agent_results
                    if agent_results is not None
                    else []
                ),

                citations=(
                    citations
                    if citations is not None
                    else []
                ),
            )

            return await self.create(result)

        # --------------------------------------------------------
        # Update only supplied fields
        # --------------------------------------------------------

        if summary is not None:
            existing.summary = summary

        if overview is not None:
            existing.overview = overview

        if evidence is not None:
            existing.evidence = evidence

        if documents is not None:
            existing.documents = documents

        if insights is not None:
            existing.insights = insights

        if sections is not None:
            existing.sections = sections

        if agent_results is not None:
            existing.agent_results = agent_results

        if citations is not None:
            existing.citations = citations

        return await self.update(existing)

    # ============================================================
    # Update
    # ============================================================

    async def update(
        self,
        research_result: ResearchResult,
    ) -> ResearchResult:

        if research_result is None:
            raise ValueError(
                "research_result is required."
            )

        await self.db.commit()
        await self.db.refresh(research_result)

        return research_result

    # ============================================================
    # Replace Entire Result
    # ============================================================

    async def replace(
        self,
        research_result: ResearchResult,
        *,
        summary: str | None,
        overview: dict[str, Any],
        evidence: list[Any],
        documents: list[Any],
        insights: list[Any],
        sections: dict[str, Any] | list[Any],
        agent_results: list[Any],
        citations: list[Any],
    ) -> ResearchResult:

        if research_result is None:
            raise ValueError(
                "research_result is required."
            )

        research_result.summary = summary
        research_result.overview = overview
        research_result.evidence = evidence
        research_result.documents = documents
        research_result.insights = insights
        research_result.sections = sections
        research_result.agent_results = agent_results
        research_result.citations = citations

        return await self.update(
            research_result
        )

    # ============================================================
    # Field Updates
    # ============================================================

    async def update_summary(
        self,
        research_result: ResearchResult,
        summary: str | None,
    ) -> ResearchResult:

        research_result.summary = summary

        return await self.update(
            research_result
        )

    async def update_overview(
        self,
        research_result: ResearchResult,
        overview: dict[str, Any],
    ) -> ResearchResult:

        research_result.overview = overview

        return await self.update(
            research_result
        )

    async def update_evidence(
        self,
        research_result: ResearchResult,
        evidence: list[Any],
    ) -> ResearchResult:

        research_result.evidence = evidence

        return await self.update(
            research_result
        )

    async def update_documents(
        self,
        research_result: ResearchResult,
        documents: list[Any],
    ) -> ResearchResult:

        research_result.documents = documents

        return await self.update(
            research_result
        )

    async def update_insights(
        self,
        research_result: ResearchResult,
        insights: list[Any],
    ) -> ResearchResult:

        research_result.insights = insights

        return await self.update(
            research_result
        )

    async def update_sections(
        self,
        research_result: ResearchResult,
        sections: dict[str, Any] | list[Any],
    ) -> ResearchResult:

        research_result.sections = sections

        return await self.update(
            research_result
        )

    async def update_agent_results(
        self,
        research_result: ResearchResult,
        agent_results: list[Any],
    ) -> ResearchResult:

        research_result.agent_results = agent_results

        return await self.update(
            research_result
        )

    async def update_citations(
        self,
        research_result: ResearchResult,
        citations: list[Any],
    ) -> ResearchResult:

        research_result.citations = citations

        return await self.update(
            research_result
        )

    # ============================================================
    # Delete By Result
    # ============================================================

    async def delete(
        self,
        research_result: ResearchResult,
    ) -> None:

        if research_result is None:
            raise ValueError(
                "research_result is required."
            )

        await self.db.delete(
            research_result
        )

        await self.db.commit()

    # ============================================================
    # Delete By Research ID
    # ============================================================

    async def delete_by_research_id(
        self,
        research_id: UUID,
    ) -> None:

        if research_id is None:
            raise ValueError(
                "research_id is required."
            )

        await self.db.execute(
            delete(ResearchResult).where(
                ResearchResult.research_id == research_id
            )
        )

        await self.db.commit()