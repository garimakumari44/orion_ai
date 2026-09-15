"""
app/agents/investment_committee/agent.py

Investment Committee Agent
==========================

Synthesizes research produced by the other agents and produces
an investment-level decision.

The agent implements only the domain-specific ``run(context)``
method required by BaseAgent.

Generic execution lifecycle, validation, error handling,
observability, result normalization, and cleanup are owned by
BaseAgent.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from app.agents.base.agent_context import AgentContext
from app.agents.base.agent_result import (
    AgentResult,
    AgentStatus,
)
from app.agents.base.base_agent import BaseAgent


logger = logging.getLogger(__name__)


class InvestmentCommitteeAgent(BaseAgent):
    """
    Investment Committee Agent.

    Responsibilities
    ----------------
    - Consume results produced by upstream research agents.
    - Synthesize agreement and disagreement across agents.
    - Evaluate the overall investment thesis.
    - Weigh valuation, financials, industry, macro, news,
      catalysts, and risks.
    - Consider critic/quality-control results.
    - Produce the final investment-level decision.

    BaseAgent owns the generic execution lifecycle.

    This class therefore implements only:

        async def run(context) -> AgentResult
    """

    # =========================================================
    # Metadata
    # =========================================================

    agent_id = "investment_committee"

    category = "research"

    display_name = "Investment Committee"

    description = (
        "Synthesizes specialized equity research into "
        "an investment-level decision."
    )

    capabilities = [
        "research_synthesis",
        "investment_decision",
        "thesis_evaluation",
        "risk_evaluation",
        "valuation_synthesis",
        "cross_agent_analysis",
    ]

    # Backward compatibility
    name = "investment_committee"
    role = "Investment Decision Committee"

    # =========================================================
    # Specialized Execution
    # =========================================================

    async def run(
        self,
        context: AgentContext,
    ) -> AgentResult:
        """
        Execute Investment Committee domain logic.

        BaseAgent.execute() owns the generic execution lifecycle.

        IMPORTANT
        ---------
        The current LLMService.generate() implementation is
        synchronous and returns a string. Therefore it MUST NOT
        be awaited here.
        """

        agent_results = context.agent_results

        research = self._build_research_context(
            agent_results
        )

        prompt = self._build_prompt(
            context=context,
            research=research,
        )

        # -----------------------------------------------------
        # LLM
        # -----------------------------------------------------
        # LLMService.generate() currently returns a normal
        # Python value, typically a string.
        #
        # Therefore:
        #
        #     response = llm.generate(...)
        #
        # NOT:
        #
        #     response = await llm.generate(...)
        # -----------------------------------------------------

        llm = self.services.llm

        response = llm.generate(
            prompt=prompt,
        )

        decision = self._parse_decision(
            response
        )

        return AgentResult.success(
            agent_name=self.agent_id,
            task_id=str(
                context.task_id or ""
            ),
            data=decision,
            findings=decision.get(
                "findings",
                [],
            ),
            evidence=self._collect_evidence(
                agent_results
            ),
            citations=self._collect_citations(
                agent_results
            ),
            confidence=self._normalize_confidence(
                decision.get(
                    "confidence",
                    0.0,
                )
            ),
            reasoning=decision.get(
                "thesis",
                "",
            ),
            metadata={
                "reviewed_agents": list(
                    agent_results.keys()
                ),
                "decision": decision.get(
                    "decision",
                    "",
                ),
                "key_reasons": decision.get(
                    "key_reasons",
                    [],
                ),
                "major_risks": decision.get(
                    "major_risks",
                    [],
                ),
                "catalysts": decision.get(
                    "catalysts",
                    [],
                ),
                "valuation_view": decision.get(
                    "valuation_view",
                    "",
                ),
            },
        )

    # =========================================================
    # Research Context
    # =========================================================

    def _build_research_context(
        self,
        agent_results: Dict[str, AgentResult],
    ) -> Dict[str, Any]:
        """
        Convert prior AgentResults into committee-level
        research context.

        The Investment Committee result itself is excluded
        to prevent recursive self-reference.
        """

        research: Dict[str, Any] = {}

        for agent_name, result in agent_results.items():

            if agent_name in {
                self.agent_id,
                self.name,
            }:
                continue

            research[agent_name] = {
                "data": getattr(
                    result,
                    "data",
                    {},
                ),
                "findings": getattr(
                    result,
                    "findings",
                    [],
                ),
                "confidence": getattr(
                    result,
                    "confidence",
                    0.0,
                ),
                "reasoning": getattr(
                    result,
                    "reasoning",
                    None,
                ),
                "evidence": getattr(
                    result,
                    "evidence",
                    [],
                ),
                "citations": getattr(
                    result,
                    "citations",
                    [],
                ),
                "sources": getattr(
                    result,
                    "sources",
                    [],
                ),
                "status": getattr(
                    result,
                    "status",
                    None,
                ),
            }

        return research

    # =========================================================
    # Prompt Construction
    # =========================================================

    def _build_prompt(
        self,
        context: AgentContext,
        research: Dict[str, Any],
    ) -> str:
        """
        Build the Investment Committee synthesis prompt.
        """

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

        company_context = ""

        if company:
            company_context += (
                f"\nCompany: {company}"
            )

        if ticker:
            company_context += (
                f"\nTicker: {ticker}"
            )

        return f"""
You are the Investment Committee for a professional
multi-agent equity research system.

{company_context}

You are reviewing research produced by specialized
research agents.

Your responsibilities are to:

1. Synthesize the research across all agents.
2. Identify areas where agents agree.
3. Identify material disagreements between agents.
4. Evaluate the strength of the investment thesis.
5. Assess financial quality and business fundamentals.
6. Evaluate industry and competitive positioning.
7. Consider macroeconomic conditions.
8. Consider relevant news and catalysts.
9. Evaluate valuation.
10. Evaluate downside risks.
11. Consider the CriticAgent's quality and reliability assessment.
12. Distinguish strong evidence from weak or uncertain claims.
13. Avoid inventing facts that are not supported by the research.
14. Produce a final investment-level decision.

Research from specialized agents:

{research}

Return a structured investment decision containing:

- decision
- thesis
- key_reasons
- major_risks
- catalysts
- valuation_view
- confidence
- findings

The decision should clearly communicate the overall
investment conclusion and the reasoning supporting it.

Confidence must be a numeric value between 0.0 and 1.0.

Do not invent facts, financial figures, citations,
or evidence that are not present in the supplied research.
"""

    # =========================================================
    # Decision Parsing
    # =========================================================

    def _parse_decision(
        self,
        response: Any,
    ) -> Dict[str, Any]:
        """
        Normalize the LLM response into committee decision data.

        Supports dictionary responses and falls back to a
        conservative free-form representation for string responses.
        """

        if isinstance(
            response,
            dict,
        ):
            decision = dict(response)

            decision.setdefault(
                "decision",
                "",
            )

            decision.setdefault(
                "thesis",
                "",
            )

            decision.setdefault(
                "key_reasons",
                [],
            )

            decision.setdefault(
                "major_risks",
                [],
            )

            decision.setdefault(
                "catalysts",
                [],
            )

            decision.setdefault(
                "valuation_view",
                "",
            )

            decision.setdefault(
                "findings",
                [],
            )

            decision.setdefault(
                "confidence",
                0.0,
            )

            return decision

        response_text = str(
            response
        ).strip()

        return {
            "decision": response_text,
            "thesis": response_text,
            "key_reasons": [],
            "major_risks": [],
            "catalysts": [],
            "valuation_view": "",
            "findings": [],
            "confidence": 0.0,
        }

    # =========================================================
    # Confidence
    # =========================================================

    def _normalize_confidence(
        self,
        value: Any,
    ) -> float:
        """
        Normalize confidence into the canonical [0.0, 1.0] range.
        """

        try:
            confidence = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                confidence,
            )
        )

    # =========================================================
    # Evidence
    # =========================================================

    def _collect_evidence(
        self,
        agent_results: Dict[str, AgentResult],
    ) -> list[Any]:
        """
        Collect evidence from upstream agents.
        """

        evidence: list[Any] = []

        for result in agent_results.values():

            if getattr(
                result,
                "agent_name",
                None,
            ) in {
                self.agent_id,
                self.name,
            }:
                continue

            result_evidence = getattr(
                result,
                "evidence",
                None,
            )

            if result_evidence:
                evidence.extend(
                    result_evidence
                )

        return evidence

    # =========================================================
    # Citations
    # =========================================================

    def _collect_citations(
        self,
        agent_results: Dict[str, AgentResult],
    ) -> list[Any]:
        """
        Collect citations from upstream agents.
        """

        citations: list[Any] = []

        for result in agent_results.values():

            if getattr(
                result,
                "agent_name",
                None,
            ) in {
                self.agent_id,
                self.name,
            }:
                continue

            result_citations = getattr(
                result,
                "citations",
                None,
            )

            if result_citations:
                citations.extend(
                    result_citations
                )

        return citations