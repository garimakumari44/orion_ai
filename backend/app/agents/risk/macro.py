from __future__ import annotations

import logging
from typing import Dict, Any, List


logger = logging.getLogger(__name__)


class MacroRiskAnalyzer:
    """
    Macro Risk Analyzer

    Evaluates:
    - Interest rate sensitivity
    - Inflation exposure
    - Economic slowdown
    - Commodity exposure
    - Currency impact
    """

    name = "macro_risk"


    async def analyze(
        self,
        company: Dict[str, Any],
        macro_data: Dict[str, Any] | None = None
    ) -> List[Dict[str, Any]]:

        risks = []

        macro_data = macro_data or {}


        industry = company.get(
            "industry"
        )


        interest_rates = macro_data.get(
            "interest_rates"
        )

        if interest_rates == "rising":

            risks.append(
                {
                    "type": "interest_rate_risk",
                    "description":
                        "Higher rates may increase borrowing costs",
                    "severity": 3
                }
            )


        inflation = macro_data.get(
            "inflation"
        )

        if inflation == "high":

            risks.append(
                {
                    "type": "inflation_risk",
                    "description":
                        "Input cost inflation may pressure margins",
                    "severity": 3
                }
            )


        recession = macro_data.get(
            "recession_probability"
        )

        if recession and recession > 0.5:

            risks.append(
                {
                    "type": "economic_downturn",
                    "description":
                        "Potential recession impact on business performance",
                    "severity": 4,
                    "probability": recession
                }
            )


        commodity_dependency = company.get(
            "commodity_dependency"
        )

        if commodity_dependency == "high":

            risks.append(
                {
                    "type": "commodity_price_risk",
                    "description":
                        "Company exposed to commodity price volatility",
                    "severity": 3
                }
            )


        return risks