from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class PorterAnalysisResult:
    """
    Result of Porter's Five Forces analysis.
    """

    industry: str

    supplier_power: str

    buyer_power: str

    competitive_rivalry: str

    threat_of_substitutes: str

    threat_of_new_entrants: str

    summary: Optional[str] = None


@dataclass
class MarketSizeResult:
    """
    Represents industry market sizing.
    """

    industry: str

    tam: Optional[str] = None

    sam: Optional[str] = None

    som: Optional[str] = None

    growth_rate: Optional[str] = None

    forecast: Optional[str] = None


@dataclass
class CompetitorProfile:
    """
    Represents a company competitor.
    """

    name: str

    market_position: Optional[str] = None

    strengths: List[str] = field(default_factory=list)

    weaknesses: List[str] = field(default_factory=list)

    market_share: Optional[str] = None


@dataclass
class IndustryTrend:
    """
    Represents an industry trend.
    """

    name: str

    impact: str

    description: Optional[str] = None


@dataclass
class IndustryReport:
    """
    Complete industry research output.
    """

    industry: str

    porter_analysis: Optional[PorterAnalysisResult] = None

    market_size: Optional[MarketSizeResult] = None

    competitors: List[CompetitorProfile] = field(default_factory=list)

    trends: List[IndustryTrend] = field(default_factory=list)

    supply_chain: Optional[Dict] = None