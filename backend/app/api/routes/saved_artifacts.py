from __future__ import annotations

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.saved_artifact import SaveDestination
from app.db.session import get_db
from app.schemas.saved_artifact import (
    SavedArtifactCreate,
    SavedArtifactListResponse,
    SavedArtifactResponse,
)
from app.services.saved_artifact_service import (
    SavedArtifactService,
)


router = APIRouter(
    prefix="/saved-artifacts",
    tags=["Saved Artifacts"],
)


# =============================================================
# Create
# =============================================================

@router.post(
    "",
    response_model=SavedArtifactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_saved_artifact(
    payload: SavedArtifactCreate,
    db: AsyncSession = Depends(get_db),
):
    service = SavedArtifactService(db)

    try:
        artifact = await service.create(payload)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return artifact


# =============================================================
# List
# =============================================================

@router.get(
    "",
    response_model=SavedArtifactListResponse,
)
async def list_saved_artifacts(
    destination: SaveDestination | None = Query(
        default=None,
    ),
    research_id: UUID | None = Query(
        default=None,
    ),
    db: AsyncSession = Depends(get_db),
):
    service = SavedArtifactService(db)

    items, total = await service.list(
        destination=destination,
        research_id=research_id,
    )

    return SavedArtifactListResponse(
        items=items,
        total=total,
    )


# =============================================================
# Get
# =============================================================

@router.get(
    "/{artifact_id}",
    response_model=SavedArtifactResponse,
)
async def get_saved_artifact(
    artifact_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = SavedArtifactService(db)

    artifact = await service.get(
        artifact_id
    )

    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved artifact not found",
        )

    return artifact


# =============================================================
# Delete
# =============================================================

@router.delete(
    "/{artifact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_saved_artifact(
    artifact_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = SavedArtifactService(db)

    deleted = await service.delete(
        artifact_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved artifact not found",
        )

    return None