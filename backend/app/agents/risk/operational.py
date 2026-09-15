from __future__ import annotations

import logging
from typing import Dict, Any, List


logger = logging.getLogger(__name__)


class OperationalRiskAnalyzer:
    """
    Operational Risk Analyzer

    Evaluates:
    - Supply chain risks
    - Business dependency
    - Execution risks
    - Customer concentration
    - Technology risks
    """

    name = "operational_risk"


    async def analyze(
        self,
        company: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        risks = []


        operations = company.get(
            "operations",
            {}
        )


        supplier_dependency = operations.get(
            "supplier_dependency"
        )

        if supplier_dependency == "high":

            risks.append(
                {
                    "type": "supply_chain_risk",
                    "description":
                        "High dependency on limited suppliers",
                    "severity": 3,
                }
            )


        customer_dependency = operations.get(
            "customer_concentration"
        )

        if customer_dependency and customer_dependency > 0.3:

            risks.append(
                {
                    "type": "customer_concentration",
                    "description":
                        "Revenue depends heavily on few customers",
                    "severity": 3,
                    "metric": customer_dependency
                }
            )


        technology_dependency = operations.get(
            "technology_dependency"
        )

        if technology_dependency == "high":

            risks.append(
                {
                    "type": "technology_risk",
                    "description":
                        "Business highly dependent on technology infrastructure",
                    "severity": 2,
                }
            )


        return risks