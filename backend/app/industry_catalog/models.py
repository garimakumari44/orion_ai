
"""
app/industry_catalog/models.py

Industry Catalog domain/application models.

Responsibilities
----------------
- Define the result contract returned by industry resolution.
- Keep resolver/application contracts separate from SQLAlchemy ORM models.
- Avoid coupling IndustryResolver to database-specific result structures.

Architecture
------------

    Company / Research
            |
            v
    IndustryCatalogManager
            |
            v
      IndustryResolver
            |
            v
      IndustryResult
            |
            +--> Industry ORM model
            +--> resolution metadata
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class IndustryResult:
    """
    Result of canonical industry resolution.

    Attributes
    ----------
    industry:
        Resolved canonical Industry ORM/domain object.

        This is intentionally typed as Any here to avoid creating
        a hard dependency from the catalog result contract onto
        the SQLAlchemy model layer.

    source:
        Source from which the industry was resolved.

        Examples:
            - "company_record"
            - "company.industry"
            - "company.sub_industry"
            - "research.industry"
            - "explicit_industry"
            - "provider"

    confidence:
        Resolution confidence in the range 0.0 - 1.0.

    matched_by:
        Field or strategy that produced the resolution.

        Examples:
            - "company_id"
            - "company.industry"
            - "company.sub_industry"
            - "ticker"
            - "industry_name"

    company_id:
        Canonical company ID associated with the resolution.

    company:
        Company name associated with the resolution.

    ticker:
        Company ticker associated with the resolution.

    metadata:
        Additional resolution information.
    """

    industry: Any | None = None
    source: str | None = None
    confidence: float | None = None
    matched_by: str | None = None

    company_id: int | None = None
    company: str | None = None
    ticker: str | None = None

    metadata: dict[str, Any] | None = None

    @property
    def resolved(self) -> bool:
        """
        Return True when a canonical industry was resolved.
        """
        return self.industry is not None

    @property
    def industry_id(self) -> int | None:
        """
        Return the canonical industry ID when available.
        """
        if self.industry is None:
            return None

        return getattr(self.industry, "id", None)

    @property
    def industry_name(self) -> str | None:
        """
        Return the canonical industry name when available.
        """
        if self.industry is None:
            return None

        return getattr(self.industry, "name", None)

    def require_industry(self) -> Any:
        """
        Return the resolved industry or raise an error.

        Useful for execution paths where a canonical industry
        is mandatory.
        """
        if self.industry is None:
            raise ValueError(
                "Canonical industry could not be resolved."
            )

        return self.industry
