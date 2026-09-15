from __future__ import annotations

from typing import Dict


class MultiplesAnalysis:
    """
    Relative valuation using financial multiples.

    Supports:
    - P/E
    - EV/EBITDA
    - EV/Revenue
    - Price/Sales
    """


    def calculate_pe_value(
        self,
        earnings_per_share: float,
        industry_pe: float,
    ) -> float:
        """
        Estimate share price using P/E multiple.
        """

        return earnings_per_share * industry_pe



    def calculate_ev_ebitda_value(
        self,
        ebitda: float,
        industry_ev_ebitda: float,
        debt: float,
        cash: float,
        shares: float,
    ) -> float:
        """
        Enterprise Value / EBITDA valuation.
        """

        enterprise_value = (
            ebitda *
            industry_ev_ebitda
        )

        equity_value = (
            enterprise_value
            - debt
            + cash
        )

        return equity_value / shares



    def calculate_ev_revenue_value(
        self,
        revenue: float,
        industry_ev_revenue: float,
        debt: float,
        cash: float,
        shares: float,
    ) -> float:
        """
        Enterprise Value / Revenue valuation.
        """

        enterprise_value = (
            revenue *
            industry_ev_revenue
        )

        equity_value = (
            enterprise_value
            - debt
            + cash
        )

        return equity_value / shares



    def compare_methods(
        self,
        valuations: Dict[str, float],
    ) -> Dict:

        valid_values = [
            value
            for value in valuations.values()
            if value
        ]


        average_value = (
            sum(valid_values)
            /
            len(valid_values)
            if valid_values
            else 0
        )


        return {
            "methods": valuations,
            "average_fair_value": average_value
        }