"""
app/industry_catalog/processing/normalizer.py

Industry data normalization.

Converts provider-specific industry records into a
consistent internal representation.

The normalizer does NOT:
- resolve conflicts
- calculate confidence
- access the database
- perform research
- call an LLM

It only cleans and standardizes data.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional


class IndustryNormalizer:
    """
    Normalize raw provider industry data.

    Provider records may use different field names:

        industry
        industry_name
        sector
        sub_industry
        sic
        sic_code
        naics
        naics_code

    This class maps them into a canonical dictionary.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def normalize(
        self,
        data: Dict[str, Any] | None,
    ) -> Dict[str, Any]:
        """
        Normalize one raw provider record.

        Returns a canonical dictionary.
        """

        if not data:
            return {}

        normalized: Dict[str, Any] = {}

        normalized["provider"] = self._normalize_string(
            data.get("provider")
        )

        normalized["provider_id"] = self._normalize_string(
            data.get("provider_id")
        )

        normalized["name"] = self._normalize_name(
            data.get("name")
            or data.get("industry_name")
            or data.get("industry")
        )

        normalized["industry"] = self._normalize_name(
            data.get("industry")
            or data.get("industry_name")
            or data.get("name")
        )

        normalized["sub_industry"] = self._normalize_name(
            data.get("sub_industry")
            or data.get("subindustry")
            or data.get("sub_industry_name")
        )

        normalized["sector"] = self._normalize_name(
            data.get("sector")
        )

        normalized["sic_code"] = self._normalize_code(
            data.get("sic_code")
            or data.get("sic")
        )

        normalized["naics_code"] = self._normalize_code(
            data.get("naics_code")
            or data.get("naics")
        )

        normalized["description"] = self._normalize_description(
            data.get("description")
        )

        normalized["source"] = self._normalize_string(
            data.get("source")
            or data.get("provider")
        )

        # Preserve original provider payload.
        normalized["raw"] = data

        return normalized

    # ------------------------------------------------------------------
    # String normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_string(
        value: Any,
    ) -> Optional[str]:

        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        return value

    # ------------------------------------------------------------------
    # Name normalization
    # ------------------------------------------------------------------

    @classmethod
    def _normalize_name(
        cls,
        value: Any,
    ) -> Optional[str]:

        value = cls._normalize_string(value)

        if value is None:
            return None

        # Normalize whitespace.
        value = re.sub(r"\s+", " ", value)

        # Remove accidental leading/trailing punctuation.
        value = value.strip(" ,;|")

        if not value:
            return None

        return value

    # ------------------------------------------------------------------
    # Code normalization
    # ------------------------------------------------------------------

    @classmethod
    def _normalize_code(
        cls,
        value: Any,
    ) -> Optional[str]:

        value = cls._normalize_string(value)

        if value is None:
            return None

        # Codes should normally contain only alphanumeric characters.
        value = re.sub(r"[^A-Za-z0-9]", "", value)

        if not value:
            return None

        return value.upper()

    # ------------------------------------------------------------------
    # Description normalization
    # ------------------------------------------------------------------

    @classmethod
    def _normalize_description(
        cls,
        value: Any,
    ) -> Optional[str]:

        value = cls._normalize_string(value)

        if value is None:
            return None

        value = re.sub(r"\s+", " ", value)

        return value