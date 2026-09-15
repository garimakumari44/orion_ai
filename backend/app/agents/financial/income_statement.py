from __future__ import annotations

from typing import Dict, Any


class IncomeStatementAnalyzer:
    """
    Income Statement Analyzer

    Analyzes:
    - Revenue growth
    - Gross margin
    - Operating margin
    - Net income
    - Earnings trends
    """


    def analyze(
        self,
        statement: Dict[str, Any]
    ) -> Dict[str, Any]:

        revenue = statement.get(
            "revenue",
            []
        )

        net_income = statement.get(
            "net_income",
            []
        )

        operating_income = statement.get(
            "operating_income",
            []
        )


        return {

            "revenue_analysis":
                self._analyze_growth(
                    revenue
                ),

            "profitability":

                {
                    "operating_income":
                        operating_income,

                    "net_income":
                        net_income
                },

            "insights":
                self._generate_insights(
                    statement
                )
        }



    def _analyze_growth(
        self,
        values
    ):

        if len(values) < 2:
            return {
                "growth": None
            }


        latest = values[-1]

        previous = values[-2]


        if previous == 0:
            growth = None

        else:
            growth = (
                (latest - previous)
                /
                previous
            ) * 100


        return {

            "latest":
                latest,

            "previous":
                previous,

            "growth_percent":
                round(
                    growth,
                    2
                )
                if growth
                else None
        }



    def _generate_insights(
        self,
        statement
    ):

        insights = []


        revenue = statement.get(
            "revenue",
            []
        )


        if len(revenue) >= 2:

            if revenue[-1] > revenue[-2]:

                insights.append(
                    "Revenue is growing."
                )

            else:

                insights.append(
                    "Revenue growth is slowing."
                )


        return insights