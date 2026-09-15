from __future__ import annotations

from typing import Dict

from app.agents.industry.models import MarketSizeResult


class MarketSizeAnalyzer:
    """
    Analyzes TAM, SAM, SOM and market growth.
    """


    def __init__(self):
        pass


    def analyze(
        self,
        industry: str,
        data: Dict
    ) -> MarketSizeResult:
        """
        Generate market size analysis.
        """

        return MarketSizeResult(

            industry=industry,

            tam=data.get(
                "tam"
            ),

            sam=data.get(
                "sam"
            ),

            som=data.get(
                "som"
            ),

            growth_rate=data.get(
                "growth_rate"
            ),

            forecast=data.get(
                "forecast"
            )
        )


    def calculate_growth(
        self,
        current_value: float,
        future_value: float,
        years: int
    ) -> float:
        """
        Calculate CAGR.
        """

        if years <= 0:
            return 0


        cagr = (
            (future_value / current_value)
            ** (1 / years)
        ) - 1


        return round(
            cagr * 100,
            2
        )