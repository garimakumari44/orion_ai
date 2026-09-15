from __future__ import annotations

from typing import Dict, Any


class BalanceSheetAnalyzer:
    """
    Balance Sheet Analyzer

    Evaluates:
    - Assets
    - Liabilities
    - Equity
    - Debt levels
    - Financial stability
    """



    def analyze(
        self,
        balance_sheet: Dict[str, Any]
    ) -> Dict[str, Any]:


        assets = balance_sheet.get(
            "total_assets",
            0
        )


        liabilities = balance_sheet.get(
            "total_liabilities",
            0
        )


        equity = balance_sheet.get(
            "shareholders_equity",
            0
        )


        debt = balance_sheet.get(
            "total_debt",
            0
        )


        return {


            "financial_position":
            {

                "assets":
                    assets,

                "liabilities":
                    liabilities,

                "equity":
                    equity

            },


            "leverage":

            self._calculate_leverage(
                debt,
                equity
            ),


            "health_score":

            self._health_score(
                assets,
                liabilities
            )

        }




    def _calculate_leverage(
        self,
        debt,
        equity
    ):


        if equity == 0:

            return None


        return round(
            debt / equity,
            2
        )




    def _health_score(
        self,
        assets,
        liabilities
    ):

        if assets == 0:

            return 0


        ratio = (
            assets - liabilities
        ) / assets


        score = ratio * 100


        return round(
            max(
                0,
                min(
                    score,
                    100
                )
            ),
            2
        )