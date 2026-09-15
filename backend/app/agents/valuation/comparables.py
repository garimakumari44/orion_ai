from __future__ import annotations

from typing import List

from .models import ComparableCompany


class ComparableAnalysis:
    """
    Peer comparison valuation model.

    Uses similar companies to estimate
    relative valuation.
    """

    def __init__(
        self,
        companies: List[ComparableCompany],
    ):
        self.companies = companies


    def average_multiple(
        self,
        metric: str,
    ) -> float:

        values = []

        for company in self.companies:

            value = getattr(
                company,
                metric,
                None
            )

            if value:
                values.append(value)


        if not values:
            return 0


        return sum(values) / len(values)



    def valuation_summary(self):

        return {

            "average_pe":
                self.average_multiple(
                    "pe_ratio"
                ),

            "average_ev_revenue":
                self.average_multiple(
                    "ev_revenue"
                ),

            "average_ev_ebitda":
                self.average_multiple(
                    "ev_ebitda"
                ),

            "peer_count":
                len(self.companies)
        }