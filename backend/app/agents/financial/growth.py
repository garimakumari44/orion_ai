from __future__ import annotations

from typing import Dict, Any


class GrowthAnalyzer:
    """
    Growth Analyzer

    Evaluates:

    - Revenue growth
    - Earnings growth
    - Operating growth
    - Growth consistency
    - Business expansion quality
    """

    def analyze(
        self,
        financial_history: Dict[str, Any]
    ) -> Dict[str, Any]:

        revenue = financial_history.get(
            "revenue",
            []
        )

        earnings = financial_history.get(
            "net_income",
            []
        )

        operating_income = financial_history.get(
            "operating_income",
            []
        )


        return {

            "revenue_growth":

                self._growth_metrics(
                    revenue
                ),


            "earnings_growth":

                self._growth_metrics(
                    earnings
                ),


            "operating_growth":

                self._growth_metrics(
                    operating_income
                ),


            "growth_quality":

                self._growth_quality(
                    revenue,
                    earnings
                )
        }



    def _growth_metrics(
        self,
        values
    ):

        if len(values) < 2:

            return {
                "growth": None
            }


        start = values[0]
        end = values[-1]


        if start == 0:

            return {
                "growth": None
            }


        growth = (
            (end - start)
            /
            abs(start)
        ) * 100


        return {

            "start":
                start,

            "end":
                end,

            "growth_percent":
                round(
                    growth,
                    2
                )
        }



    def _growth_quality(
        self,
        revenue,
        earnings
    ):

        if len(revenue) < 2:

            return "insufficient_data"


        revenue_positive = (
            revenue[-1] > revenue[0]
        )


        earnings_positive = (
            earnings
            and earnings[-1] > earnings[0]
        )


        if revenue_positive and earnings_positive:

            return "high_quality_growth"


        if revenue_positive:

            return "revenue_growth_only"


        return "weak_growth"