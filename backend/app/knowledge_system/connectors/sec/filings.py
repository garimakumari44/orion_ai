from __future__ import annotations

from typing import List, Dict

from .client import SECClient



class FilingService:


    def __init__(
        self,
        client: SECClient
    ):

        self.client = client



    def get_company_submissions(
        self,
        cik: str
    ):

        """
        Get filing history.
        """


        cik = cik.zfill(10)


        endpoint = (
            f"/submissions/"
            f"CIK{cik}.json"
        )


        return self.client.get(endpoint)



    def list_filings(
        self,
        cik: str,
        form_type: str = "10-K"
    ) -> List[Dict]:


        data = self.get_company_submissions(cik)


        recent = (
            data
            ["filings"]
            ["recent"]
        )


        filings=[]


        for i, form in enumerate(
            recent["form"]
        ):

            if form == form_type:

                filings.append(
                    {
                        "accession":
                            recent["accessionNumber"][i],

                        "date":
                            recent["filingDate"][i],

                        "report":
                            recent["primaryDocument"][i]
                    }
                )


        return filings



    def latest_filing(
        self,
        cik:str,
        form_type:str="10-K"
    ):

        filings = self.list_filings(
            cik,
            form_type
        )


        if not filings:
            return None


        return filings[0]