from __future__ import annotations

from typing import Dict, Any


class CapitalAllocationAnalyzer:
    """
    Capital Allocation Analyzer

    Evaluates:

    - Dividend policy
    - Share buybacks
    - Debt reduction
    - Acquisitions
    - Reinvestment strategy
    - Management discipline
    """



    def analyze(
        self,
        capital_data: Dict[str, Any]
    ) -> Dict[str, Any]:


        dividends = capital_data.get(
            "dividends",
            []
        )

        buybacks = capital_data.get(
            "share_buybacks",
            []
        )

        debt_repayment = capital_data.get(
            "debt_repayment",
            []
        )

        acquisitions = capital_data.get(
            "acquisitions",
            []
        )

        capex = capital_data.get(
            "capital_expenditure",
            []
        )


        return {


            "dividend_policy":

                self._evaluate_activity(
                    dividends
                ),


            "buyback_activity":

                self._evaluate_activity(
                    buybacks
                ),


            "debt_management":

                self._evaluate_activity(
                    debt_repayment
                ),


            "acquisition_strategy":

                self._evaluate_activity(
                    acquisitions
                ),


            "reinvestment":

                self._evaluate_activity(
                    capex
                ),


            "management_quality":

                self._management_score(
                    capital_data
                )

        }




    def _evaluate_activity(
        self,
        values
    ):


        if not values:

            return "no_data"


        total = sum(values)


        if total > 0:

            return "active"


        return "inactive"




    def _management_score(
        self,
        data
    ):

        score = 50


        if data.get(
            "share_buybacks"
        ):

            score += 10


        if data.get(
            "debt_repayment"
        ):

            score += 10


        if data.get(
            "acquisitions"
        ):

            score += 5


        return min(
            score,
            100
        )