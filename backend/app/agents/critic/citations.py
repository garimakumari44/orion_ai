"""
Citation Validator

Ensures research claims are
linked with proper sources.
"""

from typing import List, Dict, Any


class CitationValidator:
    """
    Validates citation quality.

    Checks:
    - Source existence
    - Source relevance
    - Citation coverage
    """

    def __init__(self):

        self.accepted_sources = [
            "sec",
            "company_filing",
            "earnings_call",
            "financial_database",
            "news"
        ]



    async def validate(
        self,
        claims: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        results = []

        for claim in claims:

            result = self.check_claim(
                claim
            )

            results.append(
                result
            )


        return {

            "citation_score":
                self.calculate_score(
                    results
                ),

            "results":
                results
        }



    def check_claim(
        self,
        claim: Dict[str, Any]
    ) -> Dict[str, Any]:

        citations = claim.get(
            "citations",
            []
        )


        if not citations:

            return {

                "claim": claim,
                "status": "missing",
                "score": 0

            }


        valid = any(

            source in str(citations).lower()

            for source
            in self.accepted_sources

        )


        return {

            "claim": claim,

            "status":
                "valid"
                if valid
                else
                "weak",

            "score":
                1
                if valid
                else
                0.5
        }



    def calculate_score(
        self,
        results
    ):

        if not results:
            return 0


        return round(

            sum(
                r["score"]
                for r in results
            )
            /
            len(results),

            2

        )