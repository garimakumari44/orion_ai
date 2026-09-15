
"""
app/schemas/company.py

Company API schemas.

Canonical company identity fields:

    id
    name
    ticker
    exchange

Canonical classification fields:

    sector
    industry
    sub_industry

IMPORTANT
---------

sector != industry != sub_industry

The application must never silently use sector as industry.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CompanyBase(BaseModel):
    """
    Base schema shared across all company models.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    name: str = Field(
        ...,
        max_length=255,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=500,
    )

    ticker: str | None = Field(
        default=None,
        max_length=20,
    )

    exchange: str | None = None

    # ------------------------------------------------------------------
    # Financial identifiers
    # ------------------------------------------------------------------

    cik: str | None = None

    lei: str | None = None

    figi: str | None = None

    isin: str | None = None

    # ------------------------------------------------------------------
    # Company information
    # ------------------------------------------------------------------

    country: str | None = None

    # IMPORTANT:
    #
    # sector is a classification above industry.
    #
    sector: str | None = None

    # Canonical industry classification.
    industry: str | None = None

    # More granular classification.
    sub_industry: str | None = None

    currency: str | None = None

    website: HttpUrl | None = None

    logo_url: HttpUrl | None = None

    description: str | None = None

    # ------------------------------------------------------------------
    # Data quality
    # ------------------------------------------------------------------

    source: str | None = None

    primary_source: str | None = None

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    last_verified: datetime | None = None


class CompanyCreate(CompanyBase):
    """
    Schema used when creating a company.
    """

    pass


class CompanyUpdate(BaseModel):
    """
    Schema used when updating company information.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    name: str | None = None

    legal_name: str | None = None

    ticker: str | None = None

    exchange: str | None = None

    # ------------------------------------------------------------------
    # Financial identifiers
    # ------------------------------------------------------------------

    cik: str | None = None

    lei: str | None = None

    figi: str | None = None

    isin: str | None = None

    # ------------------------------------------------------------------
    # Company information
    # ------------------------------------------------------------------

    country: str | None = None

    sector: str | None = None

    industry: str | None = None

    sub_industry: str | None = None

    currency: str | None = None

    website: HttpUrl | None = None

    logo_url: HttpUrl | None = None

    description: str | None = None

    # ------------------------------------------------------------------
    # Data quality
    # ------------------------------------------------------------------

    source: str | None = None

    primary_source: str | None = None

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    last_verified: datetime | None = None


class CompanyResponse(CompanyBase):
    """
    Company returned by the API.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    created_at: datetime

    updated_at: datetime


class CompanySearchRequest(BaseModel):
    """
    Request for searching companies.
    """

    query: str = Field(
        ...,
        min_length=1,
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    offset: int = Field(
        default=0,
        ge=0,
    )


class CompanySearchResult(BaseModel):
    """
    Single company search result.

    Classification fields are included so the frontend
    can display and preserve canonical company metadata.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    name: str

    legal_name: str | None = None

    ticker: str | None = None

    exchange: str | None = None

    country: str | None = None

    sector: str | None = None

    industry: str | None = None

    sub_industry: str | None = None

    website: HttpUrl | None = None

    logo_url: HttpUrl | None = None

    primary_source: str | None = None

    confidence: float | None = None

    score: float = 0.0


class CompanySearchResponse(BaseModel):
    """
    Response returned from the search API.
    """

    query: str

    total: int

    limit: int

    offset: int

    results: list[CompanySearchResult]


class CompanySyncResponse(BaseModel):
    """
    Response returned after synchronization.
    """

    company: str

    status: Literal[
        "success",
        "failed",
    ]

    message: str

