from __future__ import annotations

from typing import Dict, Any

from .client import SECClient



class CompanyFactsService:


    def __init__(
        self,
        client: SECClient
    ):

        self.client = client



    def get_company_facts(
        self,
        cik: str
    ) -> Dict[str, Any]:

        """
        Fetch all company XBRL facts.

        Example:
        Apple CIK:
        0000320193
        """


        cik = cik.zfill(10)


        endpoint = (
            f"/api/xbrl/companyfacts/"
            f"CIK{cik}.json"
        )


        return self.client.get(endpoint)



    def get_financial_metric(
        self,
        cik: str,
        taxonomy: str,
        metric: str
    ):


        facts = self.get_company_facts(cik)


        try:

            data = (
                facts["facts"]
                [taxonomy]
                [metric]
            )

            return data


        except KeyError:

            return None