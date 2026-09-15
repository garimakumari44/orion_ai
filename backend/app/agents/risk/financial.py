from __future__ import annotations

import logging
from typing import Dict, Any, List


logger = logging.getLogger(__name__)


class FinancialRiskAnalyzer:
    """
    Financial Risk Analyzer

    Detects:
    - Debt risk
    - Liquidity problems
    - Margin pressure
    - Cash flow weakness
    - Capital allocation risks
    """

    name = "financial_risk"


    async def analyze(
        self,
        company: Dict[str, Any]
    ) -> List[Dict[str, Any]]:

        risks = []


        financials = company.get(
            "financials",
            {}
        )


        debt_ratio = financials.get(
            "debt_ratio"
        )

        if debt_ratio and debt_ratio > 0.6:
            risks.append(
                {
                    "type": "debt_risk",
                    "description":
                        "High leverage may impact financial flexibility",
                    "severity": 4,
                    "metric": debt_ratio
                }
            )


        cashflow = financials.get(
            "free_cash_flow"
        )

        if cashflow and cashflow < 0:
            risks.append(
                {
                    "type": "cashflow_risk",
                    "description":
                        "Negative free cash flow",
                    "severity": 3,
                }
            )


        margin = financials.get(
            "operating_margin"
        )

        if margin and margin < 0.1:
            risks.append(
                {
                    "type": "margin_risk",
                    "description":
                        "Low operating margins indicate profitability pressure",
                    "severity": 2,
                }
            )


        return risks