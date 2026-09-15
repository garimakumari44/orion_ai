
"""
app/agents/valuation/agent.py

Valuation Analysis Agent.

Performs intrinsic and relative valuation using financial,
market, company, and comparable-company evidence available
through AgentContext and AgentServices.

Canonical architecture:

    ExecutionEngine
          |
          v
    AgentContext
          |
          v
    BaseAgent.execute()
          |
          v
    ValuationAgent.run(context)
          |
          +--> upstream AgentResults / research evidence
          |
          +--> deterministic valuation models
          |       +--> DCFModel
          |       +--> ComparableAnalysis
          |       +--> MultiplesAnalysis
          |       +--> SensitivityAnalysis
          |
          +--> optional LLM synthesis
          |
          v
      AgentResult
"""

from __future__ import annotations

import inspect
import logging
from typing import Any, Dict, List, Optional

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.agent_services import AgentServices
from app.agents.base.base_agent import BaseAgent

from .comparables import ComparableAnalysis
from .dcf import DCFModel
from .models import (
    ComparableCompany,
    ValuationInput,
    ValuationReport,
)
from .multiples import MultiplesAnalysis
from .sensitivity import SensitivityAnalysis


logger = logging.getLogger(__name__)


class ValuationAgent(BaseAgent):
    """
    Valuation research agent.

    Responsibilities
    ----------------
    - Perform intrinsic valuation.
    - Perform relative valuation.
    - Analyze trading multiples.
    - Generate valuation scenarios.
    - Produce deterministic valuation conclusions.
    - Optionally synthesize valuation evidence with an LLM.

    Runtime boundary
    ----------------
    AgentContext -> AgentResult

    Shared capabilities are accessed through the canonical
    AgentServices container inherited from BaseAgent.

    Domain-specific valuation logic remains in deterministic
    valuation models.
    """

    # =========================================================
    # Agent Metadata
    # =========================================================

    agent_id = "valuation"

    category = "research"

    display_name = "Valuation Analysis Agent"

    description = (
        "Performs intrinsic and relative valuation using "
        "financial, market, company, and comparable-company "
        "evidence."
    )

    capabilities = [
        "valuation",
        "dcf",
        "comparables",
        "multiples",
        "sensitivity_analysis",
    ]

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        services: AgentServices,
    ) -> None:
        """
        Initialize the valuation agent.

        Shared infrastructure is injected through AgentServices.

        Valuation-specific deterministic models are created
        inside the analysis boundary because they are lightweight
        domain objects rather than application-wide services.
        """

        super().__init__(
            services=services,
        )

    # =========================================================
    # Execution
    # =========================================================

    async def run(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Execute valuation analysis.

        Canonical BaseAgent contract:

            run(context)

        BaseAgent owns:

            - context validation
            - service validation
            - task validation
            - lifecycle management
            - generic exception handling
            - result normalization
            - result registration
            - cleanup

        Therefore this method does not implement a broad
        try/except execution boundary.
        """

        logger.info(
            "Starting valuation analysis | "
            "agent=%s | research_id=%s | company=%s",
            self.agent_id,
            getattr(
                context,
                "research_id",
                None,
            ),
            self._company_name(context),
        )

        # -----------------------------------------------------
        # Build normalized valuation input
        # -----------------------------------------------------

        valuation_input = await self._build_valuation_input(
            context,
        )

        # -----------------------------------------------------
        # Resolve comparable companies
        # -----------------------------------------------------

        peers = await self._get_peers(
            context,
        )

        # -----------------------------------------------------
        # Deterministic valuation
        # -----------------------------------------------------

        report = self.analyze(
            valuation_input=valuation_input,
            peers=peers,
        )

        # -----------------------------------------------------
        # Optional LLM synthesis
        #
        # Deterministic valuation remains authoritative.
        # -----------------------------------------------------

        report = await self._synthesize(
            context=context,
            report=report,
        )

        # -----------------------------------------------------
        # Canonical AgentResult
        # -----------------------------------------------------

        return AgentResult.success(
            agent_name=self.agent_id,
            task_id=getattr(
                context,
                "task_id",
                None,
            ),
            data=self._report_to_data(
                report,
            ),
            metadata={
                "company": valuation_input.company_name,
                "valuation_methods": self._valuation_methods(
                    report,
                ),
            },
        )

    # =========================================================
    # Input Construction
    # =========================================================

    async def _build_valuation_input(
        self,
        context: AgentContext,
    ) -> ValuationInput:
        """
        Build ValuationInput from upstream research context.

        Valuation consumes normalized upstream outputs rather
        than reaching directly into arbitrary application state.
        """

        company = self._get_company_data(
            context,
        )

        financial = self._get_financial_data(
            context,
        )

        market = self._get_market_data(
            context,
        )

        company_name = (
            company.get("name")
            or company.get("company_name")
            or company.get("company")
            or getattr(
                context,
                "company",
                None,
            )
            or getattr(
                context,
                "company_name",
                None,
            )
            or "Unknown Company"
        )

        return ValuationInput(
            company_name=str(
                company_name,
            ),
            free_cash_flow=self._first_value(
                financial,
                "free_cash_flow",
                "free_cash_flow_ttm",
                "fcf",
                "fcf_ttm",
            ),
            shares_outstanding=self._first_value(
                financial,
                "shares_outstanding",
                "shares",
                "shares_out",
            ),
            growth_rate=self._first_value(
                financial,
                "growth_rate",
                "revenue_growth",
                "fcf_growth",
                "earnings_growth",
            ),
            discount_rate=self._first_value(
                financial,
                "discount_rate",
                "wacc",
            ),
            current_price=self._first_value(
                market,
                "price",
                "current_price",
                "share_price",
            ),
        )

    # =========================================================
    # Comparable Companies
    # =========================================================

    async def _get_peers(
        self,
        context: AgentContext,
    ) -> List[ComparableCompany]:
        """
        Resolve comparable companies from upstream research.

        Preferred sources:

        1. valuation AgentResult
        2. valuation context data
        3. company AgentResult
        4. company context data

        No independent retrieval infrastructure is constructed.
        """

        valuation_data = self._get_context_data(
            context,
            "valuation",
        )

        peers = valuation_data.get(
            "peers",
        )

        if peers:
            return self._normalize_peers(
                peers,
            )

        company_data = self._get_company_data(
            context,
        )

        peers = company_data.get(
            "peers",
        )

        if peers:
            return self._normalize_peers(
                peers,
            )

        return []

    # =========================================================
    # Deterministic Valuation
    # =========================================================

    def analyze(
        self,
        valuation_input: ValuationInput,
        peers: Optional[
            List[ComparableCompany]
        ] = None,
    ) -> ValuationReport:
        """
        Run deterministic valuation models.

        This method contains no orchestration concerns and
        does not call the LLM.
        """

        logger.info(
            "Running valuation models | company=%s",
            valuation_input.company_name,
        )

        report = ValuationReport(
            company=valuation_input.company_name,
        )

        # =====================================================
        # 1. DCF
        # =====================================================

        if (
            valuation_input.free_cash_flow is not None
            and valuation_input.shares_outstanding is not None
        ):
            dcf_model = DCFModel(
                growth_rate=(
                    valuation_input.growth_rate
                    if valuation_input.growth_rate is not None
                    else 0.05
                ),
                discount_rate=(
                    valuation_input.discount_rate
                    if valuation_input.discount_rate is not None
                    else 0.10
                ),
            )

            report.dcf = dcf_model.calculate(
                free_cash_flow=(
                    valuation_input.free_cash_flow
                ),
                shares_outstanding=(
                    valuation_input.shares_outstanding
                ),
            )

        # =====================================================
        # 2. Comparable Companies
        # =====================================================

        if peers:
            comparable_model = ComparableAnalysis(
                peers,
            )

            report.comparable_analysis = (
                comparable_model.valuation_summary()
            )

        # =====================================================
        # 3. Trading Multiples
        # =====================================================

        multiples_model = MultiplesAnalysis()

        report.multiples_analysis = {
            "status": "Multiple valuation ready",
            "supported_methods": [
                "PE",
                "EV/EBITDA",
                "EV/Revenue",
            ],
        }

        # Keep the model instantiated so the domain dependency
        # remains explicit even when the current implementation
        # only exposes supported methods.
        _ = multiples_model

        # =====================================================
        # 4. Sensitivity Analysis
        # =====================================================

        if report.dcf:
            base_value = (
                report.dcf.fair_value_per_share
            )

            sensitivity = SensitivityAnalysis(
                valuation_function=(
                    lambda growth, discount:
                    base_value
                    * (
                        1
                        + growth
                        - discount
                    )
                )
            )

            report.sensitivity_analysis = (
                sensitivity.generate_scenario(
                    base_value,
                )
            )

        # =====================================================
        # 5. Deterministic Conclusion
        # =====================================================

        report.conclusion = (
            self.generate_conclusion(
                report,
            )
        )

        return report

    # =========================================================
    # Deterministic Conclusion
    # =========================================================

    def generate_conclusion(
        self,
        report: ValuationReport,
    ) -> str:
        """
        Generate deterministic valuation conclusion.

        LLM synthesis is performed separately and may replace
        the textual conclusion, but cannot modify deterministic
        valuation calculations.
        """

        if report.dcf:
            value = (
                report.dcf.fair_value_per_share
            )

            return (
                f"DCF estimated fair value is "
                f"{value:.2f} per share. "
                "Review valuation assumptions, "
                "sensitivity results, and investment risks "
                "before making an investment decision."
            )

        if report.comparable_analysis:
            return (
                "Comparable-company valuation is available. "
                "Review peer selection, peer assumptions, "
                "and relative valuation metrics before "
                "making an investment decision."
            )

        if report.multiples_analysis:
            return (
                "Trading-multiple analysis is available, "
                "but insufficient information is available "
                "to establish a complete intrinsic valuation."
            )

        return (
            "Insufficient valuation data available."
        )

    # =========================================================
    # LLM Synthesis
    # =========================================================

    async def _synthesize(
        self,
        context: AgentContext,
        report: ValuationReport,
    ) -> ValuationReport:
        """
        Optionally synthesize valuation evidence with the
        canonical shared LLM capability.

        IMPORTANT:

        LLMService.generate() is treated as a capability that
        may be synchronous or asynchronous.

        The agent therefore:

            1. Calls generate(prompt)
            2. Does NOT pass unsupported context=...
            3. Checks inspect.isawaitable()
            4. Awaits only when necessary

        Deterministic valuation calculations remain authoritative.
        """

        llm = self._resolve_llm(
            context,
        )

        if llm is None:
            logger.debug(
                "No LLM configured for valuation synthesis."
            )
            return report

        prompt = self._build_synthesis_prompt(
            context=context,
            report=report,
        )

        generate = getattr(
            llm,
            "generate",
            None,
        )

        if not callable(generate):
            logger.warning(
                "Valuation LLM does not expose generate(); "
                "keeping deterministic conclusion."
            )
            return report

        try:
            # -------------------------------------------------
            # IMPORTANT:
            #
            # LLMService.generate() does not accept context=...
            # Call it with the canonical prompt argument only.
            # -------------------------------------------------

            response = generate(
                prompt,
            )

            # -------------------------------------------------
            # Support both:
            #
            # async def generate(...)
            # def generate(...)
            # -------------------------------------------------

            if inspect.isawaitable(response):
                response = await response

            # -------------------------------------------------
            # Text response
            # -------------------------------------------------

            if isinstance(
                response,
                str,
            ):
                synthesis = response.strip()

                if synthesis:
                    report.conclusion = synthesis

                return report

            # -------------------------------------------------
            # Dictionary response
            # -------------------------------------------------

            if isinstance(
                response,
                dict,
            ):
                synthesis = (
                    response.get(
                        "conclusion",
                    )
                    or response.get(
                        "summary",
                    )
                    or response.get(
                        "overall_assessment",
                    )
                )

                if isinstance(
                    synthesis,
                    str,
                ):
                    synthesis = synthesis.strip()

                    if synthesis:
                        report.conclusion = synthesis

                return report

            logger.warning(
                "Valuation LLM returned unsupported response "
                "type=%s; keeping deterministic conclusion.",
                type(response).__name__,
            )

        except Exception:
            logger.exception(
                "Valuation LLM synthesis failed; "
                "keeping deterministic conclusion."
            )

        return report

    # =========================================================
    # LLM Resolution
    # =========================================================

    def _resolve_llm(
        self,
        context: AgentContext,
    ) -> Any:
        """
        Resolve the canonical shared LLM capability.

        AgentContext.services is canonical and should contain
        the same AgentServices instance validated by BaseAgent.

        AgentServices.llm is the preferred capability.
        """

        services = getattr(
            context,
            "services",
            None,
        )

        if services is not None:
            llm = getattr(
                services,
                "llm",
                None,
            )

            if llm is not None:
                return llm

        return getattr(
            self.services,
            "llm",
            None,
        )

    # =========================================================
    # LLM Prompt
    # =========================================================

    def _build_synthesis_prompt(
        self,
        context: AgentContext,
        report: ValuationReport,
    ) -> str:
        """
        Build the valuation synthesis prompt.

        The LLM receives only the deterministic valuation result.
        """

        return f"""
You are synthesizing an equity valuation analysis.

Company:
{report.company}

DCF:
{report.dcf}

Comparable analysis:
{report.comparable_analysis}

Multiples analysis:
{report.multiples_analysis}

Sensitivity analysis:
{report.sensitivity_analysis}

Deterministic conclusion:
{report.conclusion}

Produce a concise investment-research valuation conclusion.

Requirements:

- distinguish intrinsic valuation from relative valuation
- identify important valuation assumptions
- mention valuation uncertainty
- discuss sensitivity where available
- do not invent missing financial data
- do not create unsupported price targets
- do not modify deterministic valuation calculations
- clearly state when evidence is insufficient
- distinguish calculated results from qualitative interpretation
""".strip()

    # =========================================================
    # Context Helpers
    # =========================================================

    @staticmethod
    def _get_financial_data(
        context: AgentContext,
    ) -> Dict[str, Any]:
        """
        Retrieve financial evidence.

        Prefer the canonical FinancialAgent result and fall back
        to context-level financial data.
        """

        return ValuationAgent._get_result_data(
            context=context,
            agent_names=[
                "financial",
                "financial_agent",
            ],
            fallback_keys=[
                "financial",
                "financial_analysis",
                "financials",
            ],
        )

    @staticmethod
    def _get_company_data(
        context: AgentContext,
    ) -> Dict[str, Any]:
        """
        Retrieve company evidence.

        Prefer the canonical CompanyAgent result and fall back
        to context-level company data.
        """

        return ValuationAgent._get_result_data(
            context=context,
            agent_names=[
                "company",
                "company_agent",
            ],
            fallback_keys=[
                "company",
                "company_research",
            ],
        )

    @staticmethod
    def _get_market_data(
        context: AgentContext,
    ) -> Dict[str, Any]:
        """
        Retrieve market evidence.

        Prefer the canonical MarketAgent result and fall back
        to context-level market data.
        """

        return ValuationAgent._get_result_data(
            context=context,
            agent_names=[
                "market",
                "market_agent",
            ],
            fallback_keys=[
                "market",
                "market_analysis",
            ],
        )

    # =========================================================
    # Generic Result Resolution
    # =========================================================

    @staticmethod
    def _get_result_data(
        context: AgentContext,
        agent_names: List[str],
        fallback_keys: Optional[
            List[str]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Resolve upstream agent output.

        Preferred order:

            AgentContext.agent_results
                    |
                    v
            AgentContext helper methods
                    |
                    v
            context.data
                    |
                    v
            context.metadata

        The method is intentionally defensive because
        AgentContext implementations may evolve while preserving
        the canonical execution contract.
        """

        # -----------------------------------------------------
        # 1. Canonical AgentResult collection
        # -----------------------------------------------------

        agent_results = getattr(
            context,
            "agent_results",
            None,
        )

        if isinstance(
            agent_results,
            dict,
        ):
            for agent_name in agent_names:
                raw_result = agent_results.get(
                    agent_name,
                )

                data = (
                    ValuationAgent._extract_result_data(
                        raw_result,
                    )
                )

                if data:
                    return data

        # -----------------------------------------------------
        # 2. Context helper if available
        # -----------------------------------------------------

        get_result_data = getattr(
            context,
            "get_result_data",
            None,
        )

        if callable(
            get_result_data,
        ):
            for agent_name in agent_names:
                try:
                    result_data = get_result_data(
                        agent_name,
                    )

                    data = (
                        ValuationAgent._coerce_dict(
                            result_data,
                        )
                    )

                    if data:
                        return data

                except (
                    AttributeError,
                    KeyError,
                    TypeError,
                ):
                    continue

        # -----------------------------------------------------
        # 3. Context data
        # -----------------------------------------------------

        context_data = getattr(
            context,
            "data",
            None,
        )

        if isinstance(
            context_data,
            dict,
        ):
            for key in (
                fallback_keys or []
            ):
                value = context_data.get(
                    key,
                )

                data = (
                    ValuationAgent._coerce_dict(
                        value,
                    )
                )

                if data:
                    return data

        # -----------------------------------------------------
        # 4. Context metadata
        # -----------------------------------------------------

        metadata = getattr(
            context,
            "metadata",
            None,
        )

        if isinstance(
            metadata,
            dict,
        ):
            for key in (
                fallback_keys or []
            ):
                value = metadata.get(
                    key,
                )

                data = (
                    ValuationAgent._coerce_dict(
                        value,
                    )
                )

                if data:
                    return data

        return {}

    # =========================================================
    # Result Extraction
    # =========================================================

    @staticmethod
    def _extract_result_data(
        result: Any,
    ) -> Dict[str, Any]:
        """
        Extract the data dictionary from an AgentResult or
        compatible upstream result.
        """

        if result is None:
            return {}

        # AgentResult.data
        data = getattr(
            result,
            "data",
            None,
        )

        if isinstance(
            data,
            dict,
        ):
            return data

        # Raw dictionary
        if isinstance(
            result,
            dict,
        ):
            nested_data = result.get(
                "data",
            )

            if isinstance(
                nested_data,
                dict,
            ):
                return nested_data

            return result

        # Pydantic/domain object
        model_dump = getattr(
            result,
            "model_dump",
            None,
        )

        if callable(
            model_dump,
        ):
            try:
                dumped = model_dump()

                if isinstance(
                    dumped,
                    dict,
                ):
                    return dumped

            except Exception:
                pass

        return {}

    # =========================================================
    # Context Data Helper
    # =========================================================

    @staticmethod
    def _get_context_data(
        context: AgentContext,
        key: str,
    ) -> Dict[str, Any]:
        """
        Retrieve a named data section from AgentContext.
        """

        # -----------------------------------------------------
        # Preferred context helper
        # -----------------------------------------------------

        get_data = getattr(
            context,
            "get_data",
            None,
        )

        if callable(
            get_data,
        ):
            try:
                data = get_data(
                    key,
                )

                if isinstance(
                    data,
                    dict,
                ):
                    return data

            except (
                AttributeError,
                KeyError,
                TypeError,
            ):
                pass

        # -----------------------------------------------------
        # context.data
        # -----------------------------------------------------

        context_data = getattr(
            context,
            "data",
            None,
        )

        if isinstance(
            context_data,
            dict,
        ):
            data = context_data.get(
                key,
            )

            if isinstance(
                data,
                dict,
            ):
                return data

        # -----------------------------------------------------
        # context.metadata
        # -----------------------------------------------------

        metadata = getattr(
            context,
            "metadata",
            None,
        )

        if isinstance(
            metadata,
            dict,
        ):
            data = metadata.get(
                key,
            )

            if isinstance(
                data,
                dict,
            ):
                return data

        return {}

    # =========================================================
    # Value Resolution
    # =========================================================

    @staticmethod
    def _first_value(
        data: Dict[str, Any],
        *keys: str,
    ) -> Any:
        """
        Return the first non-None value for the supplied keys.
        """

        if not isinstance(
            data,
            dict,
        ):
            return None

        for key in keys:
            value = data.get(
                key,
            )

            if value is not None:
                return value

        return None

    # =========================================================
    # Company Identity
    # =========================================================

    @staticmethod
    def _company_name(
        context: AgentContext,
    ) -> str:
        """
        Resolve company name from canonical context identity.
        """

        company = getattr(
            context,
            "company",
            None,
        )

        if isinstance(
            company,
            str,
        ) and company.strip():
            return company.strip()

        if isinstance(
            company,
            dict,
        ):
            name = (
                company.get("name")
                or company.get("company_name")
                or company.get("company")
            )

            if name:
                return str(
                    name,
                )

        company_name = getattr(
            context,
            "company_name",
            None,
        )

        if company_name:
            return str(
                company_name,
            )

        return "Unknown Company"

    # =========================================================
    # Peer Normalization
    # =========================================================

    @staticmethod
    def _normalize_peers(
        peers: Any,
    ) -> List[ComparableCompany]:
        """
        Normalize peer data into ComparableCompany objects.
        """

        if isinstance(
            peers,
            dict,
        ):
            peers = [
                peers,
            ]

        if not isinstance(
            peers,
            list,
        ):
            return []

        normalized: List[
            ComparableCompany
        ] = []

        for peer in peers:
            if isinstance(
                peer,
                ComparableCompany,
            ):
                normalized.append(
                    peer,
                )
                continue

            if isinstance(
                peer,
                dict,
            ):
                try:
                    normalized.append(
                        ComparableCompany(
                            **peer,
                        )
                    )
                except Exception:
                    logger.warning(
                        "Unable to normalize comparable "
                        "company: %s",
                        peer,
                    )

        return normalized

    # =========================================================
    # Valuation Methods
    # =========================================================

    @staticmethod
    def _valuation_methods(
        report: ValuationReport,
    ) -> List[str]:
        """
        Return the valuation methods actually represented
        in the report.
        """

        methods: List[str] = []

        if getattr(
            report,
            "dcf",
            None,
        ):
            methods.append(
                "DCF",
            )

        if getattr(
            report,
            "comparable_analysis",
            None,
        ):
            methods.append(
                "Comparable Companies",
            )

        if getattr(
            report,
            "multiples_analysis",
            None,
        ):
            methods.append(
                "Trading Multiples",
            )

        if getattr(
            report,
            "sensitivity_analysis",
            None,
        ):
            methods.append(
                "Sensitivity Analysis",
            )

        return methods

    # =========================================================
    # Report Serialization
    # =========================================================

    @staticmethod
    def _report_to_data(
        report: ValuationReport,
    ) -> Dict[str, Any]:
        """
        Convert ValuationReport into the serializable
        AgentResult.data payload.

        Pydantic models are preferred when available.
        """

        model_dump = getattr(
            report,
            "model_dump",
            None,
        )

        if callable(
            model_dump,
        ):
            try:
                data = model_dump()

                if isinstance(
                    data,
                    dict,
                ):
                    return data

            except Exception:
                logger.exception(
                    "Failed to serialize ValuationReport "
                    "using model_dump()."
                )

        dict_method = getattr(
            report,
            "dict",
            None,
        )

        if callable(
            dict_method,
        ):
            try:
                data = dict_method()

                if isinstance(
                    data,
                    dict,
                ):
                    return data

            except Exception:
                logger.exception(
                    "Failed to serialize ValuationReport "
                    "using dict()."
                )

        return {
            "company": getattr(
                report,
                "company",
                None,
            ),
            "dcf": getattr(
                report,
                "dcf",
                None,
            ),
            "comparable_analysis": getattr(
                report,
                "comparable_analysis",
                None,
            ),
            "multiples_analysis": getattr(
                report,
                "multiples_analysis",
                None,
            ),
            "sensitivity_analysis": getattr(
                report,
                "sensitivity_analysis",
                None,
            ),
            "conclusion": getattr(
                report,
                "conclusion",
                None,
            ),
        }

    # =========================================================
    # Dictionary Coercion
    # =========================================================

    @staticmethod
    def _coerce_dict(
        value: Any,
    ) -> Dict[str, Any]:
        """
        Convert supported result/data objects into dictionaries.
        """

        if value is None:
            return {}

        if isinstance(
            value,
            dict,
        ):
            return value

        # AgentResult-like object
        data = getattr(
            value,
            "data",
            None,
        )

        if isinstance(
            data,
            dict,
        ):
            return data

        # Pydantic v2
        model_dump = getattr(
            value,
            "model_dump",
            None,
        )

        if callable(
            model_dump,
        ):
            try:
                dumped = model_dump()

                if isinstance(
                    dumped,
                    dict,
                ):
                    return dumped

            except Exception:
                pass

        # Pydantic v1 / legacy objects
        dict_method = getattr(
            value,
            "dict",
            None,
        )

        if callable(
            dict_method,
        ):
            try:
                dumped = dict_method()

                if isinstance(
                    dumped,
                    dict,
                ):
                    return dumped

            except Exception:
                pass

        return {}

