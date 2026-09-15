from __future__ import annotations

from typing import Dict, List


class SupplyChainAnalyzer:
    """
    Analyzes industry supply chain structure.

    Covers:
    - Suppliers
    - Manufacturers
    - Distributors
    - Customers
    - Dependencies
    """


    def __init__(self):
        pass



    def analyze(
        self,
        data: Dict
    ) -> Dict:
        """
        Build supply chain analysis.
        """

        return {

            "suppliers": data.get(
                "suppliers",
                []
            ),

            "manufacturers": data.get(
                "manufacturers",
                []
            ),

            "distributors": data.get(
                "distributors",
                []
            ),

            "customers": data.get(
                "customers",
                []
            ),

            "dependencies": data.get(
                "dependencies",
                []
            ),

            "risks": data.get(
                "risks",
                []
            )
        }



    def identify_risks(
        self,
        supply_chain: Dict
    ) -> List[str]:
        """
        Identify supply chain risks.
        """

        risks = []


        if not supply_chain.get(
            "suppliers"
        ):
            risks.append(
                "No supplier information available"
            )


        if supply_chain.get(
            "dependencies"
        ):
            risks.extend(
                supply_chain["dependencies"]
            )


        return risks