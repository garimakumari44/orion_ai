"""
Critic Agent prompt templates.

The Critic Agent performs quality assurance for equity research.

Responsibilities:
- Verify factual accuracy.
- Validate financial evidence.
- Detect unsupported conclusions.
- Check consistency across analyst outputs.
- Evaluate completeness.
- Recommend improvements.

The Critic NEVER rewrites reports.
"""

from textwrap import dedent


class CriticPrompts:
    """Prompt templates for the Equity Research Critic Agent."""

    @staticmethod
    def system_prompt() -> str:
        return dedent(
            """
            You are an expert Equity Research Critic Agent.

            Your responsibility is quality assurance.

            Evaluate whether a research report is supported by
            the available evidence.

            Responsibilities

            - Verify factual accuracy.
            - Detect unsupported claims.
            - Detect hallucinations.
            - Verify financial metrics.
            - Verify consistency with retrieved evidence.
            - Check logical reasoning.
            - Check valuation assumptions.
            - Check risk coverage.
            - Check citation coverage.
            - Evaluate completeness.
            - Evaluate clarity.
            - Suggest improvements.

            Never rewrite the report.

            Never introduce new facts.

            Return JSON only.
            """
        ).strip()

    @staticmethod
    def review_prompt(
        objective: str,
        response: str,
        supporting_research: str,
    ) -> str:

        return dedent(
            f"""
            Research Objective

            {objective}

            --------------------------------------

            Draft Report

            {response}

            --------------------------------------

            Supporting Evidence

            {supporting_research}

            --------------------------------------

            Review the report.

            Evaluate

            1. Financial accuracy
            2. Evidence support
            3. Logical consistency
            4. Completeness
            5. Missing risks
            6. Unsupported assumptions
            7. Citation coverage
            8. Valuation consistency
            9. Investment conclusion consistency
            10. Overall quality

            Return JSON.

            {{
                "overall_score": 0,
                "financial_accuracy": 0,
                "evidence_support": 0,
                "logic": 0,
                "clarity": 0,
                "completeness": 0,
                "hallucinations": [],
                "unsupported_claims": [],
                "missing_risks": [],
                "missing_information": [],
                "citation_issues": [],
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "approved": true
            }}
            """
        ).strip()

    @staticmethod
    def fact_check_prompt(
        statement: str,
        evidence: str,
    ) -> str:

        return dedent(
            f"""
            Statement

            {statement}

            --------------------------------------

            Supporting Evidence

            {evidence}

            --------------------------------------

            Classify the statement as

            - Supported
            - Partially Supported
            - Unsupported
            - Contradicted

            Identify

            - supporting evidence
            - conflicting evidence
            - confidence

            Return JSON.

            {{
                "status": "",
                "confidence": 0.0,
                "supporting_evidence": [],
                "conflicting_evidence": [],
                "reasoning": ""
            }}
            """
        ).strip()