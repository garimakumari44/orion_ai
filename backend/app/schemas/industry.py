"""
app/industry_catalog/schemas/industry.py

Pydantic schemas for canonical industry metadata.

These schemas describe the data flowing through the
Industry Catalog service/API.

They do not contain database logic or provider logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# ============================================================================
# Base
# ============================================================================


class IndustryBase(BaseModel):
    """
    Common industry metadata.

    Important:

        sector
        industry
        sub_industry

    are separate classification levels.

    Sector must never be silently used as industry.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    industry: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Canonical industry name.",
    )

    sub_industry: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Canonical sub-industry name.",
    )

    sector: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Higher-level sector classification.",
    )

    sic_code: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Standard Industrial Classification code.",
    )

    naics_code: Optional[str] = Field(
        default=None,
        max_length=20,
        description="North American Industry Classification System code.",
    )

    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Description of the industry.",
    )

    @field_validator(
        "sic_code",
        "naics_code",
        mode="before",
    )
    @classmethod
    def normalize_code(
        cls,
        value: Any,
    ) -> Optional[str]:

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        return value.upper()


# ============================================================================
# Create
# ============================================================================


class IndustryCreate(IndustryBase):
    """
    Schema used when creating a new industry catalog record.
    """

    canonical_key: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Stable canonical identifier for the industry.",
    )

    source: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Primary source of the classification.",
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Deterministic classification confidence.",
    )


# ============================================================================
# Update
# ============================================================================


class IndustryUpdate(BaseModel):
    """
    Schema used when updating an industry catalog record.

    All fields are optional.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    industry: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    sub_industry: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    sector: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    sic_code: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    naics_code: Optional[str] = Field(
        default=None,
        max_length=20,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


# ============================================================================
# Response
# ============================================================================


class IndustryResponse(IndustryBase):
    """
    Canonical industry returned by the Industry Catalog.
    """

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )

    id: int

    canonical_key: Optional[str] = None

    source: Optional[str] = None

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


# ============================================================================
# Search Result
# ============================================================================


class IndustrySearchResult(BaseModel):
    """
    Lightweight industry search result.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: Optional[int] = None

    industry: str

    sub_industry: Optional[str] = None

    sector: Optional[str] = None

    sic_code: Optional[str] = None

    naics_code: Optional[str] = None

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )


# ============================================================================
# Industry Resolution
# ============================================================================


class IndustryResolution(BaseModel):
    """
    Result produced by the industry processing pipeline.

    This is particularly useful when several providers
    disagree about classification.
    """

    industry: Optional[str] = None

    sub_industry: Optional[str] = None

    sector: Optional[str] = None

    sic_code: Optional[str] = None

    naics_code: Optional[str] = None

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    sources: List[str] = Field(
        default_factory=list,
    )

    validation_errors: List[str] = Field(
        default_factory=list,
    )

    provider_records: List[
        Dict[str, Any]
    ] = Field(
        default_factory=list,
    )

    resolved: bool = True