"""
app/industry_catalog/schemas/provider.py

Pydantic schemas for Industry Catalog providers.

Provider-specific implementations should normalize their
responses into ProviderIndustryRecord before handing them
to the processing pipeline.
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
# Provider Industry Record
# ============================================================================


class ProviderIndustryRecord(BaseModel):
    """
    Canonical representation of one provider's industry data.

    Example:

        {
            "provider": "sec",
            "provider_id": "3571",
            "industry": "Electronic Computers",
            "sic_code": "3571"
        }
    """

    model_config = ConfigDict(
        extra="allow",
        str_strip_whitespace=True,
    )

    provider: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Provider identifier.",
    )

    provider_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Provider-specific classification ID.",
    )

    name: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    industry: Optional[str] = Field(
        default=None,
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

    source: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    retrieved_at: Optional[datetime] = None

    raw: Dict[str, Any] = Field(
        default_factory=dict,
        description="Original provider payload.",
    )

    @field_validator(
        "provider",
        mode="before",
    )
    @classmethod
    def normalize_provider(
        cls,
        value: Any,
    ) -> str:

        if value is None:
            raise ValueError(
                "provider is required"
            )

        value = str(value).strip().lower()

        if not value:
            raise ValueError(
                "provider cannot be empty"
            )

        return value

    @field_validator(
        "sic_code",
        "naics_code",
        mode="before",
    )
    @classmethod
    def normalize_codes(
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
# Provider Search Request
# ============================================================================


class ProviderSearchRequest(BaseModel):
    """
    Request sent to a provider when searching for
    industry classifications.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    query: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    industry: Optional[str] = Field(
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

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    offset: int = Field(
        default=0,
        ge=0,
    )


# ============================================================================
# Provider Search Response
# ============================================================================


class ProviderSearchResponse(BaseModel):
    """
    Standardized response from an industry provider.
    """

    provider: str

    records: List[
        ProviderIndustryRecord
    ] = Field(
        default_factory=list,
    )

    total: Optional[int] = None

    has_more: bool = False

    query: Optional[str] = None


# ============================================================================
# Provider Health
# ============================================================================


class ProviderHealthResponse(BaseModel):
    """
    Provider health-check result.
    """

    provider: str

    healthy: bool

    latency_ms: Optional[float] = Field(
        default=None,
        ge=0,
    )

    message: Optional[str] = None

    checked_at: Optional[datetime] = None

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
    )