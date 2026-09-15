from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class NewsItem:
    """
    Represents a company news item.
    """

    title: str

    source: Optional[str] = None

    published_at: Optional[datetime] = None

    category: Optional[str] = None

    sentiment: Optional[str] = None

    impact: Optional[str] = None

    summary: Optional[str] = None



@dataclass
class EarningsEvent:
    """
    Earnings announcement model.
    """

    company: str

    quarter: Optional[str] = None

    revenue_growth: Optional[float] = None

    eps_surprise: Optional[float] = None

    guidance_change: Optional[str] = None

    sentiment: Optional[str] = None



@dataclass
class CorporateEvent:
    """
    Corporate event model.
    """

    company: str

    event_type: str

    description: Optional[str] = None

    date: Optional[datetime] = None

    impact_level: str = "UNKNOWN"

    strategic_value: str = "UNKNOWN"



@dataclass
class NewsAnalysisResult:
    """
    Final output produced by News Agent.
    """

    company: str

    news_items: List[NewsItem] = field(
        default_factory=list
    )

    earnings_events: List[EarningsEvent] = field(
        default_factory=list
    )

    corporate_events: List[CorporateEvent] = field(
        default_factory=list
    )


    risk_score: float = 0.0

    sentiment: str = "NEUTRAL"

    summary: Optional[str] = None