
"""
app/agents/registry_loader.py

Central application-level agent registration.

Canonical resolution:

    capability
        ↓
    agent_name
        ↓
    AgentMetadata
        ↓
    agent_class
        ↓
    AgentManager
        ↓
    Specialized Agent

This module is responsible only for registering the
application's production agents.

It does NOT:

- instantiate agents
- create AgentContext
- execute agents
- create services
- execute tasks
"""

from __future__ import annotations

import logging
from typing import Optional

from app.agents.base.registry import AgentRegistry

# ============================================================================
# Planner
# ============================================================================

from app.agents.planner.agent import PlannerAgent

# ============================================================================
# Research
# ============================================================================

from app.agents.company.agent import CompanyAgent
from app.agents.financial.agent import FinancialAnalysisAgent
from app.agents.industry.agent import IndustryAgent
from app.agents.news.agent import NewsAgent
from app.agents.macro.agent import MacroAgent

# ============================================================================
# Analysis
# ============================================================================

from app.agents.valuation.agent import ValuationAgent
from app.agents.risk.agent import RiskAgent

# ============================================================================
# Intelligence
# ============================================================================

from app.agents.evidence.agent import EvidenceAgent

# ============================================================================
# Decision
# ============================================================================

from app.agents.investment_committee.agent import (
    InvestmentCommitteeAgent,
)

# ============================================================================
# Quality
# ============================================================================

from app.agents.critic.agent import CriticAgent


logger = logging.getLogger(__name__)


# ============================================================================
# Register Agents
# ============================================================================


def register_agents(
    registry: Optional[AgentRegistry] = None,
) -> AgentRegistry:
    """
    Register all production agents into an AgentRegistry.

    If an existing registry is supplied, registrations are added
    to that exact registry instance.

    If omitted, a new AgentRegistry is created.

    Returns
    -------
    AgentRegistry
        Fully configured and validated registry.
    """

    # ------------------------------------------------------------------------
    # Registry
    # ------------------------------------------------------------------------

    if registry is None:
        registry = AgentRegistry()

    if not isinstance(registry, AgentRegistry):
        raise TypeError(
            "registry must be an AgentRegistry instance, "
            f"got {type(registry).__name__}"
        )

    logger.info(
        "Loading agent registry | registry=%s",
        type(registry).__name__,
    )

    # ========================================================================
    # Planner
    # ========================================================================

    registry.register(
        agent_name="planner",
        agent_class=PlannerAgent,
        category="planner",
        display_name="Planner Agent",
        description=(
            "Decomposes high-level research requests into "
            "executable research tasks."
        ),
        capabilities=[
            "planning",
            "research.planning",
            "task.decomposition",
        ],
    )

    # ========================================================================
    # Company
    # ========================================================================

    registry.register(
        agent_name="company",
        agent_class=CompanyAgent,
        category="research",
        display_name="Company Research Agent",
        description=(
            "Analyzes a company's business, products, segments, "
            "management, ownership, geography, and corporate profile."
        ),
        capabilities=[
            "company.research",
            "company.profile",
            "company.business_model",
            "company.management",
            "company.products",
            "company.segments",
            "company.ownership",
            "company.geography",
        ],
    )

    # ========================================================================
    # Financial
    # ========================================================================

    registry.register(
        agent_name="financial",
        agent_class=FinancialAnalysisAgent,
        category="research",
        display_name="Financial Analysis Agent",
        description=(
            "Analyzes financial statements, performance, growth, "
            "profitability, cash flow, balance sheet, ratios, "
            "and capital allocation."
        ),
        capabilities=[
            "financial.analysis",
            "financial.performance",
            "financial.statements",
            "financial.growth",
            "financial.profitability",
            "financial.cashflow",
            "financial.balance_sheet",
            "financial.capital_allocation",
            "financial.ratios",
        ],
    )

    # ========================================================================
    # Industry
    # ========================================================================

    registry.register(
        agent_name="industry",
        agent_class=IndustryAgent,
        category="research",
        display_name="Industry Research Agent",
        description=(
            "Analyzes industry structure, market size, competition, "
            "trends, supply chains, and competitive dynamics."
        ),
        capabilities=[
            "industry.analysis",
            "industry.research",
            "industry.structure",
            "industry.market_size",
            "industry.competitors",
            "industry.competitive_landscape",
            "industry.trends",
            "industry.supply_chain",
            "industry.porter_analysis",
        ],
    )

    # ========================================================================
    # News
    # ========================================================================

    registry.register(
        agent_name="news",
        agent_class=NewsAgent,
        category="research",
        display_name="News Research Agent",
        description=(
            "Researches recent company and market news, events, "
            "earnings, regulation, litigation, partnerships, "
            "insider activity, analyst updates, and sentiment."
        ),
        capabilities=[
            "news.research",
            "news.analysis",
            "news.events",
            "news.earnings",
            "news.regulation",
            "news.litigation",
            "news.partnerships",
            "news.insider_activity",
            "news.analyst_updates",
            "news.sentiment",
        ],
    )

    # ========================================================================
    # Macro
    # ========================================================================

    registry.register(
        agent_name="macro",
        agent_class=MacroAgent,
        category="research",
        display_name="Macro Research Agent",
        description=(
            "Analyzes macroeconomic conditions including rates, "
            "inflation, GDP, employment, currencies, commodities, "
            "and market sentiment."
        ),
        capabilities=[
            "macro.analysis",
            "macro.economic_conditions",
            "macro.interest_rates",
            "macro.inflation",
            "macro.gdp",
            "macro.employment",
            "macro.currencies",
            "macro.commodities",
            "macro.market_sentiment",
        ],
    )

    # ========================================================================
    # Valuation
    # ========================================================================

    registry.register(
        agent_name="valuation",
        agent_class=ValuationAgent,
        category="analysis",
        display_name="Valuation Agent",
        description=(
            "Performs valuation analysis including DCF, "
            "comparables, multiples, and sensitivity analysis."
        ),
        capabilities=[
            "valuation.analysis",
            "valuation.dcf",
            "valuation.comparables",
            "valuation.multiples",
            "valuation.sensitivity",
        ],
    )

    # ========================================================================
    # Risk
    # ========================================================================

    registry.register(
        agent_name="risk",
        agent_class=RiskAgent,
        category="analysis",
        display_name="Risk Agent",
        description=(
            "Identifies and evaluates financial, operational, "
            "regulatory, geopolitical, ESG, macro, and "
            "scenario-based risks."
        ),
        capabilities=[
            "risk.analysis",
            "risk.financial",
            "risk.operational",
            "risk.regulatory",
            "risk.geopolitical",
            "risk.esg",
            "risk.macro",
            "risk.scenario_analysis",
        ],
    )

    # ========================================================================
    # Evidence
    # ========================================================================

    registry.register(
        agent_name="evidence",
        agent_class=EvidenceAgent,
        category="intelligence",
        display_name="Evidence Agent",
        description=(
            "Collects, matches, verifies, and evaluates "
            "research evidence and sources."
        ),
        capabilities=[
            "evidence.collect",
            "evidence.collection",
            "evidence.match",
            "evidence.verify",
            "evidence.citations",
            "evidence.source_quality",
            "evidence.conflict_detection",
        ],
    )

    # ========================================================================
    # Investment Committee
    # ========================================================================

    registry.register(
        agent_name="investment_committee",
        agent_class=InvestmentCommitteeAgent,
        category="decision",
        display_name="Investment Committee Agent",
        description=(
            "Synthesizes research into an investment thesis, "
            "recommendation, confidence assessment, and "
            "committee-style investment decision."
        ),
        capabilities=[
            "investment.thesis",
            "investment.decision",
            "investment.recommendation",
            "investment.confidence",
            "investment.debate",
            "investment.voting",
        ],
    )

    # ========================================================================
    # Critic
    # ========================================================================

    registry.register(
        agent_name="critic",
        agent_class=CriticAgent,
        category="quality",
        display_name="Research Critic Agent",
        description=(
            "Reviews research quality, evidence, citations, "
            "hallucinations, consistency, and overall "
            "research reliability."
        ),
        capabilities=[
            "research.critique",
            "quality.review",
            "quality.verification",
            "quality.scoring",
            "quality.hallucination_detection",
            "quality.citation_review",
        ],
    )

    # ========================================================================
    # Registry Validation
    # ========================================================================

    registry.validate()

    _verify_registry(registry)

    # ========================================================================
    # Logging
    # ========================================================================

    logger.info(
        "Agent registry loaded successfully | "
        "agents=%d | capabilities=%d",
        len(registry.get_all()),
        len(registry.list_agent_names()),
        len(registry.list_capabilities()),
    )

    for metadata in registry.get_all():
        logger.info(
            "Agent registered | "
            "agent_name=%s | "
            "category=%s | "
            "capabilities=%s | "
            "enabled=%s",
            metadata.agent_id,
            metadata.category,
            metadata.capabilities,
            metadata.enabled,
        )

    return registry


# ============================================================================
# Registry Verification
# ============================================================================


def _verify_registry(
    registry: AgentRegistry,
) -> None:
    """
    Verify all required production agents and capability mappings.
    """

    # ========================================================================
    # Required Agents
    # ========================================================================

    expected_agents = {
        "planner",
        "company",
        "financial",
        "industry",
        "macro",
        "news",
        "risk",
        "valuation",
        "evidence",
        "critic",
        "investment_committee",
    }

    registered_agents = set(
        registry.list_agent_names()
    )

    missing_agents = (
        expected_agents - registered_agents
    )

    if missing_agents:
        raise RuntimeError(
            "Agent registry is missing required agents: "
            f"{sorted(missing_agents)}"
        )

    # ========================================================================
    # Required Capability -> Agent
    # ========================================================================

    expected_capabilities = {
        "company.research": "company",
        "financial.analysis": "financial",
        "industry.analysis": "industry",
        "macro.analysis": "macro",
        "news.research": "news",
        "risk.analysis": "risk",
        "valuation.analysis": "valuation",
        "evidence.verify": "evidence",
        "research.critique": "critic",
        "investment.decision": "investment_committee",
    }

    for (
        capability,
        expected_agent_name,
    ) in expected_capabilities.items():

        actual_agent_name = (
            registry.get_agent_name_for_capability(
                capability
            )
        )

        if actual_agent_name != expected_agent_name:
            raise RuntimeError(
                f"Invalid registry mapping for "
                f"'{capability}': expected agent "
                f"'{expected_agent_name}', got "
                f"'{actual_agent_name}'"
            )

    # ========================================================================
    # Every Agent Must Have a Capability
    # ========================================================================

    for metadata in registry.get_all():

        if not metadata.capabilities:
            raise RuntimeError(
                f"Agent '{metadata.agent_id}' has no capabilities"
            )

    # ========================================================================
    # Every Capability Must Resolve
    # ========================================================================

    for capability in registry.list_capabilities():

        metadata = registry.get_agent_for_capability(
            capability
        )

        if metadata is None:
            raise RuntimeError(
                f"Capability '{capability}' does not resolve "
                "to an agent."
            )

    # ========================================================================
    # Every Registered Agent Must Resolve by Name
    # ========================================================================

    for agent_name in registry.list_agent_names():

        metadata = registry.get_agent_for_name(
            agent_name
        )

        if metadata.agent_id != agent_name:
            raise RuntimeError(
                f"Agent name mismatch: registry key "
                f"'{agent_name}' maps to metadata "
                f"'{metadata.agent_id}'."
            )

    logger.info(
        "Agent registry verification passed | "
        "agents=%d | capabilities=%d",
        len(registry.get_all()),
        len(registry.list_capabilities()),
    )

