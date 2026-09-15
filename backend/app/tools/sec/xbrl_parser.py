"""
SEC XBRL Parser

Extracts financial metrics.
"""


from typing import Dict, Optional



class XBRLParser:



    def extract_metric(
        self,
        facts: Dict,
        concept: str
    ) -> Optional[Dict]:


        us_gaap = (
            facts
            .get("facts", {})
            .get("us-gaap", {})
        )


        metric = us_gaap.get(
            concept
        )


        if not metric:
            return None



        units = metric.get(
            "units"
        )


        values = []


        for unit in units:

            values.extend(
                units[unit]
            )


        values.sort(
            key=lambda x:
            x.get(
                "filed",
                ""
            ),
            reverse=True
        )


        if values:

            return values[0]


        return None



    def financial_summary(
        self,
        facts: Dict
    ) -> Dict:


        metrics = {

            "revenue":
                "Revenues",

            "net_income":
                "NetIncomeLoss",

            "assets":
                "Assets",

            "cash":
                "CashAndCashEquivalentsAtCarryingValue",

            "debt":
                "LongTermDebtNoncurrent"

        }



        result = {}


        for name, concept in metrics.items():

            result[name] = (
                self.extract_metric(
                    facts,
                    concept
                )
            )


        return result