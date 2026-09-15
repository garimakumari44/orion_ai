from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class MacroIndicator:
    """
    Represents a macroeconomic indicator.

    Examples:
    - Inflation rate
    - GDP growth
    - Interest rate
    - Employment data
    """

    name: str

    value: Optional[float] = None

    unit: Optional[str] = None

    region: Optional[str] = None

    period: Optional[str] = None

    source: Optional[str] = None

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )



@dataclass
class MacroRisk:
    """
    Represents a macroeconomic risk factor.
    """

    category: str

    description: str

    severity: str = "unknown"

    affected_sectors: List[str] = field(
        default_factory=list
    )

    affected_companies: List[str] = field(
        default_factory=list
    )



@dataclass
class MacroAnalysisResult:
    """
    Output model from Macro Agent.

    Passed to:
    - Valuation Agent
    - Risk Agent
    - Investment Committee Agent
    """

    region: Optional[str] = None

    inflation: Dict[str, Any] = field(
        default_factory=dict
    )

    interest_rates: Dict[str, Any] = field(
        default_factory=dict
    )

    gdp: Dict[str, Any] = field(
        default_factory=dict
    )

    employment: Dict[str, Any] = field(
        default_factory=dict
    )

    commodities: Dict[str, Any] = field(
        default_factory=dict
    )

    currencies: Dict[str, Any] = field(
        default_factory=dict
    )

    sentiment: Dict[str, Any] = field(
        default_factory=dict
    )

    risks: List[MacroRisk] = field(
        default_factory=list
    )

    indicators: List[MacroIndicator] = field(
        default_factory=list
    )

    generated_at: datetime = field(
        default_factory=datetime.utcnow
    )



@dataclass
class EconomicScenario:
    """
    Scenario model for macro forecasting.

    Used for:
    - Bull case
    - Base case
    - Bear case analysis
    """

    name: str

    probability: Optional[float] = None

    assumptions: Dict[str, Any] = field(
        default_factory=dict
    )

    sector_impacts: Dict[str, Any] = field(
        default_factory=dict
    )

    investment_implications: List[str] = field(
        default_factory=list
    )