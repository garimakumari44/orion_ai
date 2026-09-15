from __future__ import annotations

from typing import Dict

from app.agents.industry.models import PorterAnalysisResult


class PorterAnalyzer:
    """
    Performs Porter's Five Forces analysis.

    Used by IndustryResearchAgent.
    """

    def __init__(self):
        pass


    def analyze(
        self,
        industry: str,
        data: Dict
    ) -> PorterAnalysisResult:
        """
        Analyze industry competitive forces.

        Args:
            industry:
                Industry name

            data:
                Retrieved industry information

        Returns:
            PorterAnalysisResult
        """

        return PorterAnalysisResult(

            industry=industry,

            supplier_power=data.get(
                "supplier_power",
                "Unknown"
            ),

            buyer_power=data.get(
                "buyer_power",
                "Unknown"
            ),

            competitive_rivalry=data.get(
                "competitive_rivalry",
                "Unknown"
            ),

            threat_of_substitutes=data.get(
                "threat_of_substitutes",
                "Unknown"
            ),

            threat_of_new_entrants=data.get(
                "threat_of_new_entrants",
                "Unknown"
            ),

            summary=data.get(
                "summary"
            )
        )


    def generate_summary(
        self,
        result: PorterAnalysisResult
    ) -> str:

        return f"""
Industry: {result.industry}

Supplier Power:
{result.supplier_power}

Buyer Power:
{result.buyer_power}

Competitive Rivalry:
{result.competitive_rivalry}

Substitutes:
{result.threat_of_substitutes}

New Entrants:
{result.threat_of_new_entrants}
"""