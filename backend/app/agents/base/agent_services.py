
"""
app/agents/base/agent_services.py

Canonical dependency-injection container for the agent runtime.

AgentServices owns REFERENCES to application-level services.
It does not construct, initialize, or manage those services.

Request-scoped dependencies such as CompanyRepository do NOT
belong here. They belong on AgentContext.

Architecture:

```

Application Composition Root
|
v
AgentServices
|
v
AgentManager
|
v
Specialized Agents

```

Domain research flow:

```

IndustryAgent
|
v
services.industry_research
|
v
IndustryResearchService
|
v
IndustryCatalogService
|
v
Industry providers / resolver

```

IMPORTANT:

AgentServices contains application-level capabilities.

It should NOT contain:

- AsyncSession
- CompanyRepository
- AgentContext
- Provider instances
- IndustryProviderManager
- CompanyProviderManager
- FinancialProviderManager
- request-specific state
- agent instances

Those dependencies belong to their appropriate architectural layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# ============================================================================
# Core AI
# ============================================================================

from app.llm.manager import LLMManager

# ============================================================================
# Tools
# ============================================================================

from app.services.tool_router import ToolRouter

# ============================================================================
# Company Research
# ============================================================================

from app.services.company_research_service import (
    CompanyResearchService,
)

# ============================================================================
# Financial Research
# ============================================================================

from app.services.financial_research_service import (
    FinancialResearchService,
)

# ============================================================================
# Industry Research
# ============================================================================

from app.services.industry_research_service import (
    IndustryResearchService,
)

# ============================================================================
# Industry Catalog
# ============================================================================

from app.services.industry_catalog_service import (
    IndustryCatalogService
)

# ============================================================================
# Knowledge
# ============================================================================

from app.knowledge_system.manager import KnowledgeSystem

# ============================================================================
# Retrieval
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

from app.orchestration.orchestration_service import (
    OrchestrationService,
)


# ============================================================================
# Agent Services
# ============================================================================

@dataclass(slots=True)
class AgentServices:
    """
    Canonical shared-service container for all agents.

    The application composition root constructs exactly one
    AgentServices instance.

    AgentManager receives that same instance and passes it to
    every registered agent.

    Therefore:

        agent.services is services

    must refer to the same shared AgentServices object.

    AgentServices only stores REFERENCES to application-level
    services. It does not construct or manage them.

    ------------------------------------------------------------------------
    Core services
    ------------------------------------------------------------------------

        llm
        knowledge
        retrieval
        memory
        tools
        mcp
        orchestration

    ------------------------------------------------------------------------
    Domain services
    ------------------------------------------------------------------------

        company_research
        industry_research
        financial_research

    ------------------------------------------------------------------------
    Catalog services
    ------------------------------------------------------------------------

        industry_catalog

    ------------------------------------------------------------------------
    Request-scoped dependencies
    ------------------------------------------------------------------------

    These deliberately do NOT belong here:

        AsyncSession
        CompanyRepository
        AgentContext

    They are request/runtime scoped and belong to AgentContext
    or the request dependency layer.
    """

    # ========================================================================
    # Core AI
    # ========================================================================

    llm: LLMManager

    # ========================================================================
    # Shared Infrastructure
    # ========================================================================

    knowledge: KnowledgeSystem

    retrieval: AdaptiveRetrievalManager

    memory: MemoryManager

    tools: ToolRouter

    mcp: MCPManager

    orchestration: OrchestrationService

    # ========================================================================
    # Domain Research Services
    # ========================================================================

    """
    Company research capability.

    Application-level service responsible for company research
    orchestration.

    The service itself owns access to company catalog infrastructure.
    """

    company_research: Optional[CompanyResearchService] = None

    """
    Industry research capability.

    Application-level service responsible for industry research
    orchestration.

    Typical flow:

        IndustryAgent
              |
              v
        IndustryResearchService
              |
              v
        IndustryCatalogService
              |
              v
        Industry providers / resolver

    Agents normally access industry research through:

        services.industry_research
    """

    industry_research: Optional[IndustryResearchService] = None

    """
    Financial research capability.

    Application-level service responsible for financial research
    orchestration.
    """

    financial_research: Optional[FinancialResearchService] = None

    # ========================================================================
    # Catalog Services
    # ========================================================================

    """
    Industry catalog capability.

    Application-level service responsible for industry identity,
    classification, taxonomy, and catalog metadata.

    Typical flow:

        IndustryCatalogService
                |
                v
        IndustryProviderManager
                |
                v
        SIC / NAICS / GICS / Yahoo / Web providers
    """

    industry_catalog: Optional[IndustryCatalogService] = None

    # ========================================================================
    # Observability
    # ========================================================================

    """
    Optional observability integration.

    Kept generic so the agent runtime does not depend on a
    particular monitoring implementation.
    """

    observability: Optional[object] = None

    # ========================================================================
    # Optional Shared Infrastructure
    # ========================================================================

    """
    Optional application logger.

    Normally modules should use module-level logging, but this
    remains available for infrastructure that requires an injected
    logger.
    """

    logger: Optional[object] = None

    """
    Optional metrics collector.
    """

    metrics: Optional[object] = None

    """
    Optional shared cache.
    """

    cache: Optional[object] = None

