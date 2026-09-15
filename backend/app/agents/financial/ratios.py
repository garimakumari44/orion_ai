from __future__ import annotations

from typing import Dict, Any


class FinancialRatioAnalyzer:
    """
    Financial Ratio Analyzer

    Calculates:

    Profitability:
    - Gross Margin
    - Operating Margin
    - Net Margin

    Solvency:
    - Debt Equity Ratio

    Liquidity:
    - Current Ratio

    Efficiency:
    - ROE
    - ROA
    """



    def analyze(
        self,
        financials: Dict[str, Any]
    ) -> Dict[str, Any]:


        revenue = financials.get(
            "revenue",
            0
        )

        gross_profit = financials.get(
            "gross_profit",
            0
        )

        operating_income = financials.get(
            "operating_income",
            0
        )

        net_income = financials.get(
            "net_income",
            0
        )

        assets = financials.get(
            "assets",
            0
        )

        equity = financials.get(
            "equity",
            0
        )

        debt = financials.get(
            "debt",
            0
        )

        current_assets = financials.get(
            "current_assets",
            0
        )

        current_liabilities = financials.get(
            "current_liabilities",
            0
        )


        return {


            "profitability":
            {

                "gross_margin":
                    self._percentage(
                        gross_profit,
                        revenue
                    ),

                "operating_margin":
                    self._percentage(
                        operating_income,
                        revenue
                    ),

                "net_margin":
                    self._percentage(
                        net_income,
                        revenue
                    )
            },


            "returns":
            {

                "ROA":
                    self._percentage(
                        net_income,
                        assets
                    ),

                "ROE":
                    self._percentage(
                        net_income,
                        equity
                    )
            },


            "leverage":
            {

                "debt_to_equity":
                    self._ratio(
                        debt,
                        equity
                    )
            },


            "liquidity":
            {

                "current_ratio":
                    self._ratio(
                        current_assets,
                        current_liabilities
                    )

            }

        }




    def _percentage(
        self,
        numerator,
        denominator
    ):

        if denominator == 0:

            return None


        return round(
            (numerator / denominator)
            * 100,
            2
        )



    def _ratio(
        self,
        numerator,
        denominator
    ):

        if denominator == 0:

            return None


        return round(
            numerator /
            denominator,
            2
        )