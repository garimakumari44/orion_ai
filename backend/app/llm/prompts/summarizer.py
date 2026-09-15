"""
Summarizer Agent prompt templates.

The Summarizer Agent condenses financial research while preserving
the most important facts, financial metrics, investment conclusions,
and supporting evidence.

Responsibilities:
- Produce concise, accurate research summaries.
- Preserve key financial information.
- Highlight investment-relevant insights.
- Never invent facts, metrics, or conclusions.
"""

from textwrap import dedent
from typing import Literal


class SummarizerPrompts:
    """Prompt templates for the Equity Research Summarizer Agent."""

    @staticmethod
    def system_prompt() -> str:
        return dedent(
            """
            You are an expert Equity Research Summarizer.

            Your role is to summarize financial and investment research
            while preserving all critical information needed for informed
            investment decisions.

            Responsibilities:

            - Preserve factual accuracy.
            - Never fabricate financial information.
            - Preserve important financial metrics.
            - Preserve investment conclusions.
            - Highlight business performance.
            - Highlight risks and catalysts.
            - Maintain neutrality.
            - Remove redundancy.
            - Produce clear, structured summaries.
            """
        ).strip()

    @staticmethod
    def summarize_prompt(
        content: str,
        summary_type: Literal["brief", "standard", "detailed"] = "standard",
    ) -> str:
        return dedent(
            f"""
            Financial Research

            {content}

            ----------------------------------------

            Generate a {summary_type} summary.

            Requirements:

            - Preserve key business facts.
            - Preserve important financial metrics.
            - Preserve investment conclusions.
            - Highlight revenue, profitability, cash flow,
              valuation, and growth when available.
            - Highlight major risks.
            - Highlight important catalysts.
            - Remove repetition.
            - Keep the original meaning.
            - Do not fabricate information.
            """
        ).strip()

    @staticmethod
    def company_summary_prompt(
        company_analysis: str,
    ) -> str:
        return dedent(
            f"""
            Company Analysis

            {company_analysis}

            Produce a structured summary containing:

            - Company overview
            - Business model
            - Financial performance
            - Competitive position
            - Growth drivers
            - Risks
            - Investment thesis
            - Overall conclusion
            """
        ).strip()

    @staticmethod
    def earnings_summary_prompt(
        earnings_report: str,
    ) -> str:
        return dedent(
            f"""
            Earnings Report

            {earnings_report}

            Produce a structured earnings summary including:

            - Quarter and reporting period
            - Revenue performance
            - Earnings performance
            - Margin performance
            - Cash flow highlights
            - Guidance
            - Management commentary
            - Key risks
            - Positive developments
            - Negative developments
            """
        ).strip()

    @staticmethod
    def investment_memo_summary_prompt(
        memo: str,
    ) -> str:
        return dedent(
            f"""
            Investment Memo

            {memo}

            Produce a concise investment memo summary.

            Include:

            - Investment thesis
            - Supporting evidence
            - Key assumptions
            - Valuation summary
            - Bull case
            - Bear case
            - Major risks
            - Recommendation
            """
        ).strip()

    @staticmethod
    def conversation_summary_prompt(
        transcript: str,
    ) -> str:
        return dedent(
            f"""
            Research Conversation

            {transcript}

            Produce a structured summary.

            Include:

            - Research objective
            - Companies discussed
            - Main findings
            - Financial insights
            - Decisions made
            - Action items
            - Outstanding questions
            - Next research steps
            """
        ).strip()

    @staticmethod
    def document_summary_prompt(
        document: str,
    ) -> str:
        return dedent(
            f"""
            Financial Document

            {document}

            Produce:

            - Executive summary
            - Key findings
            - Important financial metrics
            - Significant business developments
            - Risks
            - Catalysts
            - Conclusions
            - Investment implications
            """
        ).strip()