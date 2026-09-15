from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional



@dataclass
class FinancialMetrics:
    """
    Core financial metrics.
    """

    revenue: Optional[float] = None

    gross_profit: Optional[float] = None

    operating_income: Optional[float] = None

    net_income: Optional[float] = None

    free_cash_flow: Optional[float] = None

    total_assets: Optional[float] = None

    total_debt: Optional[float] = None

    equity: Optional[float] = None



@dataclass
class FinancialAnalysisResult:
    """
    Complete financial agent output.
    """

    company: str


    metrics: Dict[str, Any] = field(
        default_factory=dict
    )


    income_statement: Dict[str, Any] = field(
        default_factory=dict
    )


    balance_sheet: Dict[str, Any] = field(
        default_factory=dict
    )


    cashflow: Dict[str, Any] = field(
        default_factory=dict
    )


    ratios: Dict[str, Any] = field(
        default_factory=dict
    )


    growth: Dict[str, Any] = field(
        default_factory=dict
    )


    profitability: Dict[str, Any] = field(
        default_factory=dict
    )


    capital_allocation: Dict[str, Any] = field(
        default_factory=dict
    )



@dataclass
class FinancialInsight:
    """
    Single investment insight.
    """

    category: str

    statement: str

    importance: str = "medium"