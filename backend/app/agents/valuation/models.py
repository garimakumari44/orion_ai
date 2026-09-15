from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValuationInput:
    """
    Input data required for valuation analysis.
    """

    company_name: str

    ticker: Optional[str] = None

    revenue: Optional[float] = None
    earnings: Optional[float] = None
    free_cash_flow: Optional[float] = None

    shares_outstanding: Optional[float] = None
    current_price: Optional[float] = None

    growth_rate: Optional[float] = None
    discount_rate: Optional[float] = None

    financial_data: Dict = field(default_factory=dict)


@dataclass
class DCFResult:
    """
    Discounted Cash Flow valuation output.
    """

    enterprise_value: float

    equity_value: float

    fair_value_per_share: Optional[float]

    assumptions: Dict = field(default_factory=dict)


@dataclass
class ComparableCompany:
    """
    Peer company valuation data.
    """

    name: str

    ticker: str

    market_cap: float

    revenue: float

    earnings: float

    ev_revenue: Optional[float] = None

    ev_ebitda: Optional[float] = None

    pe_ratio: Optional[float] = None


@dataclass
class ValuationReport:
    """
    Complete valuation agent output.
    """

    company: str

    dcf: Optional[DCFResult] = None

    comparable_analysis: Dict = field(default_factory=dict)

    multiples_analysis: Dict = field(default_factory=dict)

    sensitivity_analysis: Dict = field(default_factory=dict)

    conclusion: Optional[str] = None