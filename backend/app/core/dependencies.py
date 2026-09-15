"""
app/core/dependencies.py

Application dependency container and FastAPI dependencies.

Responsibilities:

- Authentication dependencies.
- Database dependencies.
- Request-scoped repository dependencies.
- Retrieval of canonical application-level services.
- Retrieval of canonical AgentServices.
- Retrieval of canonical AgentManager.
- Retrieval of canonical ExecutionEngine.
- Retrieval of canonical IndustryCatalogService.
- Retrieval of ResearchService.
- Retrieval of authenticated users.

IMPORTANT ARCHITECTURE
----------------------

app.main is the application composition root.

It owns construction and initialization of:

    AgentServices
    AgentRegistry
    AgentManager
    ToolRouter
    KnowledgeSystem
    AdaptiveRetrievalManager
    MemoryManager
    MCPManager
    OrchestrationService
    CompanyResearchService
    FinancialResearchService
    IndustryCatalogService
    ExecutionEngine
    PlanningParser
    Planner

Those objects are stored on:

    app.state

This module MUST NOT construct those application-level
services.

REQUEST-SCOPED INFRASTRUCTURE
----------------------------

The following objects are intentionally request-scoped:

    AsyncSession
    CompanyRepository
    ResearchService

The dependency graph is:

    FastAPI
        |
        +--> get_db()
        |       |
        |       v
        |   AsyncSession
        |       |
        |       v
        |   CompanyRepository
        |
        +--> app.state canonical services
                |
                v
          ResearchService

ResearchService receives CompanyRepository through dependency
injection and MUST NOT construct CompanyRepository itself.

AGENT CONTEXT
-------------

AgentContext is NOT created here.

AgentContext is created exactly once by ResearchService and
propagated unchanged through:

    ResearchService
        |
        v
    ExecutionEngine
        |
        v
    Dispatcher
        |
        v
    Worker
        |
        v
    AgentManager
        |
        v
      Agent
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession


# ============================================================
# Authentication / Database
# ============================================================

from app.core.security import verify_access_token
from app.db.session import get_db
from app.db.models.user import Users


# ============================================================
# Request-Scoped Repositories
# ============================================================

from app.repositories.company_repository import CompanyRepository


# ============================================================
# Agent Infrastructure
# ============================================================

from app.agents.base.agent_services import AgentServices
from app.agents.manager.agent_manager import AgentManager


# ============================================================
# Execution Infrastructure
# ============================================================

from app.execution.execution_engine import ExecutionEngine


# ============================================================
# Planning Infrastructure
# ============================================================

from app.planning.parser import PlanningParser
from app.planning.planner import Planner


# ============================================================
# Application Services
# ============================================================

from app.services.llm import LLMService
from app.services.tool_router import ToolRouter

from app.services.company_research_service import (
    CompanyResearchService,
)

from app.services.financial_research_service import (
    FinancialResearchService,
)

from app.services.industry_catalog_service import (
    IndustryCatalogService,
)

from app.services.research_service import ResearchService


# ============================================================
# Knowledge / Retrieval
# ============================================================

from app.knowledge_system.manager import KnowledgeSystem

from app.adaptive_retrieval.manager import (
    AdaptiveRetrievalManager,
)


# ============================================================
# Memory / MCP / Orchestration
# ============================================================

from app.memory.manager import MemoryManager

from app.mcp.manager import MCPManager

from app.orchestration.orchestration_service import (
    OrchestrationService,
)


# ============================================================
# JWT Bearer Configuration
# ============================================================

security_scheme = HTTPBearer(
    bearerFormat="JWT",
    scheme_name="Access Token",
)


# ============================================================
# Database Dependency
# ============================================================

DBSession = Annotated[
    AsyncSession,
    Depends(get_db),
]


# ============================================================
# Access Token Dependency
# ============================================================

Token = Annotated[
    HTTPAuthorizationCredentials,
    Depends(security_scheme),
]


# ============================================================
# Internal app.state Helper
# ============================================================

def _get_state_service(
    request: Request,
    name: str,
    expected_type: type[Any],
) -> Any:
    """
    Retrieve a canonical application-level service from
    request.app.state.

    Application-level services are constructed by app.main
    during application startup/lifespan.

    This helper prevents request dependencies from accidentally
    constructing duplicate application infrastructure.

    Parameters
    ----------
    request:
        Current FastAPI request.

    name:
        Attribute name on request.app.state.

    expected_type:
        Required runtime type.

    Returns
    -------
    Any
        Canonical application-level service instance.

    Raises
    ------
    RuntimeError
        If the service has not been initialized.

    TypeError
        If app.state contains an unexpected object.
    """

    service = getattr(
        request.app.state,
        name,
        None,
    )

    if service is None:
        raise RuntimeError(
            f"Canonical application service "
            f"'{name}' is not initialized. "
            "The application composition root "
            "(app.main) must initialize it during "
            "the application lifespan."
        )

    if not isinstance(
        service,
        expected_type,
    ):
        raise TypeError(
            f"app.state.{name} must be an instance of "
            f"{expected_type.__name__}, "
            f"got {type(service).__name__}."
        )

    return service


# ============================================================
# LLM Service
# ============================================================

async def get_llm_service(
    request: Request,
) -> LLMService:
    """
    Return the canonical application-level LLMService.

    LLMService is constructed by app.main.
    """

    return _get_state_service(
        request,
        "llm_service",
        LLMService,
    )


# ============================================================
# Tool Router
# ============================================================

async def get_tool_router(
    request: Request,
) -> ToolRouter:
    """
    Return the canonical application-level ToolRouter.

    ToolRouter is constructed by app.main.
    """

    return _get_state_service(
        request,
        "tool_router",
        ToolRouter,
    )


# ============================================================
# Knowledge System
# ============================================================

async def get_knowledge_system(
    request: Request,
) -> KnowledgeSystem:
    """
    Return the canonical shared KnowledgeSystem.

    KnowledgeSystem is constructed and initialized by app.main.
    """

    return _get_state_service(
        request,
        "knowledge_system",
        KnowledgeSystem,
    )


# ============================================================
# Adaptive Retrieval
# ============================================================

async def get_retrieval_manager(
    request: Request,
) -> AdaptiveRetrievalManager:
    """
    Return the canonical shared AdaptiveRetrievalManager.

    Both KnowledgeSystem and AdaptiveRetrievalManager are owned
    by the application composition root.
    """

    # Ensure the canonical KnowledgeSystem exists before
    # retrieving the retrieval manager.
    await get_knowledge_system(request)

    return _get_state_service(
        request,
        "retrieval_manager",
        AdaptiveRetrievalManager,
    )


# ============================================================
# Memory
# ============================================================

async def get_memory_manager(
    request: Request,
) -> MemoryManager:
    """
    Return the canonical shared MemoryManager.
    """

    return _get_state_service(
        request,
        "memory_manager",
        MemoryManager,
    )


# ============================================================
# MCP
# ============================================================

async def get_mcp_manager(
    request: Request,
) -> MCPManager:
    """
    Return the canonical shared MCPManager.
    """

    return _get_state_service(
        request,
        "mcp_manager",
        MCPManager,
    )


# ============================================================
# Orchestration
# ============================================================

async def get_orchestration_service(
    request: Request,
) -> OrchestrationService:
    """
    Return the canonical shared OrchestrationService.
    """

    return _get_state_service(
        request,
        "orchestration_service",
        OrchestrationService,
    )


# ============================================================
# Company Research Service
# ============================================================

async def get_company_research_service(
    request: Request,
) -> CompanyResearchService:
    """
    Return the canonical CompanyResearchService.

    CompanyResearchService is application-level infrastructure
    and is constructed by app.main.

    It MUST NOT own a request-scoped CompanyRepository.
    """

    return _get_state_service(
        request,
        "company_research_service",
        CompanyResearchService,
    )


# ============================================================
# Financial Research Service
# ============================================================

async def get_financial_research_service(
    request: Request,
) -> FinancialResearchService:
    """
    Return the canonical FinancialResearchService.

    FinancialResearchService is application-level infrastructure
    and is constructed by app.main.
    """

    return _get_state_service(
        request,
        "financial_research_service",
        FinancialResearchService,
    )


# ============================================================
# Industry Catalog Service
# ============================================================

async def get_industry_catalog_service(
    request: Request,
) -> IndustryCatalogService:
    """
    Return the canonical IndustryCatalogService.

    IndustryCatalogService is application-level infrastructure
    and is constructed by app.main.

    It MUST NOT be constructed here.

    The canonical service is stored on:

        app.state.industry_catalog_service

    This service is responsible for canonical industry
    catalog access and industry resolution.
    """

    return _get_state_service(
        request,
        "industry_catalog_service",
        IndustryCatalogService,
    )


# ============================================================
# AgentServices
# ============================================================

async def get_agent_services(
    request: Request,
) -> AgentServices:
    """
    Return the canonical application-level AgentServices.

    AgentServices is created exactly once by app.main.

    This dependency NEVER creates:

        AgentServices()
    """

    return _get_state_service(
        request,
        "agent_services",
        AgentServices,
    )


# ============================================================
# AgentManager
# ============================================================

async def get_agent_manager(
    request: Request,
) -> AgentManager:
    """
    Return the canonical application-level AgentManager.

    This dependency MUST NOT create:

        AgentManager()
        AgentRegistry()
        AgentServices()

    Those objects are owned by app.main.
    """

    return _get_state_service(
        request,
        "agent_manager",
        AgentManager,
    )


# ============================================================
# ExecutionEngine
# ============================================================

async def get_execution_engine(
    request: Request,
) -> ExecutionEngine:
    """
    Return the canonical application-level ExecutionEngine.

    ExecutionEngine is constructed by app.main.

    This dependency MUST NOT construct an ExecutionEngine.
    """

    return _get_state_service(
        request,
        "execution_engine",
        ExecutionEngine,
    )


# ============================================================
# PlanningParser
# ============================================================

async def get_planning_parser(
    request: Request,
) -> PlanningParser:
    """
    Return the canonical application-level PlanningParser.

    PlanningParser is constructed by app.main.
    """

    return _get_state_service(
        request,
        "planning_parser",
        PlanningParser,
    )


# ============================================================
# Planner
# ============================================================

async def get_planner(
    request: Request,
) -> Planner:
    """
    Return the canonical application-level Planner.

    Planner is constructed by app.main.
    """

    return _get_state_service(
        request,
        "planner",
        Planner,
    )


# ============================================================
# Request-Scoped CompanyRepository
# ============================================================

async def get_company_repository(
    db: DBSession,
) -> CompanyRepository:
    """
    Create the request-scoped CompanyRepository.

    Lifecycle:

        Request
            |
            v
        AsyncSession
            |
            v
        CompanyRepository
            |
            v
        ResearchService

    IMPORTANT
    ---------

    CompanyRepository is intentionally constructed here.

    It MUST NOT be stored on app.state because it depends on
    the request-scoped AsyncSession.
    """

    return CompanyRepository(
        db=db,
    )


# ============================================================
# Research Service
# ============================================================

async def get_research_service(
    db: DBSession,
    company_repository: Annotated[
        CompanyRepository,
        Depends(get_company_repository),
    ],
    industry_catalog_service: Annotated[
        IndustryCatalogService,
        Depends(get_industry_catalog_service),
    ],
    execution_engine: Annotated[
        ExecutionEngine,
        Depends(get_execution_engine),
    ],
    agent_services: Annotated[
        AgentServices,
        Depends(get_agent_services),
    ],
    parser: Annotated[
        PlanningParser,
        Depends(get_planning_parser),
    ],
    planner: Annotated[
        Planner,
        Depends(get_planner),
    ],
) -> ResearchService:
    """
    Construct the request-scoped ResearchService.

    Dependency graph:

        FastAPI Request
              |
              +-------------------------------+
              |                               |
              v                               v
        AsyncSession                    app.state
              |                       canonical services
              v                               |
      CompanyRepository                       |
              |                               |
              +---------------+---------------+
                              |
                              v
                      ResearchService
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
    IndustryCatalogService              ExecutionEngine
             |                                 |
             v                                 v
      Canonical Industry                 AgentContext
      Resolution                              |
                                               v
                                          Dispatcher
                                               |
                                               v
                                            Worker
                                               |
                                               v
                                          AgentManager
                                               |
                                               v
                                             Agent

    ResearchService MUST NOT construct:

        CompanyRepository
        IndustryCatalogService
        AgentServices
        ExecutionEngine
        PlanningParser
        Planner

    All application-level services are injected through
    FastAPI dependencies.
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
# Current User
# ============================================================

async def get_current_user(
    token: Token,
    db: DBSession,
) -> Users:
    """
    Resolve the authenticated user from the JWT access token.
    """

    access_token = token.credentials

    user_id = verify_access_token(
        access_token,
    )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        user_id_int = int(user_id)

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    user = await db.get(
        Users,
        user_id_int,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ============================================================
# Active User
# ============================================================

async def get_current_active_user(
    user: Users = Depends(
        get_current_user,
    ),
) -> Users:
    """
    Require an active user account.
    """

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


# ============================================================
# Admin User
# ============================================================

async def get_current_admin_user(
    user: Users = Depends(
        get_current_active_user,
    ),
) -> Users:
    """
    Require administrator privileges.
    """

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return user