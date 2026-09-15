from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.saved_artifact import SaveDestination
from app.db.session import get_db
from app.schemas.saved_artifact import (
    SavedArtifactListResponse,
    SavedArtifactResponse,
)
from app.services.saved_artifact_service import (
    SavedArtifactService,
)


router = APIRouter(
    prefix="/library",
    tags=["Library"],
)


@router.get(
    "",
    response_model=SavedArtifactListResponse,
)
async def list_library(
    research_id: UUID | None = Query(
        default=None,
    ),
    db: AsyncSession = Depends(get_db),
) -> SavedArtifactListResponse:
    """
    Return saved research artifacts belonging to the Library.

    Library is backed by the canonical saved_artifacts table.
    """

    service = SavedArtifactService(db)

    items, total = await service.list(
        destination=SaveDestination.LIBRARY,
        research_id=research_id,
    )

    return SavedArtifactListResponse(
        items=items,
        total=total,
    )


@router.get(
    "/{artifact_id}",
    response_model=SavedArtifactResponse,
)
async def get_library_item(
    artifact_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SavedArtifactResponse:
    """
    Return one Library artifact.

    The artifact must belong to the Library destination.
    """

    service = SavedArtifactService(db)

    artifact = await service.get(artifact_id)

    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library item not found",
        )

    if artifact.destination != SaveDestination.LIBRARY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library item not found",
        )

    return artifact


@router.delete(
    "/{artifact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_library_item(
    artifact_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Remove an artifact from the Library.

    This deletes the saved-artifact record, not the
    underlying Research record.
    """

    service = SavedArtifactService(db)

    artifact = await service.get(artifact_id)

    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library item not found",
        )

    if artifact.destination != SaveDestination.LIBRARY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library item not found",
        )

    deleted = await service.delete(artifact_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library item not found",
        )

    return None