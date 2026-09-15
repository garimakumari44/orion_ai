"""
app/agents/news/agent.py

News & Events Intelligence Agent.

Responsibilities:
- Retrieve company news and event information through AgentServices
- Analyze earnings announcements
- Analyze major corporate events
- Detect market-moving information
- Produce structured news intelligence
- Return the canonical AgentResult

Architecture:

    NewsAgent
        ↓
    AgentContext
        ↓
    AgentServices
        ↓
    News Research / Retrieval
        ↓
    EarningsAnalyzer
    EventAnalyzer
        ↓
    News Analysis
        ↓
    AgentResult
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_services import AgentServices
from app.agents.base.base_agent import BaseAgent

from app.agents.news.earnings import EarningsAnalyzer
from app.agents.news.events import EventAnalyzer


logger = logging.getLogger(__name__)


class NewsAgent(BaseAgent):
    """
    News & Events Intelligence Agent.

    The agent itself does not own retrieval infrastructure.

    Retrieval, knowledge access, tools, memory, LLM access, etc.
    are provided through AgentServices.

    Deterministic news analyzers remain local to this agent.
    """

    name = "news_agent"

    description = (
        "Analyzes company news, earnings, events, regulatory "
        "updates and market-moving information."
    )

    def __init__(
        self,
        services: AgentServices,
    ) -> None:
        super().__init__(
            services=services
        )

        self.earnings_analyzer = EarningsAnalyzer()
        self.event_analyzer = EventAnalyzer()

    async def execute(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Execute news analysis.

        Canonical flow:

            AgentContext
                ↓
            news research/retrieval
                ↓
            deterministic analyzers
                ↓
            structured result
                ↓
            AgentResult
        """

        company = self._resolve_company(context)

        if not company:
            return AgentResult.failure(
                error="Company information required for news analysis",
                agent=self.name,
            )

        logger.info(
            "Running News Analysis for %s",
            company,
        )

        try:
            news_data = await self._retrieve_news(
                context=context,
                company=company,
            )

            earnings = await self.earnings_analyzer.analyze(
                news_data
            )

            events = await self.event_analyzer.analyze(
                news_data
            )

            summary = self.generate_summary(
                earnings=earnings,
                events=events,
            )

            result = {
                "agent": self.name,
                "company": company,
                "news": news_data,
                "earnings": earnings,
                "events": events,
                "summary": summary,
            }

            return AgentResult.success(
                data=result,
                agent=self.name,
            )

        except Exception as exc:
            logger.exception(
                "News analysis failed for %s",
                company,
            )

            return AgentResult.failure(
                error=str(exc),
                agent=self.name,
            )

    # ------------------------------------------------------------------
    # Company resolution
    # ------------------------------------------------------------------

    def _resolve_company(
        self,
        context: AgentContext,
    ) -> Any:
        """
        Resolve company information from AgentContext.

        AgentContext is the canonical source of task data.
        """

        data = context.data or {}

        company = data.get("company")

        if company:
            return company

        # Some execution flows may provide company_id rather than
        # a fully hydrated company object.
        return data.get("company_id")

    # ------------------------------------------------------------------
    # News retrieval
    # ------------------------------------------------------------------

    async def _retrieve_news(
        self,
        context: AgentContext,
        company: Any,
    ) -> Dict[str, Any]:
        """
        Retrieve news through the shared service boundary.

        NewsAgent does not directly instantiate a news provider,
        HTTP client, scraper, MCP client, or retrieval engine.
        """

        services = context.services

        if services is None:
            raise RuntimeError(
                "AgentServices are required for NewsAgent"
            )

        # Prefer a dedicated news research capability when available.
        news_research = getattr(
            services,
            "news_research",
            None,
        )

        if news_research is not None:
            return await news_research.research(
                company=company,
                context=context,
            )

        # Fall back to the shared retrieval capability.
        retrieval = getattr(
            services,
            "retrieval",
            None,
        )

        if retrieval is not None:
            return await retrieval.retrieve(
                query=self._build_news_query(company),
                context=context,
            )

        # Finally allow the shared tool layer to provide news.
        tools = getattr(
            services,
            "tools",
            None,
        )

        if tools is not None:
            return await tools.execute(
                tool_name="news_search",
                arguments={
                    "company": company,
                },
                context=context,
            )

        raise RuntimeError(
            "News research/retrieval service is not configured "
            "in AgentServices."
        )

    def _build_news_query(
        self,
        company: Any,
    ) -> str:
        """
        Build a retrieval query for company news.
        """

        if isinstance(company, dict):
            name = (
                company.get("name")
                or company.get("company_name")
                or company.get("ticker")
                or company.get("symbol")
            )
        else:
            name = str(company)

        return (
            f"Latest news, earnings announcements, "
            f"corporate events, regulatory updates and "
            f"market-moving information for {name}"
        )

    # ------------------------------------------------------------------
    # News synthesis
    # ------------------------------------------------------------------

    def generate_summary(
        self,
        earnings: Dict[str, Any],
        events: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate deterministic news summary.
        """

        return {
            "earnings_signal": earnings.get("signal"),
            "event_risk": events.get("risk"),
            "market_impact": self.calculate_market_impact(
                earnings=earnings,
                events=events,
            ),
        }

    def calculate_market_impact(
        self,
        earnings: Dict[str, Any],
        events: Dict[str, Any],
    ) -> str:
        """
        Calculate deterministic market-impact level.
        """

        score = 0

        if earnings.get("surprise"):
            score += 1

        if events.get("major_event"):
            score += 1

        if score >= 2:
            return "HIGH"

        if score == 1:
            return "MEDIUM"

        return "LOW"