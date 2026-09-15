from __future__ import annotations

from typing import Dict, Any


class CashFlowAnalyzer:
    """
    Cash Flow Analyzer

    Analyzes:
    - Operating cash flow
    - Capital expenditure
    - Free cash flow
    - Cash conversion
    - Liquidity strength
    """

    def analyze(
        self,
        cashflow: Dict[str, Any]
    ) -> Dict[str, Any]:

        operating_cash_flow = cashflow.get(
            "operating_cash_flow",
            []
        )

        capital_expenditure = cashflow.get(
            "capital_expenditure",
            []
        )

        free_cash_flow = (
            self._calculate_free_cash_flow(
                operating_cash_flow,
                capital_expenditure
            )
        )


        return {

            "operating_cash_flow":
                operating_cash_flow,

            "capital_expenditure":
                capital_expenditure,

            "free_cash_flow":
                free_cash_flow,

            "cash_quality":
                self._cash_quality(
                    free_cash_flow
                ),

            "insights":
                self._generate_insights(
                    free_cash_flow
                )
        }



    def _calculate_free_cash_flow(
        self,
        operating_cash_flow,
        capex
    ):

        if not operating_cash_flow:
            return []


        result = []


        for index, cash in enumerate(
            operating_cash_flow
        ):

            investment = 0

            if index < len(capex):
                investment = capex[index]


            result.append(
                cash - investment
            )


        return result



    def _cash_quality(
        self,
        free_cash_flow
    ):

        if not free_cash_flow:

            return "unknown"


        positive_years = len(
            [
                value
                for value in free_cash_flow
                if value > 0
            ]
        )


        if positive_years == len(
            free_cash_flow
        ):

            return "strong"


        elif positive_years > 0:

            return "mixed"


        return "weak"



    def _generate_insights(
        self,
        free_cash_flow
    ):

        insights = []


        if not free_cash_flow:
            return insights


        if free_cash_flow[-1] > 0:

            insights.append(
                "Company generates positive free cash flow."
            )

        else:

            insights.append(
                "Company has negative free cash flow."
            )


        return insights