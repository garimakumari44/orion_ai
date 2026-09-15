from __future__ import annotations

from typing import Dict, Any


class ProfitabilityAnalyzer:
    """
    Profitability Analyzer

    Evaluates:

    - Gross margins
    - Operating margins
    - Net margins
    - Margin expansion
    - Earnings quality
    """



    def analyze(
        self,
        financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:


        revenue = financial_data.get(
            "revenue",
            []
        )

        gross_profit = financial_data.get(
            "gross_profit",
            []
        )

        operating_income = financial_data.get(
            "operating_income",
            []
        )

        net_income = financial_data.get(
            "net_income",
            []
        )


        return {


            "gross_margin":

                self._calculate_margin(
                    gross_profit,
                    revenue
                ),


            "operating_margin":

                self._calculate_margin(
                    operating_income,
                    revenue
                ),


            "net_margin":

                self._calculate_margin(
                    net_income,
                    revenue
                ),


            "margin_trend":

                self._margin_trend(
                    operating_income,
                    revenue
                ),


            "quality":

                self._profitability_quality(
                    net_income
                )

        }




    def _calculate_margin(
        self,
        profit,
        revenue
    ):


        if not profit or not revenue:

            return []


        margins = []


        for p, r in zip(
            profit,
            revenue
        ):

            if r == 0:

                margins.append(None)

            else:

                margins.append(
                    round(
                        (p / r) * 100,
                        2
                    )
                )


        return margins




    def _margin_trend(
        self,
        operating_income,
        revenue
    ):


        margins = self._calculate_margin(
            operating_income,
            revenue
        )


        if len(margins) < 2:

            return "unknown"


        if margins[-1] > margins[0]:

            return "expanding"


        if margins[-1] < margins[0]:

            return "declining"


        return "stable"




    def _profitability_quality(
        self,
        net_income
    ):


        if not net_income:

            return "unknown"


        positive_years = len(
            [
                x
                for x in net_income
                if x > 0
            ]
        )


        if positive_years == len(
            net_income
        ):

            return "consistent_profitability"


        return "volatile_profitability"