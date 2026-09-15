"""
Research Agent prompt templates.

The Research Agent gathers and validates financial evidence for
equity research.

Responsibilities:
- Collect evidence from multiple financial sources.
- Validate information.
- Identify conflicting evidence.
- Detect knowledge gaps.
- Prepare structured research outputs.
- Never perform valuation or investment recommendations.
"""

from textwrap import dedent
from typing import List, Optional


class ResearcherPrompts:
    """Prompt templates for the Equity Research Agent."""

    @staticmethod
    def system_prompt() -> str:
        return dedent(
            """
            You are an expert Equity Research Agent.

            Your responsibility is to collect reliable financial
            information for downstream analyst agents.

            Responsibilities

            - Understand the research objective.
            - Gather financial evidence.
            - Compare multiple sources.
            - Validate factual consistency.
            - Identify conflicting information.
            - Extract quantitative metrics.
            - Extract qualitative insights.
            - Identify knowledge gaps.
            - Assess source credibility.
            - Never fabricate facts.
            - Never perform valuation.
            - Never make investment recommendations.

            Preferred evidence

            - SEC filings
            - Annual reports
            - Quarterly reports
            - Earnings call transcripts
            - Investor presentations
            - Official press releases
            - Exchange filings
            - Trusted financial news
            - Industry reports
            - Macroeconomic publications

            Always distinguish facts from assumptions.

            Return structured JSON only.
            """
        ).strip()

    @staticmethod
    def research_prompt(
        query: str,
        context: Optional[str] = None,
        available_sources: Optional[List[str]] = None,
    ) -> str:

        context = context or "No additional context."

        sources = (
            "\n".join(f"- {s}" for s in available_sources)
            if available_sources
            else "Any available financial source."
        )

        return dedent(
            f"""
            Research Objective

            {query}

            ------------------------------------

            Context

            {context}

            ------------------------------------

            Available Sources

            {sources}

            ------------------------------------

            Perform comprehensive financial research.

            Tasks

            1. Understand the objective.
            2. Gather financial evidence.
            3. Compare sources.
            4. Identify contradictions.
            5. Extract financial metrics.
            6. Extract management commentary.
            7. Extract industry information.
            8. Identify macroeconomic factors.
            9. Identify missing information.
            10. Estimate confidence.

            Return JSON.

            {{
                "objective": "",
                "summary": "",
                "financial_metrics": [],
                "qualitative_findings": [],
                "industry_findings": [],
                "macroeconomic_findings": [],
                "evidence": [],
                "contradictions": [],
                "knowledge_gaps": [],
                "confidence": 0.0
            }}
            """
        ).strip()

    @staticmethod
    def source_analysis_prompt(
        source_content: str,
    ) -> str:

        return dedent(
            f"""
            Analyze the following financial source.

            Source

            {source_content}

            Extract

            - important facts
            - financial metrics
            - management commentary
            - business developments
            - risks
            - opportunities
            - assumptions
            - source credibility
            - possible bias

            Return JSON.

            {{
                "facts": [],
                "financial_metrics": [],
                "management_commentary": [],
                "risks": [],
                "opportunities": [],
                "assumptions": [],
                "credibility": "",
                "bias": ""
            }}
            """
        ).strip()

    @staticmethod
    def compare_sources_prompt(
        sources: List[str],
    ) -> str:

        formatted = "\n\n".join(
            f"Source {i+1}:\n{text}"
            for i, text in enumerate(sources)
        )

        return dedent(
            f"""
            Compare the following financial sources.

            {formatted}

            Identify

            - agreements
            - disagreements
            - strongest evidence
            - weakest evidence
            - conflicting financial metrics
            - conflicting management statements
            - missing information

            Return JSON.

            {{
                "agreements": [],
                "disagreements": [],
                "strongest_evidence": [],
                "weakest_evidence": [],
                "conflicts": [],
                "missing_information": []
            }}
            """
        ).strip()

    @staticmethod
    def gap_analysis_prompt(
        objective: str,
        findings: str,
    ) -> str:

        return dedent(
            f"""
            Research Objective

            {objective}

            ------------------------------------

            Current Findings

            {findings}

            ------------------------------------

            Identify

            - unanswered questions
            - missing financial data
            - missing company disclosures
            - missing industry information
            - missing macroeconomic information
            - additional research required

            Return JSON.

            {{
                "knowledge_gaps": [],
                "additional_research": [],
                "confidence": 0.0
            }}
            """
        ).strip()

    @staticmethod
    def summarize_research_prompt(
        research_json: str,
    ) -> str:

        return dedent(
            f"""
            Summarize the structured research below.

            Research

            {research_json}

            Produce

            - executive_summary
            - key_financial_findings
            - major_business_findings
            - important_risks
            - remaining_uncertainties
            - confidence

            Return JSON.

            {{
                "executive_summary": "",
                "key_financial_findings": [],
                "major_business_findings": [],
                "important_risks": [],
                "remaining_uncertainties": [],
                "confidence": 0.0
            }}
            """
        ).strip()