from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class FinancialPeriod(BaseModel):
    """
    Represents the reporting period of a financial fact.

    Examples:
    - FY2025
    - Q1 2026
    - TTM
    """

    fiscal_year: Optional[int] = None

    fiscal_quarter: Optional[int] = None

    period_type: Optional[str] = None
    # annual, quarterly, trailing_twelve_months

    start_date: Optional[datetime] = None

    end_date: Optional[datetime] = None


class FinancialValue(BaseModel):
    """
    Numeric value container.

    Keeps value metadata because financial
    numbers require units and currency.
    """

    value: Optional[float] = None

    currency: str = "USD"

    unit: Optional[str] = None
    # dollars, shares, percentage


class FinancialFact(BaseModel):
    """
    Atomic financial knowledge object.

    Example:

    Company:
        Apple Inc.

    Metric:
        Revenue

    Value:
        394.3 Billion USD

    Period:
        FY2025

    Source:
        SEC 10-K
    """

    fact_id: str

    company_id: str


    # XBRL / accounting concept
    concept: str
    # Example:
    # Revenue
    # NetIncomeLoss
    # Assets
    # CashAndCashEquivalentsAtCarryingValue


    label: Optional[str] = None


    category: Optional[str] = None
    # revenue
    # expense
    # asset
    # liability
    # equity
    # ratio


    value: FinancialValue


    period: FinancialPeriod


    filing_type: Optional[str] = None
    # 10-K
    # 10-Q
    # 8-K


    source_document: Optional[str] = None


    source_url: Optional[str] = None


    extraction_method: Optional[str] = None
    # xbrl
    # parser
    # llm_extraction


    confidence_score: float = 0.0


    verified: bool = False


    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )


    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )


    class Config:
        json_schema_extra = {

            "example": {

                "fact_id": "AAPL_REVENUE_FY2025",

                "company_id": "AAPL",

                "concept": "Revenue",

                "label": "Total Net Sales",

                "category": "revenue",

                "value": {
                    "value": 394300000000,
                    "currency": "USD",
                    "unit": "dollars"
                },

                "period": {
                    "fiscal_year": 2025,
                    "period_type": "annual"
                },

                "filing_type": "10-K",

                "extraction_method": "xbrl",

                "confidence_score": 0.98,

                "verified": True
            }
        }