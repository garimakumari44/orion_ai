
"""
app/agents/macro/agent.py

Macro Research Agent.

Performs macroeconomic research for equity analysis.

Canonical execution flow:

    ExecutionEngine
          |
          v
    AgentContext
          |
          v
    MacroAgent
          |
          v
    AgentServices
          |
          v
    Macro Research Capability
          |
          v
    Retrieved / Structured Macro Data
          |
          v
    ┌─────────────────────────────┐
    │ InflationAnalyzer           │
    │ RatesAnalyzer               │
    │ Future Macro Analyzers      │
    └─────────────────────────────┘
          |
          v
    MacroReport
          |
          v
    AgentResult
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.base_agent import BaseAgent

from app.agents.macro.inflation import InflationAnalyzer
from app.agents.macro.rates import RatesAnalyzer


logger = logging.getLogger(__name__)


class MacroAgent(BaseAgent):
    """
    Macro Research Agent.

    Responsibilities
    ----------------
    - Analyze global and regional macroeconomic conditions
    - Evaluate inflation environment
    - Analyze interest-rate cycles
    - Identify macroeconomic risks
    - Analyze economic cycles
    - Evaluate market environment
    - Provide macro inputs to downstream research agents

    Architectural responsibilities
    -------------------------------
    MacroAgent owns deterministic macroeconomic analyzers.

    It does NOT own:

        - AgentContext creation
        - retrieval infrastructure
        - knowledge infrastructure
        - memory
        - MCP
        - external data providers
        - tool orchestration
        - LLM infrastructure

    Those capabilities are provided through AgentServices.
    """

    agent_id = "macro"
    name = "macro"

    description = (
        "Analyzes macroeconomic factors including inflation, "
        "interest rates, GDP growth, employment, commodities, "
        "currencies, economic cycles, and market environment."
    )

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        # Deterministic domain analyzers.
        self.inflation_analyzer = InflationAnalyzer()
        self.rates_analyzer = RatesAnalyzer()

    async def run(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Execute macro research.

        The public lifecycle is owned by BaseAgent.execute().
        This method contains only MacroAgent-specific execution logic.

        Macro context is resolved from AgentContext rather than from
        a separate `company`, `region`, or arbitrary dictionary argument.
        """

        company = self._get_company(context)
        region = self._get_region(context)

        logger.info(
            "Starting macro research",
            extra={
                "agent_id": self.agent_id,
                "task_id": getattr(context, "task_id", None),
                "company": company,
                "region": region,
            },
        )

        # --------------------------------------------------------------
        # 1. Retrieve macro research through shared services
        # --------------------------------------------------------------

        macro_data = await self._research_macro(
            context=context,
            company=company,
            region=region,
        )

        macro_data = self._normalize_macro_data(
            macro_data
        )

        # --------------------------------------------------------------
        # 2. Deterministic macro analysis
        # --------------------------------------------------------------

        inflation_result = await self._run_inflation_analysis(
            region=region,
            data=macro_data.get("inflation", {}),
        )

        rates_result = await self._run_rates_analysis(
            region=region,
            data=macro_data.get("interest_rates", {}),
        )

        # --------------------------------------------------------------
        # 3. Build macro report
        # --------------------------------------------------------------

        report = {
            "company": company,
            "region": region,
            "inflation": inflation_result,
            "interest_rates": rates_result,
            "economic_cycle": macro_data.get(
                "economic_cycle",
                {},
            ),
            "gdp": macro_data.get(
                "gdp",
                {},
            ),
            "employment": macro_data.get(
                "employment",
                {},
            ),
            "commodities": macro_data.get(
                "commodities",
                {},
            ),
            "currencies": macro_data.get(
                "currencies",
                {},
            ),
            "market_environment": macro_data.get(
                "market_environment",
                {},
            ),
            "macro_risks": macro_data.get(
                "macro_risks",
                [],
            ),
        }

        # --------------------------------------------------------------
        # 4. Store report in AgentContext
        # --------------------------------------------------------------

        self._store_report(
            context=context,
            report=report,
        )

        logger.info(
            "Macro research completed",
            extra={
                "agent_id": self.agent_id,
                "task_id": getattr(context, "task_id", None),
                "company": company,
                "region": region,
            },
        )

        # --------------------------------------------------------------
        # 5. Return canonical AgentResult
        # --------------------------------------------------------------

        return AgentResult(
            success=True,
            agent_id=self.agent_id,
            task_id=getattr(context, "task_id", None),
            data={
                "company": company,
                "region": region,
                "macro_analysis": report,
            },
            metadata={
                "analysis_type": "macro_research",
                "analyzers": [
                    "inflation",
                    "interest_rates",
                ],
            },
        )

    # ==================================================================
    # Context resolution
    # ==================================================================

    @staticmethod
    def _get_company(
        context: AgentContext,
    ) -> str | None:
        """
        Resolve company from AgentContext.

        Company is optional for pure macro research, but may be useful
        when macro analysis is being performed as part of an equity
        research workflow.
        """

        company = getattr(
            context,
            "company",
            None,
        )

        if company:
            return str(company)

        data = getattr(
            context,
            "data",
            None,
        )

        if isinstance(data, dict):
            company = data.get("company")

            if company:
                return str(company)

        return None

    @staticmethod
    def _get_region(
        context: AgentContext,
    ) -> str | None:
        """
        Resolve geographic region from AgentContext.
        """

        region = getattr(
            context,
            "region",
            None,
        )

        if region:
            return str(region)

        data = getattr(
            context,
            "data",
            None,
        )

        if isinstance(data, dict):
            region = data.get("region")

            if region:
                return str(region)

        return None

    # ==================================================================
    # Macro research capability
    # ==================================================================

    async def _research_macro(
        self,
        context: AgentContext,
        company: str | None,
        region: str | None,
    ) -> Dict[str, Any]:
        """
        Retrieve structured macroeconomic research through
        AgentServices.

        MacroAgent does not implement retrieval itself.

        Expected capability:

            context.services.macro_research

        That capability may internally use:

            Knowledge
            Adaptive Retrieval
            Market Data
            News
            Memory
            MCP
            External economic data providers
        """

        services = getattr(
            context,
            "services",
            None,
        )

        if services is None:
            raise RuntimeError(
                "MacroAgent requires AgentContext.services."
            )

        macro_research = getattr(
            services,
            "macro_research",
            None,
        )

        if macro_research is None:
            raise RuntimeError(
                "Macro research service is not configured "
                "in AgentServices. Expected "
                "services.macro_research."
            )

        # Preferred capability API.
        if hasattr(macro_research, "research"):
            result = macro_research.research(
                company=company,
                region=region,
                context=context,
            )

            if hasattr(result, "__await__"):
                result = await result

            return self._extract_research_data(result)

        # Compatibility API.
        if hasattr(macro_research, "analyze"):
            result = macro_research.analyze(
                company=company,
                region=region,
                context=context,
            )

            if hasattr(result, "__await__"):
                result = await result

            return self._extract_research_data(result)

        raise RuntimeError(
            "Configured macro_research capability does not expose "
            "a supported research method."
        )

    @staticmethod
    def _extract_research_data(
        result: Any,
    ) -> Dict[str, Any]:
        """
        Normalize a macro research service response into a dictionary.
        """

        if result is None:
            return {}

        if isinstance(result, dict):
            return result

        data = getattr(
            result,
            "data",
            None,
        )

        if isinstance(data, dict):
            return data

        payload = getattr(
            result,
            "result",
            None,
        )

        if isinstance(payload, dict):
            return payload

        raise TypeError(
            "Macro research capability returned an unsupported "
            f"result type: {type(result).__name__}"
        )

    # ==================================================================
    # Analyzer execution
    # ==================================================================

    async def _run_inflation_analysis(
        self,
        region: str | None,
        data: Dict[str, Any],
    ) -> Any:
        """
        Run the inflation analyzer.

        The analyzer currently accepts only region. The data argument
        is retained at the agent boundary so the analyzer can later
        consume structured retrieved data without changing the
        MacroAgent architecture.
        """

        try:
            return await self.inflation_analyzer.analyze(
                region=region,
                data=data,
            )
        except TypeError:
            # Compatibility with the current analyzer contract.
            return await self.inflation_analyzer.analyze(
                region=region,
            )

    async def _run_rates_analysis(
        self,
        region: str | None,
        data: Dict[str, Any],
    ) -> Any:
        """
        Run the interest-rate analyzer.

        Supports both the future data-aware analyzer contract and
        the current region-only contract.
        """

        try:
            return await self.rates_analyzer.analyze(
                region=region,
                data=data,
            )
        except TypeError:
            # Compatibility with the current analyzer contract.
            return await self.rates_analyzer.analyze(
                region=region,
            )

    # ==================================================================
    # Data normalization
    # ==================================================================

    @staticmethod
    def _normalize_macro_data(
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize macro research data into stable analyzer inputs.
        """

        return {
            "inflation": data.get(
                "inflation",
                {},
            )
            or {},
            "interest_rates": data.get(
                "interest_rates",
                {},
            )
            or {},
            "economic_cycle": data.get(
                "economic_cycle",
                {},
            )
            or {},
            "gdp": data.get(
                "gdp",
                {},
            )
            or {},
            "employment": data.get(
                "employment",
                {},
            )
            or {},
            "commodities": data.get(
                "commodities",
                {},
            )
            or {},
            "currencies": data.get(
                "currencies",
                {},
            )
            or {},
            "market_environment": data.get(
                "market_environment",
                {},
            )
            or {},
            "macro_risks": data.get(
                "macro_risks",
                [],
            )
            or [],
        }

    # ==================================================================
    # Context persistence
    # ==================================================================

    @staticmethod
    def _store_report(
        context: AgentContext,
        report: Dict[str, Any],
    ) -> None:
        """
        Store the macro report in the shared AgentContext.
        """

        if hasattr(context, "set_data"):
            context.set_data(
                "macro_report",
                report,
            )
            return

        # Compatibility fallback for older AgentContext implementations.
        data = getattr(
            context,
            "data",
            None,
        )

        if isinstance(data, dict):
            data["macro_report"] = report
            return

        raise RuntimeError(
            "AgentContext does not provide set_data() or "
            "a writable data mapping."
        )

    # ==================================================================
    # Capabilities
    # ==================================================================

    def capabilities(self) -> List[str]:
        """
        Return capabilities exposed by MacroAgent.
        """

        return [
            "inflation_analysis",
            "interest_rate_analysis",
            "economic_cycle_analysis",
            "macro_risk_detection",
            "market_environment_analysis",
        ]

