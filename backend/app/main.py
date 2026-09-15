"""
app/main.py

FastAPI application entry point.

Application composition root.

Responsibilities
----------------

- Initialize shared application services.
- Initialize company catalog infrastructure.
- Initialize industry catalog infrastructure.
- Initialize financial infrastructure.
- Initialize canonical LLM infrastructure.
- Construct the canonical AgentServices container.
- Construct the canonical AgentRegistry.
- Register all agents.
- Construct the canonical AgentManager.
- Construct the execution runtime.
- Validate canonical runtime wiring.
- Store canonical runtime objects on app.state.
- Configure FastAPI and CORS.
- Register and expose API routes.

IMPORTANT ARCHITECTURE

Application-global infrastructure is created exactly once
inside the lifespan.

Request-scoped infrastructure is NOT created here:

    AsyncSession
    CompanyRepository
    Request-specific ResearchService state
    AgentContext

AgentContext is created by ResearchService and propagated through:

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

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ============================================================================
# Logging
# ============================================================================

logger = logging.getLogger("orion")


# ============================================================================
# API / Configuration
# ============================================================================

from app.api.router import (
    api_router,
    get_registered_routes,
    validate_api_router,
)

from app.core.config import settings


# ============================================================================
# Database
# ============================================================================

from app.db.session import AsyncSessionLocal


# ============================================================================
# Agent Runtime
# ============================================================================

from app.agents.base.agent_services import AgentServices
from app.agents.base.registry import AgentRegistry
from app.agents.manager.agent_manager import AgentManager
from app.agents.registry_loader import register_agents


# ============================================================================
# Core Services
# ============================================================================

from app.services.tool_router import ToolRouter


# ============================================================================
# Canonical LLM Manager
# ============================================================================

from app.llm.factory import create_llm_manager
from app.llm.manager import LLMManager


# ============================================================================
# Research Services
# ============================================================================

from app.services.company_research_service import (
    CompanyResearchService,
)

from app.services.industry_research_service import (
    IndustryResearchService,
)

from app.services.financial_research_service import (
    FinancialResearchService,
)


# ============================================================================
# Company Catalog Infrastructure
# ============================================================================

from app.company_catalog.providers.provider_manager import (
    CompanyProviderManager,
)

from app.company_catalog.processing.pipeline import (
    CompanyProcessingPipeline,
)

from app.company_catalog.processing.deduplicate import (
    CompanyDeduplicator,
)


# ============================================================================
# Company Providers
# ============================================================================

from app.company_catalog.providers.sec_provider import SECProvider
from app.company_catalog.providers.yahoo_provider import YahooProvider
from app.company_catalog.providers.polygon_provider import PolygonProvider
from app.company_catalog.providers.alpha_vantage_provider import (
    AlphaVantageProvider,
)
from app.company_catalog.providers.openfigi_provider import OpenFIGIProvider
from app.company_catalog.providers.crunchbase_provider import CrunchbaseProvider
from app.company_catalog.providers.companies_house_provider import (
    CompaniesHouseProvider,
)


# ============================================================================
# Industry Catalog Infrastructure
# ============================================================================

from app.industry_catalog.sqlalchemy_repository import (
    SQLAlchemyIndustryRepository,
)

from app.services.industry_catalog_service import (
    IndustryCatalogService,
)


# ============================================================================
# Industry Processing
# ============================================================================

from app.industry_catalog.processing.pipeline import (
    IndustryProcessingPipeline,
)


# ============================================================================
# Industry Providers
# ============================================================================

from app.industry_catalog.providers.manager import (
    IndustryProviderManager,
)

from app.industry_catalog.providers.yahoo_provider import (
    YahooIndustryProvider,
)


# ============================================================================
# Market / Financial Tools
# ============================================================================

from app.tools.market.yahoo_finance_tool import YahooFinanceTool


# ============================================================================
# Financial Infrastructure
# ============================================================================

from app.financial.providers.provider_manager import (
    FinancialProviderManager,
)


# ============================================================================
# Knowledge System
# ============================================================================

from app.knowledge_system.manager import KnowledgeSystem


# ============================================================================
# Adaptive Retrieval
# ============================================================================

from app.adaptive_retrieval.manager import (
    AdaptiveRetrievalManager,
)


# ============================================================================
# Memory
# ============================================================================

from app.memory.manager import MemoryManager


# ============================================================================
# MCP
# ============================================================================

from app.mcp.manager import MCPManager


# ============================================================================
# Orchestration
# ============================================================================

from app.orchestration.tool_registry import ToolRegistry
from app.orchestration.tool_selector import ToolSelector
from app.orchestration.health_monitor import HealthMonitor
from app.orchestration.policies import PolicyEngine

from app.orchestration.orchestration_service import (
    OrchestrationService,
)


# ============================================================================
# Planning
# ============================================================================

from app.planning.parser import PlanningParser
from app.planning.planner import Planner


# ============================================================================
# Execution
# ============================================================================

from app.execution.execution_engine import ExecutionEngine
from app.execution.worker import Worker
from app.execution.dispatcher import Dispatcher


# ============================================================================
# Company Provider Factory
# ============================================================================

def _create_company_provider_manager() -> CompanyProviderManager:
    """Create the canonical company provider manager."""

    providers = [
        SECProvider(),
        YahooProvider(),
        PolygonProvider(),
        AlphaVantageProvider(),
        OpenFIGIProvider(),
        CrunchbaseProvider(),
        CompaniesHouseProvider(),
    ]

    provider_manager = CompanyProviderManager(
        providers=providers,
    )

    registered_providers = provider_manager.list_providers()

    if not registered_providers:
        raise RuntimeError(
            "CompanyProviderManager initialized without "
            "any registered providers."
        )

    print(
        "CompanyProviderManager initialized | "
        f"providers={registered_providers}"
    )

    return provider_manager


# ============================================================================
# Industry Provider Factory
# ============================================================================

def _create_industry_provider_manager() -> IndustryProviderManager:
    """Create the canonical industry provider manager."""

    yahoo_finance_tool = YahooFinanceTool()

    print(
        "YahooFinanceTool initialized for industry provider"
    )

    providers = [
        YahooIndustryProvider(
            yahoo_tool=yahoo_finance_tool,
        ),
    ]

    provider_manager = IndustryProviderManager(
        providers=providers,
    )

    registered_providers = provider_manager.provider_names()

    if not registered_providers:
        raise RuntimeError(
            "IndustryProviderManager initialized without "
            "any registered providers."
        )

    print(
        "IndustryProviderManager initialized | "
        f"providers={registered_providers}"
    )

    return provider_manager


# ============================================================================
# Route Diagnostics
# ============================================================================

def _get_registered_api_routes() -> list[dict[str, Any]]:
    """
    Return all actual routes currently registered on api_router.

    FastAPI 0.139.x stores routers included through
    APIRouter.include_router() as _IncludedRouter wrappers.

    The central get_registered_routes() helper recursively
    unwraps those objects and returns the actual endpoint routes.
    """

    return get_registered_routes()


def _validate_api_routes() -> None:
    """
    Validate critical API route registration.

    The frontend calls:

        /api/saved-artifacts

    Therefore the central router must contain:

        POST /saved-artifacts
    """

    # ------------------------------------------------------------------------
    # Validate through the central router.
    #
    # This uses recursive route inspection compatible with FastAPI 0.139.x.
    # ------------------------------------------------------------------------

    validate_api_router()

    # ------------------------------------------------------------------------
    # Get actual flattened routes.
    # ------------------------------------------------------------------------

    routes = _get_registered_api_routes()

    # ------------------------------------------------------------------------
    # Find saved-artifact routes.
    # ------------------------------------------------------------------------

    saved_artifact_routes = [
        route
        for route in routes
        if (
            "saved-artifact"
            in str(route["path"]).lower()
            or "saved_artifacts"
            in str(route["path"]).lower()
        )
    ]

    print()
    print(
        "API route registration validation"
    )
    print(
        "----------------------------------------------"
    )

    # ------------------------------------------------------------------------
    # Critical validation.
    # ------------------------------------------------------------------------

    if not saved_artifact_routes:
        raise RuntimeError(
            "Saved-artifact routes are not registered "
            "on api_router. "
            "Expected at least POST /saved-artifacts."
        )

    # ------------------------------------------------------------------------
    # Display saved-artifact routes.
    # ------------------------------------------------------------------------

    for route in saved_artifact_routes:
        print(
            "   [OK] "
            f"{route['methods']} "
            f"{route['path']}"
        )

    # ------------------------------------------------------------------------
    # Display total.
    # ------------------------------------------------------------------------

    print(
        "   Total API router routes: "
        f"{len(routes)}"
    )

    print(
        "----------------------------------------------"
    )
    print()


# ============================================================================
# Runtime Validation
# ============================================================================

def _validate_runtime(
    *,
    llm_manager: LLMManager,
    tool_router: ToolRouter,
    knowledge_system: KnowledgeSystem,
    retrieval_manager: AdaptiveRetrievalManager,
    memory_manager: MemoryManager,
    mcp_manager: MCPManager,
    orchestration_service: OrchestrationService,
    tool_registry: ToolRegistry,
    tool_selector: ToolSelector,
    health_monitor: HealthMonitor,
    policy_engine: PolicyEngine,
    planner: Planner,
    agent_services: AgentServices,
    agent_manager: AgentManager,
    worker: Worker,
    dispatcher: Dispatcher,
    execution_engine: ExecutionEngine,
) -> dict[str, Any]:
    """
    Validate that the canonical runtime graph is wired.

    This is intentionally a structural/wiring validation.

    It does NOT make expensive external API calls during startup.

    External providers should be tested through dedicated runtime
    health/smoke endpoints.
    """

    checks: dict[str, bool] = {}

    # ------------------------------------------------------------------
    # LLM
    # ------------------------------------------------------------------

    checks["llm_manager"] = isinstance(
        llm_manager,
        LLMManager,
    )

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    checks["tool_router"] = tool_router is not None
    checks["tool_registry"] = tool_registry is not None
    checks["tool_selector"] = tool_selector is not None

    # ------------------------------------------------------------------
    # Knowledge
    # ------------------------------------------------------------------

    checks["knowledge_system"] = knowledge_system is not None

    checks["adaptive_retrieval"] = (
        retrieval_manager is not None
        and getattr(
            retrieval_manager,
            "knowledge_system",
            knowledge_system,
        )
        is knowledge_system
    )

    # ------------------------------------------------------------------
    # Memory / MCP
    # ------------------------------------------------------------------

    checks["memory_manager"] = memory_manager is not None
    checks["mcp_manager"] = mcp_manager is not None

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    checks["health_monitor"] = health_monitor is not None
    checks["policy_engine"] = policy_engine is not None

    checks["orchestration_service"] = (
        orchestration_service is not None
        and getattr(
            orchestration_service,
            "registry",
            tool_registry,
        )
        is tool_registry
    )

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

    checks["planner"] = planner is not None

    # ------------------------------------------------------------------
    # Agent runtime
    # ------------------------------------------------------------------

    checks["agent_services"] = agent_services is not None
    checks["agent_manager"] = agent_manager is not None
    checks["worker"] = worker is not None
    checks["dispatcher"] = dispatcher is not None
    checks["execution_engine"] = execution_engine is not None

    # ------------------------------------------------------------------
    # Final validation
    # ------------------------------------------------------------------

    failed = [
        name
        for name, status in checks.items()
        if not status
    ]

    if failed:
        raise RuntimeError(
            "Runtime wiring validation failed: "
            f"{failed}"
        )

    print(
        "Runtime wiring validation passed | "
        f"checks={len(checks)}"
    )

    for name in checks:
        print(
            f"   [OK] {name}"
        )

    return {
        "status": "healthy",
        "checks": checks,
    }


# ============================================================================
# Application Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle."""

    print(
        "Enterprise AI Platform API starting..."
    )

    # ========================================================================
    # 1. LLM
    # ========================================================================

    print()

    llm_manager = create_llm_manager()

    if not isinstance(
        llm_manager,
        LLMManager,
    ):
        raise RuntimeError(
            "create_llm_manager() did not return "
            "an LLMManager instance."
        )

    print(
        "LLMManager initialized"
    )

    # ========================================================================
    # 2. Tool Router
    # ========================================================================

    tool_router = ToolRouter()

    print(
        "ToolRouter initialized"
    )

    # ========================================================================
    # 3. Knowledge
    # ========================================================================

    knowledge_system = KnowledgeSystem()

    print(
        "KnowledgeSystem initialized"
    )

    # ========================================================================
    # 4. Memory
    # ========================================================================

    memory_manager = MemoryManager()

    print(
        "MemoryManager initialized"
    )

    # ========================================================================
    # 5. MCP
    # ========================================================================

    mcp_manager = MCPManager()

    print(
        "MCPManager initialized"
    )

    # ========================================================================
    # 6. Adaptive Retrieval
    # ========================================================================

    retrieval_manager = AdaptiveRetrievalManager(
        knowledge_system=knowledge_system,
    )

    print(
        "AdaptiveRetrievalManager initialized"
    )

    # ========================================================================
    # 7. Orchestration
    # ========================================================================

    tool_registry = ToolRegistry()

    print(
        "ToolRegistry initialized"
    )

    tool_selector = ToolSelector(
        registry=tool_registry,
    )

    print(
        "ToolSelector initialized"
    )

    health_monitor = HealthMonitor()

    print(
        "HealthMonitor initialized"
    )

    policy_engine = PolicyEngine()

    print(
        "PolicyEngine initialized"
    )

    orchestration_service = OrchestrationService(
        registry=tool_registry,
        selector=tool_selector,
        health_monitor=health_monitor,
        policy_engine=policy_engine,
    )

    print(
        "OrchestrationService initialized"
    )

    # ========================================================================
    # 8. Company
    # ========================================================================

    company_provider_manager = (
        _create_company_provider_manager()
    )

    company_deduplicator = CompanyDeduplicator()

    print(
        "CompanyDeduplicator initialized"
    )

    company_processing_pipeline = CompanyProcessingPipeline(
        deduplicator=company_deduplicator,
    )

    print(
        "CompanyProcessingPipeline initialized"
    )

    company_research_service = CompanyResearchService(
        provider_manager=company_provider_manager,
        pipeline=company_processing_pipeline,
    )

    print(
        "CompanyResearchService initialized"
    )

    # ========================================================================
    # 9. Industry
    # ========================================================================

    industry_provider_manager = (
        _create_industry_provider_manager()
    )

    industry_processing_pipeline = IndustryProcessingPipeline(
        provider_manager=industry_provider_manager,
    )

    print(
        "IndustryProcessingPipeline initialized"
    )

    industry_catalog_repository = SQLAlchemyIndustryRepository(
        session_factory=AsyncSessionLocal,
    )

    print(
        "IndustryCatalogRepository initialized"
    )

    industry_catalog_service = IndustryCatalogService(
        repository=industry_catalog_repository,
        processing_pipeline=industry_processing_pipeline,
    )

    print(
        "IndustryCatalogService initialized"
    )

    industry_research_service = IndustryResearchService(
        industry_provider_manager=industry_provider_manager,
        industry_catalog=industry_catalog_service,
    )

    print(
        "IndustryResearchService initialized"
    )

    # ========================================================================
    # 10. Financial
    # ========================================================================

    financial_provider_manager = FinancialProviderManager()

    print(
        "FinancialProviderManager initialized"
    )

    print(
        "Financial providers registered | "
        f"providers={financial_provider_manager.list_providers()}"
    )

    financial_research_service = FinancialResearchService(
        provider_manager=financial_provider_manager,
    )

    print(
        "FinancialResearchService initialized"
    )

    # ========================================================================
    # 11. Planning
    # ========================================================================

    planning_parser = PlanningParser(
        llm_manager=llm_manager,
    )

    print(
        "PlanningParser initialized"
    )

    planner = Planner(
        llm_manager=llm_manager,
    )

    print(
        "Planner initialized"
    )

    # ========================================================================
    # 12. Agent Services
    # ========================================================================

    agent_services = AgentServices(
        llm=llm_manager,
        knowledge=knowledge_system,
        retrieval=retrieval_manager,
        memory=memory_manager,
        tools=tool_router,
        mcp=mcp_manager,
        orchestration=orchestration_service,
        company_research=company_research_service,
        industry_research=industry_research_service,
        financial_research=financial_research_service,
    )

    print(
        "AgentServices initialized"
    )

    # ========================================================================
    # 13. Agent Registry
    # ========================================================================

    registry = AgentRegistry()

    print(
        "AgentRegistry initialized"
    )

    register_agents(registry)

    registered_agents = registry.list_agent_ids()

    print(
        "Agents registered | "
        f"count={len(registered_agents)} | "
        f"agents={registered_agents}"
    )

    # ========================================================================
    # 14. Agent Manager
    # ========================================================================

    agent_manager = AgentManager(
        services=agent_services,
        registry=registry,
    )

    print(
        "AgentManager initialized"
    )

    required_agents = {
        "company",
        "financial",
        "industry",
    }

    missing_agents = sorted(
        name
        for name in required_agents
        if not agent_manager.has_agent(name)
    )

    if missing_agents:
        raise RuntimeError(
            "Agent registration failed. "
            f"Missing agents: {missing_agents}. "
            f"Registered agents: {registry.list_agent_ids()}"
        )

    print(
        "Required research agents validated | "
        f"agents={registry.list_agent_ids()}"
    )

    # ========================================================================
    # 15. Execution
    # ========================================================================

    worker = Worker(
        agent_manager=agent_manager,
    )

    print(
        "Worker initialized"
    )

    dispatcher = Dispatcher(
        worker=worker,
    )

    print(
        "Dispatcher initialized"
    )

    execution_engine = ExecutionEngine(
        dispatcher=dispatcher,
    )

    print(
        "ExecutionEngine initialized"
    )

    # ========================================================================
    # 16. Runtime Validation
    # ========================================================================

    runtime_health = _validate_runtime(
        llm_manager=llm_manager,
        tool_router=tool_router,
        knowledge_system=knowledge_system,
        retrieval_manager=retrieval_manager,
        memory_manager=memory_manager,
        mcp_manager=mcp_manager,
        orchestration_service=orchestration_service,
        tool_registry=tool_registry,
        tool_selector=tool_selector,
        health_monitor=health_monitor,
        policy_engine=policy_engine,
        planner=planner,
        agent_services=agent_services,
        agent_manager=agent_manager,
        worker=worker,
        dispatcher=dispatcher,
        execution_engine=execution_engine,
    )

    # ========================================================================
    # 17. Store Runtime
    # ========================================================================

    app.state.llm_manager = llm_manager

    app.state.tool_router = tool_router

    app.state.knowledge_system = knowledge_system
    app.state.retrieval_manager = retrieval_manager

    app.state.memory_manager = memory_manager
    app.state.mcp_manager = mcp_manager

    app.state.tool_registry = tool_registry
    app.state.tool_selector = tool_selector
    app.state.health_monitor = health_monitor
    app.state.policy_engine = policy_engine
    app.state.orchestration_service = orchestration_service

    app.state.company_provider_manager = (
        company_provider_manager
    )

    app.state.provider_manager = (
        company_provider_manager
    )

    app.state.company_deduplicator = (
        company_deduplicator
    )

    app.state.company_processing_pipeline = (
        company_processing_pipeline
    )

    app.state.company_research_service = (
        company_research_service
    )

    app.state.industry_provider_manager = (
        industry_provider_manager
    )

    app.state.industry_processing_pipeline = (
        industry_processing_pipeline
    )

    app.state.industry_catalog_repository = (
        industry_catalog_repository
    )

    app.state.industry_catalog_service = (
        industry_catalog_service
    )

    app.state.industry_catalog = (
        industry_catalog_service
    )

    app.state.industry_research_service = (
        industry_research_service
    )

    app.state.financial_provider_manager = (
        financial_provider_manager
    )

    app.state.financial_research_service = (
        financial_research_service
    )

    app.state.planning_parser = planning_parser
    app.state.planner = planner

    app.state.agent_services = agent_services
    app.state.agent_registry = registry
    app.state.agent_manager = agent_manager

    app.state.worker = worker
    app.state.dispatcher = dispatcher
    app.state.execution_engine = execution_engine

    app.state.runtime_health = runtime_health

    # ========================================================================
    # 18. Startup Summary
    # ========================================================================

    print(
        "=============================================="
    )

    print(
        "Orion AI Platform runtime initialized"
    )

    print()

    print(
        f"   API prefix: {settings.API_PREFIX}"
    )

    print(
        f"   LLMManager: {id(llm_manager)}"
    )

    print(
        f"   ToolRouter: {id(tool_router)}"
    )

    print(
        f"   KnowledgeSystem: {id(knowledge_system)}"
    )

    print(
        f"   AdaptiveRetrievalManager: {id(retrieval_manager)}"
    )

    print(
        f"   MemoryManager: {id(memory_manager)}"
    )

    print(
        f"   MCPManager: {id(mcp_manager)}"
    )

    print(
        f"   OrchestrationService: {id(orchestration_service)}"
    )

    print(
        f"   AgentServices: {id(agent_services)}"
    )

    print(
        f"   AgentRegistry: {id(registry)}"
    )

    print(
        f"   AgentManager: {id(agent_manager)}"
    )

    print(
        f"   Worker: {id(worker)}"
    )

    print(
        f"   Dispatcher: {id(dispatcher)}"
    )

    print(
        f"   ExecutionEngine: {id(execution_engine)}"
    )

    print(
        "   Company providers: "
        f"{company_provider_manager.list_providers()}"
    )

    print(
        "   Industry providers: "
        f"{industry_provider_manager.provider_names()}"
    )

    print(
        "   Financial providers: "
        f"{financial_provider_manager.list_providers()}"
    )

    print(
        "   Registered agents: "
        f"{registry.list_agent_ids()}"
    )

    print(
        "=============================================="
    )

    yield

    print(
        "Enterprise AI Platform API shutdown"
    )


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# ============================================================================
# CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API Routes
# ============================================================================

# Route registration happens during application construction,
# not inside the lifespan.
#
# The central api_router recursively understands FastAPI 0.139.x
# _IncludedRouter objects.

_validate_api_routes()

app.include_router(
    api_router,
    prefix=settings.API_PREFIX,
)


# ============================================================================
# Root
# ============================================================================

@app.get("/")
async def root() -> dict[str, str]:
    """Root API health endpoint."""

    return {
        "message": "Orion AI Platform API running",
        "version": settings.APP_VERSION,
    }


# ============================================================================
# Runtime Health
# ============================================================================

@app.get("/runtime/health")
async def runtime_health() -> dict[str, Any]:
    """
    Return canonical runtime wiring status.
    """

    if not hasattr(
        app.state,
        "runtime_health",
    ):
        return {
            "status": "unavailable",
            "message": "Runtime has not completed startup.",
        }

    return app.state.runtime_health


# ============================================================================
# Runtime Architecture
# ============================================================================

@app.get("/runtime/architecture")
async def runtime_architecture() -> dict[str, Any]:
    """
    Expose the canonical Orion runtime architecture.
    """

    return {
        "status": "running",

        "llm": {
            "llm_service": hasattr(
                app.state,
                "llm_service",
            ),
            "llm_manager": hasattr(
                app.state,
                "llm_manager",
            ),
        },

        "tools": {
            "tool_router": hasattr(
                app.state,
                "tool_router",
            ),
            "tool_registry": hasattr(
                app.state,
                "tool_registry",
            ),
            "tool_selector": hasattr(
                app.state,
                "tool_selector",
            ),
        },

        "knowledge": {
            "knowledge_system": hasattr(
                app.state,
                "knowledge_system",
            ),
            "adaptive_retrieval": hasattr(
                app.state,
                "retrieval_manager",
            ),
        },

        "memory": {
            "memory_manager": hasattr(
                app.state,
                "memory_manager",
            ),
        },

        "mcp": {
            "mcp_manager": hasattr(
                app.state,
                "mcp_manager",
            ),
        },

        "orchestration": {
            "orchestration_service": hasattr(
                app.state,
                "orchestration_service",
            ),
            "health_monitor": hasattr(
                app.state,
                "health_monitor",
            ),
            "policy_engine": hasattr(
                app.state,
                "policy_engine",
            ),
        },

        "planning": {
            "planning_parser": hasattr(
                app.state,
                "planning_parser",
            ),
            "planner": hasattr(
                app.state,
                "planner",
            ),
        },

        "agents": {
            "registry": hasattr(
                app.state,
                "agent_registry",
            ),
            "manager": hasattr(
                app.state,
                "agent_manager",
            ),
            "agents": (
                app.state.agent_registry.list_agent_ids()
                if hasattr(
                    app.state,
                    "agent_registry",
                )
                else []
            ),
        },

        "execution": {
            "worker": hasattr(
                app.state,
                "worker",
            ),
            "dispatcher": hasattr(
                app.state,
                "dispatcher",
            ),
            "execution_engine": hasattr(
                app.state,
                "execution_engine",
            ),
        },

        "api": {
            "prefix": settings.API_PREFIX,

            "saved_artifacts": [
                route
                for route in _get_registered_api_routes()
                if (
                    "saved-artifact"
                    in str(route["path"]).lower()
                    or "saved_artifacts"
                    in str(route["path"]).lower()
                )
            ],
        },
    }