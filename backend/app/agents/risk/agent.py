
"""
app/agents/risk/agent.py

Risk Analysis Agent.

Canonical architecture:

    ExecutionEngine
          |
          v
      AgentContext
          |
          v
       RiskAgent
          |
          +── upstream AgentResults / evidence
          |
          +── shared Knowledge / Retrieval
          |
          +── deterministic risk analyzers
          |
          +── scenario engine
          |
          +── deterministic risk scoring
          |
          +── optional LLM synthesis
          |
          v
      AgentResult
"""

from __future__ import annotations

import inspect
import logging
from typing import Any

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import AgentResult
from app.agents.base.base_agent import BaseAgent

from app.agents.risk.models import (
    RiskAnalysisResult,
    RiskFactor,
)


logger = logging.getLogger(__name__)


class RiskAgent(BaseAgent):
    """
    Risk analysis agent.

    Responsibilities:

        - consume canonical AgentContext
        - consume upstream research evidence
        - analyze financial risks
        - analyze operational risks
        - analyze regulatory risks
        - perform scenario analysis
        - calculate deterministic risk score
        - optionally synthesize findings using canonical LLM
        - return AgentResult

    Generic execution, validation, lifecycle management,
    and observability are owned by BaseAgent.
    """

    # =====================================================================
    # Agent metadata
    # =====================================================================

    agent_id = "risk"

    category = "research"

    display_name = "Risk Analysis Agent"

    description = (
        "Analyzes company and investment risks including "
        "financial, operational, regulatory, macro, geopolitical, "
        "scenario, competitive, market, and ESG risks."
    )

    capabilities = [
        "risk",
    ]

    # =====================================================================
    # Deterministic severity mapping
    # =====================================================================

    SEVERITY_SCORES: dict[str, float] = {
        "negligible": 1.0,
        "very_low": 1.0,
        "low": 2.0,
        "medium": 3.0,
        "moderate": 3.0,
        "high": 4.0,
        "very_high": 4.5,
        "critical": 5.0,
    }

    # =====================================================================
    # Initialization
    # =====================================================================

    def __init__(
        self,
        services,
        financial_analyzer=None,
        operational_analyzer=None,
        regulatory_analyzer=None,
        scenario_engine=None,
    ) -> None:

        super().__init__(
            services=services,
        )

        self.financial_analyzer = financial_analyzer
        self.operational_analyzer = operational_analyzer
        self.regulatory_analyzer = regulatory_analyzer
        self.scenario_engine = scenario_engine

        # IMPORTANT:
        #
        # BaseAgent owns the canonical LLM:
        #
        #     self.llm = services.llm
        #
        # Do not create another LLM manager here.

    # =====================================================================
    # Execution
    # =====================================================================

    async def run(
        self,
        context: AgentContext,
    ) -> AgentResult:

        task_id = getattr(
            context,
            "task_id",
            None,
        )

        logger.info(
            "Starting risk analysis | "
            "agent=%s | task_id=%s | research_id=%s",
            self.agent_id,
            task_id,
            context.research_id,
        )

        company = self._resolve_company(
            context=context,
        )

        if not company:
            raise ValueError(
                "Company evidence is missing from AgentContext."
            )

        result = await self.analyze(
            company=company,
            context=context,
        )

        data = self._serialize_analysis_result(
            result
        )

        logger.info(
            "Risk analysis completed | "
            "agent=%s | task_id=%s | research_id=%s | "
            "risk_score=%s | overall_risk=%s",
            self.agent_id,
            task_id,
            context.research_id,
            result.risk_score,
            result.overall_risk,
        )

        return AgentResult.success(
            agent_name=self.agent_id,
            task_id=task_id,
            data=data,
        )

    # =====================================================================
    # Company resolution
    # =====================================================================

    def _resolve_company(
        self,
        context: AgentContext,
    ) -> dict[str, Any]:

        company = getattr(
            context,
            "company",
            None,
        )

        if isinstance(company, dict):
            return dict(company)

        context_data = getattr(
            context,
            "data",
            None,
        ) or {}

        if isinstance(context_data, dict):

            company = context_data.get(
                "company"
            )

            if isinstance(company, dict):
                return dict(company)

        metadata = getattr(
            context,
            "metadata",
            None,
        ) or {}

        if isinstance(metadata, dict):

            company = metadata.get(
                "company"
            )

            if isinstance(company, dict):
                return dict(company)

        name = getattr(
            context,
            "company",
            None,
        )

        ticker = getattr(
            context,
            "ticker",
            None,
        )

        industry = getattr(
            context,
            "industry",
            None,
        )

        if isinstance(name, str):
            return {
                "name": name,
                "ticker": ticker,
                "industry": industry,
            }

        return {}

    # =====================================================================
    # Risk analysis
    # =====================================================================

    async def analyze(
        self,
        company: dict[str, Any],
        context: AgentContext,
    ) -> RiskAnalysisResult:

        logger.info(
            "Running risk analysis for company=%s",
            company.get(
                "name",
                company.get(
                    "company",
                    "unknown",
                ),
            ),
        )

        # --------------------------------------------------------------
        # Evidence
        # --------------------------------------------------------------

        evidence = await self._collect_evidence(
            company=company,
            context=context,
        )

        # --------------------------------------------------------------
        # Risks
        # --------------------------------------------------------------

        risks: list[RiskFactor] = []

        # --------------------------------------------------------------
        # Financial
        # --------------------------------------------------------------

        if self.financial_analyzer is not None:

            financial_risks = await self._run_analyzer(
                analyzer=self.financial_analyzer,
                company=company,
                context=context,
                evidence=evidence,
            )

            risks.extend(
                self._normalize_risks(
                    financial_risks,
                    category="financial",
                )
            )

        # --------------------------------------------------------------
        # Operational
        # --------------------------------------------------------------

        if self.operational_analyzer is not None:

            operational_risks = await self._run_analyzer(
                analyzer=self.operational_analyzer,
                company=company,
                context=context,
                evidence=evidence,
            )

            risks.extend(
                self._normalize_risks(
                    operational_risks,
                    category="operational",
                )
            )

        # --------------------------------------------------------------
        # Regulatory
        # --------------------------------------------------------------

        if self.regulatory_analyzer is not None:

            regulatory_risks = await self._run_analyzer(
                analyzer=self.regulatory_analyzer,
                company=company,
                context=context,
                evidence=evidence,
            )

            risks.extend(
                self._normalize_risks(
                    regulatory_risks,
                    category="regulatory",
                )
            )

        # --------------------------------------------------------------
        # Scenarios
        # --------------------------------------------------------------

        scenarios = await self._run_scenarios(
            company=company,
            context=context,
            evidence=evidence,
        )

        # --------------------------------------------------------------
        # Deterministic scoring
        # --------------------------------------------------------------

        risk_score = self.calculate_risk_score(
            risks
        )

        overall_risk = self.calculate_overall_risk(
            risk_score
        )

        company_name = (
            company.get("name")
            or company.get("company")
        )

        # --------------------------------------------------------------
        # Domain result
        # --------------------------------------------------------------

        result = RiskAnalysisResult(
            company=company_name,
            overall_risk=overall_risk,
            risk_score=risk_score,
            risks=risks,
            summary="",
            recommendations=[],
            metadata={
                "risk_model": "deterministic_severity_average",
                "risk_scale": "1-5",
                "risk_count": len(risks),
                "has_scenarios": scenarios is not None,
            },
        )

        # Keep scenarios inside metadata because the
        # public RiskAnalysisResult contract does not require
        # a dedicated scenarios field.
        result.metadata["scenarios"] = scenarios

        # --------------------------------------------------------------
        # Optional LLM synthesis
        # --------------------------------------------------------------

        result = await self._synthesize_result(
            result=result,
            evidence=evidence,
            context=context,
        )

        return result

    # =====================================================================
    # Evidence collection
    # =====================================================================

    async def _collect_evidence(
        self,
        company: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:

        evidence: dict[str, Any] = {}

        context_data = getattr(
            context,
            "data",
            None,
        ) or {}

        if isinstance(context_data, dict):

            evidence.update(
                self._extract_upstream_evidence(
                    context_data
                )
            )

        agent_results = getattr(
            context,
            "agent_results",
            None,
        )

        if agent_results:

            evidence["agent_results"] = (
                self._serialize_agent_results(
                    agent_results
                )
            )

        knowledge = self._resolve_service(
            context,
            "knowledge",
        )

        if knowledge is None:
            return evidence

        try:

            retrieved = await self._retrieve_risk_evidence(
                knowledge=knowledge,
                company=company,
                context=context,
            )

            if retrieved is not None:
                evidence["retrieved"] = retrieved

        except Exception:

            logger.exception(
                "Risk evidence retrieval failed | company=%s",
                company.get(
                    "name",
                    company.get(
                        "company",
                        "unknown",
                    ),
                ),
            )

        return evidence

    # =====================================================================
    # Upstream evidence
    # =====================================================================

    def _extract_upstream_evidence(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        evidence: dict[str, Any] = {}

        upstream = data.get(
            "agent_results"
        )

        if isinstance(upstream, dict):
            evidence["agent_results"] = upstream

        for key in (
            "company",
            "company_research",
            "financial",
            "financial_analysis",
            "financials",
            "market",
            "market_analysis",
            "macro",
            "macro_analysis",
            "news",
            "news_analysis",
            "industry",
            "industry_analysis",
        ):

            value = data.get(key)

            if value is not None:
                evidence[key] = value

        return evidence

    # =====================================================================
    # Agent result serialization
    # =====================================================================

    def _serialize_agent_results(
        self,
        agent_results: Any,
    ) -> Any:

        if isinstance(agent_results, dict):

            return {
                key: self._serialize_agent_results(value)
                for key, value in agent_results.items()
            }

        if isinstance(agent_results, list):

            return [
                self._serialize_agent_results(item)
                for item in agent_results
            ]

        if isinstance(agent_results, AgentResult):

            return {
                "agent_name": agent_results.agent_name,
                "status": str(agent_results.status),
                "task_id": agent_results.task_id,
                "data": agent_results.data,
                "sources": agent_results.sources,
                "confidence": agent_results.confidence,
                "reasoning": agent_results.reasoning,
                "error": agent_results.error,
                "metadata": agent_results.metadata,
            }

        if hasattr(agent_results, "model_dump"):

            return agent_results.model_dump()

        return agent_results

    # =====================================================================
    # Shared retrieval
    # =====================================================================

    async def _retrieve_risk_evidence(
        self,
        knowledge,
        company: dict[str, Any],
        context: AgentContext,
    ) -> Any:

        query = self._build_risk_query(
            company=company,
            context=context,
        )

        retrieve = getattr(
            knowledge,
            "retrieve",
            None,
        )

        if retrieve is None:
            return None

        try:

            value = retrieve(
                query=query,
                context=context,
            )

            if inspect.isawaitable(value):
                return await value

            return value

        except TypeError:

            value = retrieve(query)

            if inspect.isawaitable(value):
                return await value

            return value

    def _build_risk_query(
        self,
        company: dict[str, Any],
        context: AgentContext,
    ) -> str:

        name = (
            company.get("name")
            or company.get("company")
            or getattr(
                context,
                "company",
                None,
            )
            or "the company"
        )

        ticker = (
            company.get("ticker")
            or getattr(
                context,
                "ticker",
                None,
            )
        )

        identifier = (
            f"{name} ({ticker})"
            if ticker
            else str(name)
        )

        return (
            f"Investment risk analysis for {identifier}. "
            "Identify material financial, operational, regulatory, "
            "macro, geopolitical, market, competitive, and scenario "
            "risks. Prioritize evidence-backed risks and recent "
            "developments."
        )

    # =====================================================================
    # Analyzer execution
    # =====================================================================

    async def _run_analyzer(
        self,
        analyzer,
        company: dict[str, Any],
        context: AgentContext,
        evidence: dict[str, Any],
    ) -> Any:

        analyze = getattr(
            analyzer,
            "analyze",
            None,
        )

        if not callable(analyze):
            raise AttributeError(
                f"Risk analyzer "
                f"{type(analyzer).__name__} "
                "does not expose analyze()."
            )

        # Modern signature
        try:

            value = analyze(
                company=company,
                context=context,
                evidence=evidence,
            )

            if inspect.isawaitable(value):
                return await value

            return value

        except TypeError:
            pass

        # Positional signature
        try:

            value = analyze(
                company,
                context,
                evidence,
            )

            if inspect.isawaitable(value):
                return await value

            return value

        except TypeError:
            pass

        # Legacy signature
        value = analyze(company)

        if inspect.isawaitable(value):
            return await value

        return value

    # =====================================================================
    # Scenario execution
    # =====================================================================

    async def _run_scenarios(
        self,
        company: dict[str, Any],
        context: AgentContext,
        evidence: dict[str, Any],
    ) -> Any:

        if self.scenario_engine is None:
            return None

        run = getattr(
            self.scenario_engine,
            "run",
            None,
        )

        if not callable(run):
            raise AttributeError(
                "ScenarioEngine does not expose run()."
            )

        try:

            value = run(
                company=company,
                context=context,
                evidence=evidence,
            )

            if inspect.isawaitable(value):
                return await value

            return value

        except TypeError:
            pass

        try:

            value = run(
                company,
                context,
                evidence,
            )

            if inspect.isawaitable(value):
                return await value

            return value

        except TypeError:
            pass

        value = run(company)

        if inspect.isawaitable(value):
            return await value

        return value

    # =====================================================================
    # Risk normalization
    # =====================================================================

    def _normalize_risks(
        self,
        risks: Any,
        category: str,
    ) -> list[RiskFactor]:

        if risks is None:
            return []

        if isinstance(risks, RiskFactor):
            risks = [risks]

        elif isinstance(risks, dict):
            risks = [risks]

        if not isinstance(
            risks,
            (list, tuple),
        ):
            return []

        normalized: list[RiskFactor] = []

        for risk in risks:

            # Already canonical
            if isinstance(risk, RiskFactor):

                if not risk.category:
                    risk.category = category

                self._populate_severity_score(risk)

                normalized.append(risk)
                continue

            # Pydantic object
            if hasattr(risk, "model_dump"):

                try:
                    risk = risk.model_dump()
                except Exception:
                    continue

            # Dictionary
            if not isinstance(risk, dict):
                continue

            payload = dict(risk)

            payload.setdefault(
                "category",
                category,
            )

            name = payload.get("name")

            description = payload.get(
                "description"
            )

            if not name:
                name = (
                    payload.get("risk")
                    or payload.get("title")
                    or "Unnamed risk"
                )

            if not description:
                description = (
                    payload.get("details")
                    or payload.get("reason")
                    or payload.get("explanation")
                    or ""
                )

            payload["name"] = str(name)

            payload["description"] = str(
                description
            )

            severity = payload.get(
                "severity",
                "medium",
            )

            if severity is None:
                severity = "medium"

            payload["severity"] = (
                str(severity)
                .strip()
                .lower()
                .replace("-", "_")
                .replace(" ", "_")
            )

            try:

                risk_factor = RiskFactor(
                    **payload
                )

            except Exception:

                logger.warning(
                    "Unable to normalize risk result | "
                    "category=%s | value=%r",
                    category,
                    risk,
                )

                continue

            self._populate_severity_score(
                risk_factor
            )

            normalized.append(
                risk_factor
            )

        return normalized

    # =====================================================================
    # Severity normalization
    # =====================================================================

    def _populate_severity_score(
        self,
        risk: RiskFactor,
    ) -> None:

        if risk.severity_score is not None:
            return

        severity = (
            str(risk.severity)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        numeric_score = (
            self.SEVERITY_SCORES.get(
                severity
            )
        )

        if numeric_score is not None:
            risk.severity_score = numeric_score

    # =====================================================================
    # Deterministic risk scoring
    # =====================================================================

    def calculate_risk_score(
        self,
        risks: list[RiskFactor | dict[str, Any]],
    ) -> float:
        """
        Calculate deterministic average risk severity.

        Scale:

            1.0 = negligible
            2.0 = low
            3.0 = medium
            4.0 = high
            5.0 = critical

        The score is independent of the LLM.
        """

        if not risks:
            return 0.0

        total = 0.0
        valid = 0

        for risk in risks:

            score: float | None = None

            if isinstance(
                risk,
                RiskFactor,
            ):

                if risk.severity_score is not None:

                    score = float(
                        risk.severity_score
                    )

                else:

                    score = self._severity_to_score(
                        risk.severity
                    )

            elif isinstance(
                risk,
                dict,
            ):

                raw_score = risk.get(
                    "severity_score"
                )

                if raw_score is not None:

                    try:
                        score = float(
                            raw_score
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):
                        score = None

                if score is None:

                    score = self._severity_to_score(
                        risk.get("severity")
                    )

            if score is None:
                continue

            score = max(
                1.0,
                min(
                    5.0,
                    score,
                ),
            )

            total += score
            valid += 1

        if valid == 0:
            return 0.0

        return round(
            total / valid,
            2,
        )

    # =====================================================================
    # Severity to score
    # =====================================================================

    def _severity_to_score(
        self,
        severity: Any,
    ) -> float | None:

        if severity is None:
            return None

        if isinstance(
            severity,
            (int, float),
        ):

            try:
                return float(severity)

            except (
                TypeError,
                ValueError,
            ):
                return None

        normalized = (
            str(severity)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

        if normalized in self.SEVERITY_SCORES:

            return self.SEVERITY_SCORES[
                normalized
            ]

        try:
            return float(normalized)

        except (
            TypeError,
            ValueError,
        ):
            return None

    # =====================================================================
    # Overall risk classification
    # =====================================================================

    def calculate_overall_risk(
        self,
        risk_score: float,
    ) -> str:
        """
        Convert deterministic 1-5 risk score into a stable label.

        Thresholds:

            < 2.0  -> low
            < 3.0  -> medium
            < 4.0  -> high
            >= 4.0 -> critical
        """

        if risk_score <= 0:
            return "medium"

        if risk_score < 2.0:
            return "low"

        if risk_score < 3.0:
            return "medium"

        if risk_score < 4.0:
            return "high"

        return "critical"

    # =====================================================================
    # LLM synthesis
    # =====================================================================

    async def _synthesize_result(
        self,
        result: RiskAnalysisResult,
        evidence: dict[str, Any],
        context: AgentContext,
    ) -> RiskAnalysisResult:

        llm = self._resolve_llm(
            context
        )

        if llm is None:
            logger.debug(
                "No LLM available for risk synthesis | company=%s",
                result.company,
            )
            return result

        synthesis_fields = (
            "summary",
            "recommendations",
        )

        supported_fields = {
            field
            for field in synthesis_fields
            if hasattr(result, field)
        }

        if not supported_fields:
            return result

        try:

            synthesis = await self._generate_synthesis(
                llm=llm,
                result=result,
                evidence=evidence,
                context=context,
            )

            if not synthesis:
                return result

            if isinstance(
                synthesis,
                dict,
            ):

                update = {
                    key: value
                    for key, value in synthesis.items()
                    if key in supported_fields
                }

                if update:

                    if hasattr(
                        result,
                        "model_copy",
                    ):

                        return result.model_copy(
                            update=update
                        )

                    # Pydantic v1 compatibility
                    if hasattr(
                        result,
                        "copy",
                    ):

                        return result.copy(
                            update=update
                        )

        except Exception:

            # LLM synthesis is OPTIONAL.
            #
            # The deterministic risk analysis remains valid even
            # when the LLM provider is unavailable or malformed.
            logger.exception(
                "Risk synthesis failed | company=%s",
                result.company,
            )

        return result

    # =====================================================================
    # LLM generation
    # =====================================================================

    async def _generate_synthesis(
        self,
        llm,
        result: RiskAnalysisResult,
        evidence: dict[str, Any],
        context: AgentContext,
    ) -> Any:
        """
        Generate risk synthesis using the canonical LLMManager.chat()
        contract.

        The canonical runtime contract is:

            llm.chat(
                messages=messages,
                task="chat",
            )

        Do not pass AgentContext through this call.

        AgentContext is an internal Orion runtime object and must not
        leak into the OpenAI/OpenRouter SDK request.
        """

        prompt = self._build_synthesis_prompt(
            result=result,
            evidence=evidence,
        )

        if not prompt or not prompt.strip():
            logger.warning(
                "Skipping risk synthesis because prompt is empty | company=%s",
                result.company,
            )
            return None

        messages = [
            {
                "role": "system",
                "content": (
                    "You are the risk synthesis component of the "
                    "Orion AI research system. "
                    "Use only the supplied evidence. "
                    "Do not invent facts. "
                    "Do not alter deterministic risk scores."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        # --------------------------------------------------------------
        # Canonical path:
        #
        # Agent -> LLMManager.chat(messages=..., task=...)
        #
        # IMPORTANT:
        #
        # Do NOT pass:
        #
        #     context=context
        #
        # because LLMManager.chat() forwards **kwargs to the provider,
        # which ultimately forwards them to the OpenAI/OpenRouter SDK.
        # AgentContext is not a valid Completions.create() parameter.
        # --------------------------------------------------------------

        chat = getattr(
            llm,
            "chat",
            None,
        )

        if callable(chat):

            value = chat(
                messages=messages,
                task="chat",
            )

            if inspect.isawaitable(value):
                return await value

            return value

        # --------------------------------------------------------------
        # Compatibility fallback.
        #
        # Only use generate if the object does not expose chat().
        #
        # The current Orion architecture should normally never reach
        # this branch because LLMManager exposes chat().
        # --------------------------------------------------------------

        generate = getattr(
            llm,
            "generate",
            None,
        )

        if callable(generate):

            try:

                value = generate(
                    prompt=prompt,
                )

                if inspect.isawaitable(value):
                    return await value

                return value

            except TypeError:

                value = generate(
                    prompt,
                )

                if inspect.isawaitable(value):
                    return await value

                return value

        logger.warning(
            "LLM object does not expose chat() or generate() | "
            "type=%s",
            type(llm).__name__,
        )

        return None

    # =====================================================================
    # LLM prompt
    # =====================================================================

    def _build_synthesis_prompt(
        self,
        result: RiskAnalysisResult,
        evidence: dict[str, Any],
    ) -> str:

        scenarios = result.metadata.get(
            "scenarios"
        )

        return (
            "Synthesize the following investment risk analysis.\n\n"

            "Rules:\n"
            "1. Use only supplied evidence.\n"
            "2. Do not invent facts.\n"
            "3. Do not change the deterministic risk score.\n"
            "4. Clearly distinguish observed risks from scenarios.\n"
            "5. Produce concise evidence-grounded conclusions.\n"
            "6. Do not introduce unsupported financial figures.\n"
            "7. Do not introduce unsupported recommendations.\n\n"

            f"Company: {result.company}\n"
            f"Overall risk: {result.overall_risk}\n"
            f"Risk score: {result.risk_score}\n"
            f"Risks: {result.risks}\n"
            f"Scenarios: {scenarios}\n"
            f"Evidence: {evidence}\n\n"

            "Return structured output containing:\n"
            "- summary\n"
            "- recommendations\n\n"

            "The summary should explain the most material risks. "
            "Recommendations should be concise and directly connected "
            "to the identified evidence-backed risks."
        )

    # =====================================================================
    # Service resolution
    # =====================================================================

    def _resolve_service(
        self,
        context: AgentContext,
        service_name: str,
    ) -> Any:

        services = getattr(
            context,
            "services",
            None,
        )

        if services is None:
            services = self.services

        if services is None:
            return None

        return getattr(
            services,
            service_name,
            None,
        )

    # =====================================================================
    # LLM resolution
    # =====================================================================

    def _resolve_llm(
        self,
        context: AgentContext,
    ) -> Any:

        runtime_llm = self._resolve_service(
            context,
            "llm",
        )

        if runtime_llm is not None:
            return runtime_llm

        return self.llm

    # =====================================================================
    # Final result normalization
    # =====================================================================

    def _serialize_analysis_result(
        self,
        result: RiskAnalysisResult,
    ) -> dict[str, Any]:

        if hasattr(
            result,
            "model_dump",
        ):

            return result.model_dump(
                mode="json"
            )

        if isinstance(
            result,
            dict,
        ):
            return result

        return {
            "result": result,
        }
