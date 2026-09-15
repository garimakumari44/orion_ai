from __future__ import annotations

import logging
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession


# ============================================================
# Core Dependencies
# ============================================================

from app.core.dependencies import (
    get_agent_services,
    get_company_repository,
    get_execution_engine,
    get_industry_catalog_service,
    get_planner,
    get_planning_parser,
)


# ============================================================
# Database
# ============================================================

from app.db.session import get_db

from app.repositories.company_repository import (
    CompanyRepository,
)


# ============================================================
# Industry Catalog
# ============================================================

from app.services.industry_catalog_service import (
    IndustryCatalogService,
)


# ============================================================
# Planning
# ============================================================

from app.planning.parser import PlanningParser
from app.planning.planner import Planner


# ============================================================
# Execution
# ============================================================

from app.execution.execution_engine import ExecutionEngine


# ============================================================
# Agent Services
# ============================================================

from app.agents.base.agent_services import AgentServices


# ============================================================
# Schemas
# ============================================================

from app.schemas.research import (
    ResearchDetailResponse,
    ResearchResultResponse,
    ResearchStartRequest,
    ResearchStartResponse,
    ResearchStatusResponse,
)


# ============================================================
# Research Service
# ============================================================

from app.services.research_service import (
    ResearchService,
)


# ============================================================
# Logger
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/research",
    tags=["Research"],
)


# ============================================================
# Research Service Dependency
# ============================================================

async def get_research_service(
    db: AsyncSession = Depends(get_db),

    company_repository: CompanyRepository = Depends(
        get_company_repository
    ),

    industry_catalog_service: IndustryCatalogService = Depends(
        get_industry_catalog_service
    ),

    execution_engine: ExecutionEngine = Depends(
        get_execution_engine
    ),

    agent_services: AgentServices = Depends(
        get_agent_services
    ),

    parser: PlanningParser = Depends(
        get_planning_parser
    ),

    planner: Planner = Depends(
        get_planner
    ),
) -> ResearchService:
    """
    Construct the request-scoped ResearchService.

    Application-global infrastructure is injected through
    app.core.dependencies.

    This function does not construct execution infrastructure.
    """

    return ResearchService(
        db=db,
        company_repository=company_repository,
        industry_catalog_service=industry_catalog_service,
        parser=parser,
        planner=planner,
        execution_engine=execution_engine,
        services=agent_services,
    )


# ============================================================
# POST /research/start
#
# Final route:
#     POST /api/research/start
# ============================================================

@router.post(
    "/start",
    response_model=ResearchStartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_research(
    request: ResearchStartRequest,
    background_tasks: BackgroundTasks,
    service: ResearchService = Depends(
        get_research_service
    ),
) -> ResearchStartResponse:
    """
    Create a research project and queue execution.

    research.id is a UUID and is passed unchanged into
    ResearchService.execute_research().
    """

    try:
        response, execution_plan = (
            await service.start_research(request)
        )

        research_id = response.research.id

        logger.info(
            "Research created successfully | "
            "research_id=%s | execution_plan_id=%s",
            research_id,
            response.execution_plan_id,
        )

        background_tasks.add_task(
            service.execute_research,
            research_id,
            execution_plan,
        )

        logger.info(
            "Research execution queued | research_id=%s",
            research_id,
        )

        return response

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Failed to start research | request=%s",
            request,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ============================================================
# GET /research/status/{research_id}
#
# Final route:
#     GET /api/research/status/{uuid}
# ============================================================

@router.get(
    "/status/{research_id}",
    response_model=ResearchStatusResponse,
)
async def research_status(
    research_id: UUID,
    service: ResearchService = Depends(
        get_research_service
    ),
) -> ResearchStatusResponse:
    """
    Get live research execution status.

    research_id is a UUID.
    """

    logger.info(
        "Research status requested | research_id=%s",
        research_id,
    )

    try:
        result = await service.get_status(
            research_id
        )

        if result is None:
            logger.warning(
                "Research not found | research_id=%s",
                research_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research not found",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Failed to retrieve research status | "
            "research_id=%s",
            research_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ============================================================
# GET /research/{research_id}/results
#
# Final route:
#     GET /api/research/{uuid}/results
# ============================================================

@router.get(
    "/{research_id}/results",
    response_model=ResearchResultResponse,
)
async def get_research_results(
    research_id: UUID,
    service: ResearchService = Depends(
        get_research_service
    ),
) -> ResearchResultResponse:
    """
    Get the persisted research result.

    research_id is a UUID.
    """

    logger.info(
        "Research results requested | research_id=%s",
        research_id,
    )

    try:
        results = await service.get_results(
            research_id
        )

        if results is None:
            logger.info(
                "Research results not available yet | "
                "research_id=%s",
                research_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Results not available",
            )

        logger.info(
            "Research results returned successfully | "
            "research_id=%s",
            research_id,
        )

        return results

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Failed to retrieve research results | "
            "research_id=%s",
            research_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ============================================================
# GET /research/{research_id}
#
# Final route:
#     GET /api/research/{uuid}
# ============================================================

@router.get(
    "/{research_id}",
    response_model=ResearchDetailResponse,
)
async def get_research(
    research_id: UUID,
    service: ResearchService = Depends(
        get_research_service
    ),
) -> ResearchDetailResponse:
    """
    Get research workspace metadata.

    research_id is a UUID.
    """

    logger.info(
        "Research metadata requested | research_id=%s",
        research_id,
    )

    try:
        research = await service.get_research(
            research_id
        )

        if research is None:
            logger.warning(
                "Research not found | research_id=%s",
                research_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research not found",
            )

        return research

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Failed to retrieve research | research_id=%s",
            research_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc