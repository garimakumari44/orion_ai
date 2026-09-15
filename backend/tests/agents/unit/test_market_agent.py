"""
Unit tests for MarketAgent.
"""

from __future__ import annotations

import pytest

from app.agents.base.agent_context import AgentContext
from app.agents.market.market_agent import MarketAgent


@pytest.fixture
def agent() -> MarketAgent:
    """Create a MarketAgent instance."""
    return MarketAgent()


@pytest.fixture
def context() -> AgentContext:
    """Create a basic AgentContext."""
    return AgentContext(
        query="Analyze NVIDIA",
        task="Analyze NVIDIA",
        metadata={},
    )


# ---------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------


def test_market_agent_initialization(agent: MarketAgent) -> None:
    """Agent initializes correctly."""

    assert agent.name == "market"

    assert "market research" in agent.description.lower()

    assert len(agent.capabilities) == 10

    assert agent.supports("company_analysis")
    assert agent.supports("market_research")
    assert agent.supports("competitor_analysis")
    assert agent.supports("industry_analysis")
    assert agent.supports("stock_analysis")
    assert agent.supports("financial_summary")
    assert agent.supports("economic_indicators")
    assert agent.supports("market_news")
    assert agent.supports("trend_analysis")
    assert agent.supports("investment_research")


# ---------------------------------------------------------------------
# Execute routing
# ---------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "capability",
    [
        "company_analysis",
        "market_research",
        "competitor_analysis",
        "industry_analysis",
        "stock_analysis",
        "financial_summary",
        "economic_indicators",
        "market_news",
        "trend_analysis",
        "investment_research",
    ],
)
async def test_execute_supported_capabilities(
    agent: MarketAgent,
    context: AgentContext,
    capability: str,
) -> None:
    """Every supported capability should route correctly."""

    context.metadata = {"capability": capability}

    result = await agent.execute(context)

    assert result["success"] is True
    assert result["agent"] == "market"
    assert result["operation"] == capability
    assert result["query"] == context.task
    assert result["parameters"]["capability"] == capability
    assert result["status"] == "pending_tool_execution"


@pytest.mark.asyncio
async def test_execute_unknown_capability(
    agent: MarketAgent,
    context: AgentContext,
) -> None:
    """Unknown capability should return an error."""

    context.metadata = {"capability": "unknown"}

    result = await agent.execute(context)

    assert result["success"] is False
    assert result["agent"] == "market"
    assert "Unsupported capability" in result["error"]


# ---------------------------------------------------------------------
# Individual handlers
# ---------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_name,operation",
    [
        ("company_analysis", "company_analysis"),
        ("market_research", "market_research"),
        ("competitor_analysis", "competitor_analysis"),
        ("industry_analysis", "industry_analysis"),
        ("stock_analysis", "stock_analysis"),
        ("financial_summary", "financial_summary"),
        ("economic_indicators", "economic_indicators"),
        ("market_news", "market_news"),
        ("trend_analysis", "trend_analysis"),
        ("investment_research", "investment_research"),
    ],
)
async def test_individual_handlers(
    agent: MarketAgent,
    context: AgentContext,
    method_name: str,
    operation: str,
) -> None:
    """Each handler should produce the standardized response."""

    handler = getattr(agent, method_name)

    result = await handler(context)

    assert result["success"] is True
    assert result["agent"] == "market"
    assert result["operation"] == operation
    assert result["query"] == context.task
    assert result["status"] == "pending_tool_execution"


# ---------------------------------------------------------------------
# _response helper
# ---------------------------------------------------------------------


def test_response_helper_uses_task(
    agent: MarketAgent,
    context: AgentContext,
) -> None:
    """Task should take precedence over query."""

    context.task = "Analyze Tesla"
    context.query = "Ignored"

    result = agent._response("company_analysis", context)

    assert result["query"] == "Analyze Tesla"


def test_response_helper_falls_back_to_query(
    agent: MarketAgent,
    context: AgentContext,
) -> None:
    """Query should be used if task is empty."""

    context.task = ""
    context.query = "Analyze Apple"

    result = agent._response("company_analysis", context)

    assert result["query"] == "Analyze Apple"


def test_response_preserves_metadata(
    agent: MarketAgent,
    context: AgentContext,
) -> None:
    """Metadata should be preserved."""

    context.metadata = {
        "capability": "market_research",
        "ticker": "NVDA",
        "country": "US",
    }

    result = agent._response("market_research", context)

    assert result["parameters"] == context.metadata