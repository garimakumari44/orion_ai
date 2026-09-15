"""
app/api/research/companies/search.py

Company research/search API.

Responsibilities
----------------
- Search companies through the canonical CompanySearchService.
- Use request-scoped database sessions.
- Reuse application-global company catalog infrastructure.
- Return normalized company search responses.
- Retrieve individual companies by database ID.

Architecture
------------

Application startup
        |
        v
CompanyProviderManager
CompanyDeduplicator
CompanyProcessingPipeline
        |
        v
app.state
        |
        v
Request
        |
        v
get_company_search_service()
        |
        +--> CompanyRepository(request-scoped)
        |
        +--> canonical CompanyProviderManager
        |
        +--> canonical CompanyProcessingPipeline
        |
        v
CompanySearchService
"""

from __future__ import annotations

import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.company_catalog.services.company_search_service import (
    CompanySearchService,
)

from app.db.models.company import Company

from app.db.session import get_db

from app.repositories.company_repository import (
    CompanyRepository,
)

from app.schemas.company import (
    CompanyResponse,
    CompanySearchResponse,
)


logger = logging.getLogger(__name__)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/research/companies",
    tags=["Research - Companies"],
)


# =========================================================
# DEPENDENCIES
# =========================================================

def get_company_search_service(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> CompanySearchService:
    """
    Build a request-scoped CompanySearchService.

    IMPORTANT
    ---------
    The CompanyRepository is request-scoped because it uses the
    current AsyncSession.

    The following objects are application-global and MUST be
    retrieved from app.state:

        - company_provider_manager
        - company_deduplicator
        - company_processing_pipeline

    Do NOT instantiate CompanyProviderManager() here.

    Creating a new CompanyProviderManager() would create an empty
    provider registry and would cause:

        Company provider search requested but no providers
        are registered

    The canonical provider manager is created once in main.py
    during application startup.
    """

    # ---------------------------------------------------------
    # Request-scoped repository
    # ---------------------------------------------------------

    repository = CompanyRepository(
        db=db,
    )

    # ---------------------------------------------------------
    # Application-global company infrastructure
    # ---------------------------------------------------------

    try:
        provider_manager = (
            request.app.state.company_provider_manager
        )
    except AttributeError as exc:
        logger.exception(
            "Canonical CompanyProviderManager is missing "
            "from app.state."
        )

        raise RuntimeError(
            "CompanyProviderManager has not been initialized. "
            "Check application startup."
        ) from exc

    try:
        deduplicator = (
            request.app.state.company_deduplicator
        )
    except AttributeError as exc:
        logger.exception(
            "Canonical CompanyDeduplicator is missing "
            "from app.state."
        )

        raise RuntimeError(
            "CompanyDeduplicator has not been initialized. "
            "Check application startup."
        ) from exc

    try:
        pipeline = (
            request.app.state.company_processing_pipeline
        )
    except AttributeError as exc:
        logger.exception(
            "Canonical CompanyProcessingPipeline is missing "
            "from app.state."
        )

        raise RuntimeError(
            "CompanyProcessingPipeline has not been initialized. "
            "Check application startup."
        ) from exc

    # ---------------------------------------------------------
    # Safety validation
    # ---------------------------------------------------------

    registered_providers = (
        provider_manager.list_providers()
    )

    if not registered_providers:
        logger.error(
            "Canonical CompanyProviderManager contains "
            "no registered providers."
        )

        raise RuntimeError(
            "CompanyProviderManager contains no registered "
            "providers. Check application startup."
        )

    logger.debug(
        "CompanySearchService dependency created | "
        "providers=%s",
        registered_providers,
    )

    # ---------------------------------------------------------
    # Construct request-scoped service using shared
    # application infrastructure.
    # ---------------------------------------------------------

    return CompanySearchService(
        repository=repository,
        provider_manager=provider_manager,
        pipeline=pipeline,
    )


# =========================================================
# SEARCH
# =========================================================

@router.get(
    "/search",
    response_model=CompanySearchResponse,
)
async def search_companies(
    q: str = Query(
        ...,
        min_length=2,
        description=(
            "Search by company name, ticker, "
            "legal name, or alias."
        ),
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    service: CompanySearchService = Depends(
        get_company_search_service,
    ),
):
    """
    Search companies.

    Search strategy:

        1. Search PostgreSQL company catalog.
        2. If insufficient results, query registered providers.
        3. Normalize provider results.
        4. Deduplicate provider results.
        5. Upsert discovered companies.
        6. Merge local and imported results.
        7. Return the final result set.
    """

    query = q.strip()

    if not query:
        return CompanySearchResponse(
            query=q,
            total=0,
            results=[],
            limit=limit,
            offset=offset,
        )

    try:
        companies = await service.search(
            query=query,
            limit=limit,
            offset=offset,
        )

    except Exception as exc:
        logger.exception(
            "Company search failed | query=%r",
            query,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Company search failed. "
                "Check backend logs for details."
            ),
        ) from exc

    return CompanySearchResponse(
        query=query,
        total=len(companies),
        results=list(companies),
        limit=limit,
        offset=offset,
    )


# =========================================================
# GET COMPANY
# =========================================================

@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a company by database ID.
    """

    repository = CompanyRepository(
        db=db,
    )

    company = await repository.get_by_id(
        company_id,
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    return company


__all__ = [
    "router",
    "get_company_search_service",
    "search_companies",
    "get_company",
]