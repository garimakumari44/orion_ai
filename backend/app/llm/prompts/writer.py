"""
Writer Agent prompt templates.

The Writer Agent transforms structured financial research into
professional, evidence-based equity research reports and investment
documents.

Responsibilities:
- Produce institutional-quality financial writing.
- Preserve factual accuracy.
- Use only supplied evidence.
- Never fabricate financial information.
- Present balanced investment analysis.
"""

from textwrap import dedent
from typing import Optional


class WriterPrompts:
    """Prompt templates for the Equity Research Writer Agent."""

    @staticmethod
    def system_prompt() -> str:
        return dedent(
            """
            You are an expert Equity Research Writer.

            Your responsibility is to transform structured research into
            professional investment research documents suitable for
            analysts, portfolio managers, and investors.

            Responsibilities:

            - Write clear, professional financial reports.
            - Preserve factual accuracy.
            - Never fabricate financial information.
            - Use only supplied evidence.
            - Distinguish facts from assumptions.
            - Present balanced bullish and bearish perspectives.
            - Organize information logically.
            - Highlight key financial metrics.
            - Explain investment implications clearly.
            - Cite evidence whenever available.
            - State uncertainty when evidence is insufficient.

            Do not critique your own writing.
            """
        ).strip()

    @staticmethod
    def write_prompt(
        objective: str,
        research: str,
        audience: str = "Investment Professionals",
        tone: str = "Professional",
        style: Optional[str] = None,
    ) -> str:

        style = style or "Clear, analytical, and evidence-based."

        return dedent(
            f"""
            Objective

            {objective}

            --------------------------------------------------

            Research

            {research}

            --------------------------------------------------

            Audience

            {audience}

            --------------------------------------------------

            Tone

            {tone}

            --------------------------------------------------

            Style

            {style}

            --------------------------------------------------

            Write a complete equity research report.

            Requirements:

            - Use only the supplied evidence.
            - Never invent financial metrics or conclusions.
            - Distinguish facts from interpretation.
            - Highlight important financial metrics.
            - Explain business performance.
            - Discuss growth opportunities.
            - Identify major risks.
            - Present valuation insights when available.
            - Mention important catalysts.
            - Keep recommendations evidence-based.
            - Organize the report with appropriate headings.
            - Finish with a concise investment conclusion.
            """
        ).strip()

    @staticmethod
    def investment_memo_prompt(
        research: str,
    ) -> str:
        return dedent(
            f"""
            Research

            {research}

            Produce a professional investment memo.

            Include:

            - Executive Summary
            - Investment Thesis
            - Business Overview
            - Industry Overview
            - Financial Analysis
            - Competitive Position
            - Valuation
            - Risks
            - Catalysts
            - Recommendation
            """
        ).strip()

    @staticmethod
    def earnings_report_prompt(
        research: str,
    ) -> str:
        return dedent(
            f"""
            Earnings Research

            {research}

            Write an earnings analysis.

            Include:

            - Quarter Summary
            - Revenue Performance
            - Earnings Performance
            - Margin Analysis
            - Cash Flow
            - Guidance
            - Management Commentary
            - Positive Developments
            - Risks
            - Overall Assessment
            """
        ).strip()

    @staticmethod
    def company_analysis_prompt(
        research: str,
    ) -> str:
        return dedent(
            f"""
            Company Research

            {research}

            Write a comprehensive company analysis.

            Include:

            - Company Overview
            - Business Model
            - Revenue Drivers
            - Financial Performance
            - Competitive Advantages
            - Industry Position
            - Growth Opportunities
            - Risks
            - Valuation
            - Investment Outlook
            """
        ).strip()

    @staticmethod
    def valuation_report_prompt(
        research: str,
    ) -> str:
        return dedent(
            f"""
            Valuation Research

            {research}

            Produce a valuation report.

            Include:

            - Valuation Methodology
            - Key Assumptions
            - Comparable Companies
            - Valuation Multiples
            - Fair Value Assessment
            - Sensitivity Analysis
            - Risks
            - Conclusion
            """
        ).strip()