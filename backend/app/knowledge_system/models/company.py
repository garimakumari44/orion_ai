from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CompanyIdentifier(BaseModel):
    """
    External identifiers for a company.

    Examples:
    - SEC CIK
    - ticker
    - ISIN
    - LEI
    """

    ticker: Optional[str] = None
    cik: Optional[str] = None
    isin: Optional[str] = None
    lei: Optional[str] = None


class CompanyProfile(BaseModel):
    """
    Core company information.
    """

    name: str

    legal_name: Optional[str] = None

    identifiers: CompanyIdentifier = Field(
        default_factory=CompanyIdentifier
    )

    exchange: Optional[str] = None

    country: Optional[str] = None

    industry: Optional[str] = None

    sector: Optional[str] = None

    description: Optional[str] = None

    website: Optional[str] = None


class ManagementMember(BaseModel):
    """
    Company leadership information.
    """

    name: str

    role: Optional[str] = None

    start_date: Optional[datetime] = None

    end_date: Optional[datetime] = None

    biography: Optional[str] = None


class CompanyFinancialSummary(BaseModel):
    """
    High-level financial snapshot.
    """

    market_cap: Optional[float] = None

    revenue: Optional[float] = None

    net_income: Optional[float] = None

    earnings_per_share: Optional[float] = None

    debt: Optional[float] = None

    cash: Optional[float] = None

    currency: Optional[str] = "USD"

    fiscal_year: Optional[int] = None


class CompanyEvent(BaseModel):
    """
    Important company events.

    Examples:
    - earnings release
    - acquisition
    - CEO change
    - guidance update
    """

    event_type: str

    title: str

    date: Optional[datetime] = None

    description: Optional[str] = None

    source: Optional[str] = None


class CompanyKnowledge(BaseModel):
    """
    Main company knowledge object stored
    inside the Knowledge System.

    Used by:
    - Knowledge Builder
    - Graph Builder
    - Retrieval System
    - Agents
    """

    company_id: str

    profile: CompanyProfile

    management: List[ManagementMember] = Field(
        default_factory=list
    )

    financials: Optional[CompanyFinancialSummary] = None

    events: List[CompanyEvent] = Field(
        default_factory=list
    )

    facts: Dict[str, Any] = Field(
        default_factory=dict
    )

    relationships: List[Dict[str, Any]] = Field(
        default_factory=list
    )

    sources: List[str] = Field(
        default_factory=list
    )

    confidence_score: float = 0.0

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )


    class Config:
        json_schema_extra = {
            "example": {
                "company_id": "AAPL",
                "profile": {
                    "name": "Apple Inc.",
                    "identifiers": {
                        "ticker": "AAPL",
                        "cik": "0000320193"
                    },
                    "industry": "Technology"
                },
                "financials": {
                    "market_cap": 3000000000000,
                    "currency": "USD"
                },
                "events": [
                    {
                        "event_type": "earnings",
                        "title": "Q4 Earnings Release"
                    }
                ]
            }
        }