"""
app/agents/industry/agent.py

Industry Research Agent.

Performs deep industry and competitive research for equity analysis.

Canonical execution flow:

    ExecutionEngine
          |
          v
      AgentContext
          |
          v
    IndustryAgent
          |
          v
      AgentServices
          |
          v
    IndustryResearchService
          |
          v
    IndustryCatalogService
          |
          +-------------------------+
          |                         |
          v                         v
    IndustryCatalogRepository   IndustryProcessingPipeline
                                      |
                                      v
                              IndustryProviderManager
                                      |
                                      v
                              Structured Industry Data
                                      |
                                      v
                    +-----------------------------+
                    | PorterAnalyzer              |
                    | MarketSizeAnalyzer          |
                    | CompetitorAnalyzer           |
                    | SupplyChainAnalyzer          |
                    | TrendAnalyzer               |
                    +-----------------------------+
                                      |
                                      v
                                IndustryReport
                                      |
                                      v
                                  AgentResult


Architectural rules:

1. IndustryAgent receives only AgentContext at runtime.
2. IndustryAgent does not receive Task directly.
3. IndustryAgent does not construct AgentContext.
4. IndustryAgent does not construct AgentServices.
5. IndustryAgent does not perform provider retrieval directly.
6. IndustryAgent does not access IndustryProviderManager directly.
7. IndustryAgent does not access IndustryCatalogRepository directly.
8. Industry research is obtained through AgentServices.
9. IndustryCatalogService is owned by IndustryResearchService.
10. Deterministic industry analyzers remain local to the agent.
11. Canonical runtime identity comes from AgentContext.
12. AgentResult is created through canonical factory methods.
13. Company identity and industry identity are not inferred from
    supplemental metadata.
14. Sector is NOT treated as industry.
15. Industry resolution belongs to the catalog/research layer,
    not this agent.
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.base_agent import BaseAgent

from app.agents.industry.competitors import CompetitorAnalyzer
from app.agents.industry.market_size import MarketSizeAnalyzer
from app.agents.industry.models import IndustryReport
from app.agents.industry.porter_analysis import PorterAnalyzer
from app.agents.industry.supply_chain import SupplyChainAnalyzer
from app.agents.industry.trends import TrendAnalyzer


logger = logging.getLogger(__name__)


class IndustryAgent(BaseAgent):
    """
    Industry & Competitor Research Agent.

    Responsibilities:

    - Request industry research through AgentServices.
    - Analyze industry structure.
    - Evaluate competitive landscape.
    - Analyze market size.
    - Identify industry trends.
    - Analyze supply-chain dynamics.
    - Produce an IndustryReport.

    The agent owns deterministic domain analyzers.

    The agent does NOT own:

    - industry providers
    - provider selection
    - industry catalog
    - industry repository
    - industry processing pipeline
    - retrieval
    - database access
    - knowledge access
    - memory
    - MCP
    - tool orchestration
    - LLM infrastructure
    - AgentContext creation
    - AgentServices creation
    """

    # =========================================================
    # Agent Metadata
    # =========================================================

    agent_id = "industry"

    category = "research"

    name = "industry"

    display_name = "Industry & Competitor Research Agent"

    description = (
        "Performs deep industry, competitive, market-size, "
        "supply-chain, and trend research for equity analysis."
    )

    capabilities = [
        "industry.research",
        "industry.analysis",
        "competitor.analysis",
    ]

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        services: Any,
    ) -> None:
        """
        Initialize the IndustryAgent.

        AgentManager injects the canonical AgentServices instance.

        IndustryAgent does not construct application-level
        infrastructure.
        """

        super().__init__(
            services=services,
        )

        # -----------------------------------------------------
        # Deterministic domain analyzers
        # -----------------------------------------------------

        self.porter_analyzer = PorterAnalyzer()

        self.market_analyzer = MarketSizeAnalyzer()

        self.competitor_analyzer = CompetitorAnalyzer()

        self.supply_chain_analyzer = SupplyChainAnalyzer()

        self.trend_analyzer = TrendAnalyzer()

    # =========================================================
    # Execution
    # =========================================================

    async def run(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Execute industry research.

        Runtime input is exclusively AgentContext.

        IndustryAgent does not resolve the canonical industry.

        The canonical industry must already exist in:

            context.industry

        before the agent is executed.
        """

        # -----------------------------------------------------
        # Validate context
        # -----------------------------------------------------

        if context is None:
            return AgentResult.failure(
                agent_name=self.agent_id,
                task_id=None,
                error="AgentContext is required for IndustryAgent.",
            )

        # -----------------------------------------------------
        # Extract canonical runtime identifiers
        # -----------------------------------------------------

        task_id = getattr(
            context,
            "task_id",
            None,
        )

        research_id = getattr(
            context,
            "research_id",
            None,
        )

        company_id = getattr(
            context,
            "company_id",
            None,
        )

        company = getattr(
            context,
            "company",
            None,
        )

        ticker = getattr(
            context,
            "ticker",
            None,
        )

        try:
            # =================================================
            # 1. Read canonical industry
            # =================================================

            industry = self._get_canonical_industry(
                context=context,
            )

            if not industry:
                raise ValueError(
                    "IndustryAgent requires a canonical industry "
                    "in AgentContext. Industry must be resolved "
                    "before agent execution. "
                    f"research_id={research_id!r} "
                    f"company_id={company_id!r} "
                    f"company={company!r} "
                    f"ticker={ticker!r}"
                )

            # =================================================
            # 2. Log canonical runtime identity
            # =================================================

            logger.info(
                "=================================================="
            )

            logger.info(
                "INDUSTRY AGENT START"
            )

            logger.info(
                "IndustryAgent runtime context | "
                "context_object_id=%s | "
                "task_id=%r | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r | "
                "industry=%r",
                id(context),
                task_id,
                research_id,
                company_id,
                company,
                ticker,
                industry,
            )

            # =================================================
            # 3. Retrieve structured industry research
            # =================================================

            industry_data = await self._research_industry(
                context=context,
                industry=industry,
            )

            # =================================================
            # 4. Normalize research data
            # =================================================

            industry_data = self._normalize_research_data(
                industry_data,
            )

            logger.info(
                "Industry research data normalized | "
                "task_id=%r | "
                "research_id=%r | "
                "industry=%r | "
                "fields=%s",
                task_id,
                research_id,
                industry,
                sorted(industry_data.keys()),
            )

            # =================================================
            # 5. Porter analysis
            # =================================================

            porter_result = self.porter_analyzer.analyze(
                industry,
                industry_data.get(
                    "porter",
                    {},
                ),
            )

            # =================================================
            # 6. Market-size analysis
            # =================================================

            market_result = self.market_analyzer.analyze(
                industry,
                industry_data.get(
                    "market",
                    {},
                ),
            )

            # =================================================
            # 7. Competitor analysis
            # =================================================

            competitors = self.competitor_analyzer.analyze(
                industry_data.get(
                    "competitors",
                    [],
                ),
            )

            # =================================================
            # 8. Supply-chain analysis
            # =================================================

            supply_chain = self.supply_chain_analyzer.analyze(
                industry_data.get(
                    "supply_chain",
                    {},
                ),
            )

            # =================================================
            # 9. Trend analysis
            # =================================================

            trends = self.trend_analyzer.analyze(
                industry_data.get(
                    "trends",
                    [],
                ),
            )

            # =================================================
            # 10. Build IndustryReport
            # =================================================

            report = IndustryReport(
                industry=industry,
                porter_analysis=porter_result,
                market_size=market_result,
                competitors=competitors,
                trends=trends,
                supply_chain=supply_chain,
            )

            # =================================================
            # 11. Store raw industry research
            # =================================================

            self._store_data(
                context=context,
                key="industry_research",
                value=industry_data,
            )

            # =================================================
            # 12. Store final industry report
            # =================================================

            self._store_report(
                context=context,
                report=report,
            )

            # =================================================
            # 13. Preserve canonical industry
            # =================================================

            self._store_data(
                context=context,
                key="industry",
                value=industry,
            )

            # =================================================
            # 14. Build result payload
            # =================================================

            result = {
                "research_id": research_id,
                "company_id": company_id,
                "company": company,
                "ticker": ticker,
                "industry": industry,
                "industry_data": industry_data,
                "report": report,
            }

            logger.info(
                "INDUSTRY RESEARCH COMPLETED | "
                "task_id=%r | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r | "
                "industry=%r",
                task_id,
                research_id,
                company_id,
                company,
                ticker,
                industry,
            )

            logger.info(
                "AgentContext after IndustryAgent | %r",
                (
                    context.summary()
                    if hasattr(context, "summary")
                    else None
                ),
            )

            logger.info(
                "=================================================="
            )

            # =================================================
            # 15. Canonical success result
            # =================================================

            return AgentResult.success(
                agent_name=self.agent_id,
                task_id=task_id,
                data=result,
            )

        except Exception as exc:
            logger.exception(
                "=================================================="
            )

            logger.exception(
                "INDUSTRY AGENT FAILED"
            )

            logger.exception(
                "exception_type=%s",
                type(exc).__name__,
            )

            logger.exception(
                "exception=%s",
                str(exc),
            )

            logger.exception(
                "task_id=%r",
                task_id,
            )

            logger.exception(
                "research_id=%r",
                research_id,
            )

            logger.exception(
                "company_id=%r",
                company_id,
            )

            logger.exception(
                "company=%r",
                company,
            )

            logger.exception(
                "ticker=%r",
                ticker,
            )

            logger.exception(
                "industry=%r",
                getattr(
                    context,
                    "industry",
                    None,
                ),
            )

            try:
                context_summary = (
                    context.summary()
                    if hasattr(context, "summary")
                    else None
                )
            except Exception:
                context_summary = None

            logger.exception(
                "context_summary=%r",
                context_summary,
            )

            logger.exception(
                "=================================================="
            )

            return AgentResult.failure(
                agent_name=self.agent_id,
                task_id=task_id,
                error=str(exc),
            )

    # =========================================================
    # Canonical Industry Access
    # =========================================================

    @staticmethod
    def _get_canonical_industry(
        context: AgentContext,
    ) -> str | None:
        """
        Read the canonical industry from AgentContext.

        Industry resolution happens before agent execution.

        Canonical flow:

            CompanyRepository
                    |
                    v
            ResearchService
                    |
                    v
            IndustryCatalogService
                    |
                    v
              AgentContext.industry
                    |
                    v
              IndustryAgent

        IndustryAgent intentionally does NOT use:

            context.metadata["industry"]
            context.data["industry"]
            context.data["company_research"]["industry"]
            context.data["company"]["industry"]
            context.data["sector"]
            context.metadata["sector"]

        Sector is never treated as industry.
        """

        if context is None:
            return None

        industry = getattr(
            context,
            "industry",
            None,
        )

        if industry is None:
            return None

        industry = str(
            industry
        ).strip()

        return industry or None

    # =========================================================
    # Industry Research Capability
    # =========================================================

    async def _research_industry(
        self,
        context: AgentContext,
        industry: str,
    ) -> dict[str, Any]:
        """
        Retrieve structured industry research through
        AgentServices.

        The dependency chain is:

            AgentServices
                |
                v
            IndustryResearchService
                |
                v
            IndustryCatalogService
                |
                +---- IndustryCatalogRepository
                |
                +---- IndustryProcessingPipeline
                            |
                            v
                    IndustryProviderManager

        IndustryAgent does not directly access any of these
        infrastructure components.
        """

        services = getattr(
            self,
            "services",
            None,
        )

        if services is None:
            raise RuntimeError(
                "IndustryAgent requires injected AgentServices."
            )

        industry_research = getattr(
            services,
            "industry_research",
            None,
        )

        if industry_research is None:
            raise RuntimeError(
                "Industry research capability is not configured "
                "in AgentServices. Expected "
                "services.industry_research."
            )

        task_id = getattr(
            context,
            "task_id",
            None,
        )

        research_id = getattr(
            context,
            "research_id",
            None,
        )

        company_id = getattr(
            context,
            "company_id",
            None,
        )

        company = getattr(
            context,
            "company",
            None,
        )

        ticker = getattr(
            context,
            "ticker",
            None,
        )

        metadata = getattr(
            context,
            "metadata",
            None,
        )

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        logger.info(
            "IndustryAgent -> IndustryResearchService | "
            "task_id=%r | "
            "research_id=%r | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "industry=%r",
            task_id,
            research_id,
            company_id,
            company,
            ticker,
            industry,
        )

        # =====================================================
        # Preferred research API
        # =====================================================

        research_method = getattr(
            industry_research,
            "research",
            None,
        )

        if callable(
            research_method
        ):
            result = await self._invoke_research_method(
                research_method=research_method,
                context=context,
                industry=industry,
                company=company,
                ticker=ticker,
                company_id=company_id,
                research_id=research_id,
                metadata=metadata,
            )

            return self._extract_research_data(
                result,
            )

        # =====================================================
        # Compatibility research API
        # =====================================================

        research_industry_method = getattr(
            industry_research,
            "research_industry",
            None,
        )

        if callable(
            research_industry_method
        ):
            result = await self._invoke_research_method(
                research_method=research_industry_method,
                context=context,
                industry=industry,
                company=company,
                ticker=ticker,
                company_id=company_id,
                research_id=research_id,
                metadata=metadata,
            )

            return self._extract_research_data(
                result,
            )

        raise RuntimeError(
            "Configured industry_research capability does not "
            "implement research() or research_industry()."
        )

    # =========================================================
    # Research Method Invocation
    # =========================================================

    @staticmethod
    async def _invoke_research_method(
        research_method: Any,
        *,
        context: AgentContext,
        industry: str,
        company: str | None,
        ticker: str | None,
        company_id: Any,
        research_id: Any,
        metadata: dict[str, Any],
    ) -> Any:
        """
        Invoke the configured research method safely.

        Only keyword arguments accepted by the actual method
        signature are passed.

        This prevents errors such as:

            unexpected keyword argument 'context'

        when an implementation exposes a narrower API.
        """

        candidate_kwargs: dict[str, Any] = {
            "industry": industry,
            "company": company,
            "ticker": ticker,
            "company_id": company_id,
            "research_id": research_id,
            "metadata": metadata,
            "context": context,
        }

        try:
            signature = inspect.signature(
                research_method
            )
        except (TypeError, ValueError):
            signature = None

        if signature is not None:

            parameters = signature.parameters

            accepts_kwargs = any(
                parameter.kind
                == inspect.Parameter.VAR_KEYWORD
                for parameter in parameters.values()
            )

            if not accepts_kwargs:
                candidate_kwargs = {
                    key: value
                    for key, value in candidate_kwargs.items()
                    if key in parameters
                }

        result = research_method(
            **candidate_kwargs
        )

        if inspect.isawaitable(
            result
        ):
            result = await result

        return result

    # =========================================================
    # Research Result Extraction
    # =========================================================

    @staticmethod
    def _extract_research_data(
        result: Any,
    ) -> dict[str, Any]:
        """
        Normalize an industry research capability response
        into a dictionary.

        Supported response shapes:

            dict

            object.data -> dict

            object.result -> dict
        """

        if result is None:
            return {}

        # -----------------------------------------------------
        # Direct dictionary
        # -----------------------------------------------------

        if isinstance(
            result,
            dict,
        ):
            return dict(
                result
            )

        # -----------------------------------------------------
        # Result object with `.data`
        # -----------------------------------------------------

        data = getattr(
            result,
            "data",
            None,
        )

        if isinstance(
            data,
            dict,
        ):
            return dict(
                data
            )

        # -----------------------------------------------------
        # Result object with `.result`
        # -----------------------------------------------------

        payload = getattr(
            result,
            "result",
            None,
        )

        if isinstance(
            payload,
            dict,
        ):
            return dict(
                payload
            )

        raise TypeError(
            "Industry research capability returned an "
            "unsupported result type: "
            f"{type(result).__name__}"
        )

    # =========================================================
    # Research Data Normalization
    # =========================================================

    @staticmethod
    def _normalize_research_data(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ensure deterministic analyzers receive stable
        input structures.

        Canonical normalized structure:

            {
                "porter": {},
                "market": {},
                "competitors": [],
                "supply_chain": {},
                "trends": [],
                ...
            }
        """

        if not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "Industry research data must be a dictionary."
            )

        # -----------------------------------------------------
        # IndustryResearchService may return normalized
        # provider data under:
        #
        #     data["data"]
        #
        # Unwrap it when present.
        # -----------------------------------------------------

        nested_data = data.get(
            "data"
        )

        if isinstance(
            nested_data,
            dict,
        ):
            normalized = dict(
                nested_data
            )

            # Preserve top-level identity/source fields.
            for key in (
                "research_id",
                "company_id",
                "company",
                "ticker",
                "industry",
                "industry_name",
                "industry_source",
                "industry_confidence",
                "metadata",
                "providers",
            ):
                if key in data:
                    normalized.setdefault(
                        key,
                        data[key],
                    )

        else:
            normalized = dict(
                data
            )

        # -----------------------------------------------------
        # Porter
        # -----------------------------------------------------

        porter = normalized.get(
            "porter",
            {},
        )

        if not isinstance(
            porter,
            dict,
        ):
            porter = {}

        # -----------------------------------------------------
        # Market
        # -----------------------------------------------------

        market = normalized.get(
            "market",
            {},
        )

        if not isinstance(
            market,
            dict,
        ):
            market = {}

        # -----------------------------------------------------
        # Compatibility with market_size
        # -----------------------------------------------------

        if not market:

            market_size = normalized.get(
                "market_size",
            )

            if isinstance(
                market_size,
                dict,
            ):
                market = dict(
                    market_size
                )

            elif market_size is not None:
                market = {
                    "market_size": market_size,
                }

        # -----------------------------------------------------
        # Competitors
        # -----------------------------------------------------

        competitors = normalized.get(
            "competitors",
            [],
        )

        if competitors is None:
            competitors = []

        elif isinstance(
            competitors,
            tuple,
        ):
            competitors = list(
                competitors
            )

        elif not isinstance(
            competitors,
            list,
        ):
            competitors = [
                competitors
            ]

        # -----------------------------------------------------
        # Supply Chain
        # -----------------------------------------------------

        supply_chain = normalized.get(
            "supply_chain",
            {},
        )

        if not isinstance(
            supply_chain,
            dict,
        ):
            supply_chain = {}

        # -----------------------------------------------------
        # Trends
        # -----------------------------------------------------

        trends = normalized.get(
            "trends",
            [],
        )

        if trends is None:
            trends = []

        elif isinstance(
            trends,
            tuple,
        ):
            trends = list(
                trends
            )

        elif not isinstance(
            trends,
            list,
        ):
            trends = [
                trends
            ]

        # -----------------------------------------------------
        # Guarantee analyzer-compatible fields.
        # -----------------------------------------------------

        normalized.update(
            {
                "porter": porter,
                "market": market,
                "competitors": competitors,
                "supply_chain": supply_chain,
                "trends": trends,
            }
        )

        return normalized

    # =========================================================
    # Context Data Persistence
    # =========================================================

    @staticmethod
    def _store_data(
        context: AgentContext,
        key: str,
        value: Any,
    ) -> None:
        """
        Store runtime data in AgentContext.

        Preferred API:

            context.set_data(key, value)

        Compatibility fallback:

            context.data[key] = value
        """

        if context is None:
            raise RuntimeError(
                "Cannot store data without AgentContext."
            )

        # -----------------------------------------------------
        # Preferred AgentContext API
        # -----------------------------------------------------

        set_data = getattr(
            context,
            "set_data",
            None,
        )

        if callable(
            set_data
        ):
            set_data(
                key,
                value,
            )
            return

        # -----------------------------------------------------
        # Compatibility fallback
        # -----------------------------------------------------

        data = getattr(
            context,
            "data",
            None,
        )

        if isinstance(
            data,
            dict,
        ):
            data[key] = value
            return

        raise RuntimeError(
            "AgentContext does not provide set_data() "
            "or a writable data mapping."
        )

    # =========================================================
    # Industry Report Persistence
    # =========================================================

    @staticmethod
    def _store_report(
        context: AgentContext,
        report: IndustryReport,
    ) -> None:
        """
        Store the domain IndustryReport in AgentContext.
        """

        if report is None:
            raise ValueError(
                "Industry report cannot be None."
            )

        IndustryAgent._store_data(
            context=context,
            key="industry_report",
            value=report,
        )