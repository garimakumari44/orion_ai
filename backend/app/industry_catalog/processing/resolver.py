"""
app/industry_catalog/processing/resolver.py

Industry classification resolver.

Combines normalized provider records into one canonical
industry classification.

This component is deterministic.

It does not:
- perform web research
- call an LLM
- perform market research
- infer trends
- write to the database
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Optional


class IndustryResolver:
    """
    Resolve canonical industry metadata from provider records.

    Resolution priority:

        1. Explicit canonical classification
        2. SIC / NAICS-backed classification
        3. Provider priority
        4. Frequency / consensus
        5. First valid value

    Important:
        A canonical industry supplied by the normalized top-level
        payload must not be lost merely because provider_records
        are incomplete.

    The resolver accepts either:

        dict
            Single normalized provider record.

        list[dict]
            Multiple provider records.

    Provider priority can be configured.
    """

    DEFAULT_PROVIDER_PRIORITY = [
        "sec",
        "naics",
        "sic",
        "companies_house",
        "openfigi",
        "yahoo",
        "polygon",
        "alphavantage",
    ]

    def __init__(
        self,
        provider_priority: Optional[Iterable[str]] = None,
    ) -> None:

        self.provider_priority = [
            str(provider).strip().lower()
            for provider in (
                provider_priority
                or self.DEFAULT_PROVIDER_PRIORITY
            )
            if provider
        ]

    # ==================================================================
    # PUBLIC API
    # ==================================================================

    def resolve(
        self,
        records: Dict[str, Any]
        | List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Resolve canonical industry metadata.

        Supports both a single normalized dictionary and
        a list of provider records.
        """

        # --------------------------------------------------------------
        # Preserve top-level canonical metadata before normalizing.
        # --------------------------------------------------------------

        top_level_metadata: Dict[str, Any] = {}

        if isinstance(records, dict):
            top_level_metadata = dict(records)

        # --------------------------------------------------------------
        # Normalize input into provider records.
        # --------------------------------------------------------------

        normalized_records = self._normalize_records(
            records
        )

        if not normalized_records:
            return {}

        # --------------------------------------------------------------
        # Resolve fields.
        # --------------------------------------------------------------

        industry = self._resolve_industry(
            normalized_records,
            top_level_metadata=top_level_metadata,
        )

        sub_industry = self._resolve_field(
            normalized_records,
            field="sub_industry",
        )

        sector = self._resolve_field(
            normalized_records,
            field="sector",
        )

        sic_code = self._resolve_code(
            normalized_records,
            "sic_code",
        )

        naics_code = self._resolve_code(
            normalized_records,
            "naics_code",
        )

        # --------------------------------------------------------------
        # Start with the first normalized record.
        # --------------------------------------------------------------

        resolved: Dict[str, Any] = dict(
            normalized_records[0]
        )

        # --------------------------------------------------------------
        # Preserve important top-level metadata.
        #
        # The normalized payload may contain information that is not
        # present inside provider_records.
        # --------------------------------------------------------------

        for key in (
            "company",
            "ticker",
            "provider",
            "source",
            "company_id",
            "industry",
            "industry_name",
            "canonical_industry",
            "classification",
            "classification_name",
            "industry_code",
            "classification_code",
            "gics_code",
            "naics_code",
            "sic_code",
        ):

            value = top_level_metadata.get(key)

            if value is not None:
                resolved[key] = value

        # --------------------------------------------------------------
        # Set resolved canonical industry.
        # --------------------------------------------------------------

        if industry:
            resolved["industry"] = industry

        if sub_industry:
            resolved["sub_industry"] = sub_industry

        if sector:
            resolved["sector"] = sector

        if sic_code:
            resolved["sic_code"] = sic_code

        if naics_code:
            resolved["naics_code"] = naics_code

        # --------------------------------------------------------------
        # Collect sources.
        # --------------------------------------------------------------

        resolved["sources"] = self._collect_sources(
            normalized_records
        )

        # --------------------------------------------------------------
        # Preserve the actual provider records.
        # --------------------------------------------------------------

        resolved["provider_records"] = (
            normalized_records
        )

        return resolved

    # ==================================================================
    # INPUT NORMALIZATION
    # ==================================================================

    @classmethod
    def _normalize_records(
        cls,
        records: Dict[str, Any]
        | List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Convert resolver input into a list of dictionaries.

        If the top-level payload contains a canonical industry
        but provider_records do not, the canonical industry is
        copied into the first valid provider record.

        This prevents:

            payload["industry"]
                    ↓
            provider_records
                    ↓
            IndustryResolver
                    ↓
            industry = None
        """

        # --------------------------------------------------------------
        # Dictionary input.
        # --------------------------------------------------------------

        if isinstance(records, dict):

            provider_records = records.get(
                "provider_records"
            )

            # ----------------------------------------------------------
            # Existing provider records.
            # ----------------------------------------------------------

            if isinstance(provider_records, list):

                valid_records = [
                    dict(record)
                    for record in provider_records
                    if isinstance(record, dict)
                    and record
                ]

                if valid_records:

                    # --------------------------------------------------
                    # Extract top-level canonical industry.
                    # --------------------------------------------------

                    top_level_industry = (
                        cls._extract_industry(
                            records
                        )
                    )

                    # --------------------------------------------------
                    # If provider records contain no industry but the
                    # normalized payload does, preserve it.
                    # --------------------------------------------------

                    if top_level_industry:

                        has_provider_industry = any(
                            cls._extract_industry(
                                record
                            )
                            for record in valid_records
                        )

                        if not has_provider_industry:

                            valid_records[0][
                                "industry"
                            ] = top_level_industry

                    # --------------------------------------------------
                    # Preserve top-level classification codes.
                    # --------------------------------------------------

                    for key in (
                        "sic_code",
                        "naics_code",
                        "gics_code",
                        "industry_code",
                        "classification_code",
                    ):

                        value = records.get(key)

                        if (
                            value is not None
                            and not valid_records[0].get(key)
                        ):
                            valid_records[0][key] = value

                    # --------------------------------------------------
                    # Preserve identity metadata.
                    # --------------------------------------------------

                    for key in (
                        "provider",
                        "source",
                        "company",
                        "ticker",
                        "company_id",
                    ):

                        value = records.get(key)

                        if (
                            value is not None
                            and not valid_records[0].get(key)
                        ):
                            valid_records[0][key] = value

                    return valid_records

            # ----------------------------------------------------------
            # No provider_records.
            #
            # Treat the dictionary itself as one provider record.
            # ----------------------------------------------------------

            return [dict(records)]

        # --------------------------------------------------------------
        # List input.
        # --------------------------------------------------------------

        if isinstance(records, list):

            return [
                dict(record)
                for record in records
                if isinstance(record, dict)
                and record
            ]

        raise TypeError(
            "IndustryResolver.resolve() requires "
            "a dict or list[dict]."
        )

    # ==================================================================
    # INDUSTRY RESOLUTION
    # ==================================================================

    @classmethod
    def _resolve_industry(
        cls,
        records: List[Dict[str, Any]],
        *,
        top_level_metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Optional[str]:
        """
        Resolve the canonical industry.

        Priority:

            1. Explicit top-level canonical classification
            2. Explicit canonical classification in records
            3. SIC / NAICS-backed provider records
            4. Provider priority
            5. Consensus
            6. First valid value
        """

        top_level_metadata = (
            top_level_metadata or {}
        )

        # --------------------------------------------------------------
        # 1. Explicit top-level canonical classification.
        # --------------------------------------------------------------

        top_level_industry = cls._extract_industry(
            top_level_metadata
        )

        if top_level_industry:
            return top_level_industry

        # --------------------------------------------------------------
        # 2. Explicit canonical classification.
        # --------------------------------------------------------------

        explicit_keys = (
            "canonical_industry",
            "classification_name",
            "classification",
        )

        for record in records:

            for key in explicit_keys:

                value = cls._clean(
                    record.get(key)
                )

                if value:
                    return value

        # --------------------------------------------------------------
        # 3. SIC / NAICS-backed classification.
        #
        # Only use this when the record has an industry AND a
        # corresponding classification code.
        # --------------------------------------------------------------

        for record in records:

            industry = cls._clean(
                record.get("industry")
            )

            if not industry:
                continue

            sic_code = cls._clean(
                record.get("sic_code")
            )

            naics_code = cls._clean(
                record.get("naics_code")
            )

            provider = str(
                record.get("provider")
                or ""
            ).lower()

            if (
                sic_code
                or naics_code
                or provider in {
                    "sic",
                    "naics",
                    "sec",
                }
            ):
                return industry

        # --------------------------------------------------------------
        # 4. Provider priority.
        # --------------------------------------------------------------

        candidates = cls._industry_candidates(
            records
        )

        # --------------------------------------------------------------
        # Determine available providers using the class default
        # priority. This preserves the existing classmethod design.
        # --------------------------------------------------------------

        available_providers = {
            candidate["provider"]
            for candidate in candidates
            if candidate["provider"]
        }

        for provider in cls.DEFAULT_PROVIDER_PRIORITY:

            if provider not in available_providers:
                continue

            for candidate in candidates:

                if candidate["provider"] == provider:
                    return candidate["value"]

        # --------------------------------------------------------------
        # 5. Consensus.
        # --------------------------------------------------------------

        if candidates:

            counts = Counter(
                candidate["value"].lower()
                for candidate in candidates
            )

            most_common = counts.most_common(1)

            if most_common:

                normalized_value = (
                    most_common[0][0]
                )

                for candidate in candidates:

                    if (
                        candidate["value"].lower()
                        == normalized_value
                    ):
                        return candidate["value"]

        # --------------------------------------------------------------
        # 6. First valid value.
        # --------------------------------------------------------------

        if candidates:
            return candidates[0]["value"]

        return None

    # ==================================================================
    # FIELD RESOLUTION
    # ==================================================================

    def _resolve_field(
        self,
        records: List[Dict[str, Any]],
        field: str,
    ) -> Optional[str]:
        """
        Resolve a normal metadata field.
        """

        candidates = []

        for record in records:

            value = record.get(field)

            if not value:
                continue

            value = str(value).strip()

            if not value:
                continue

            provider = str(
                record.get("provider")
                or ""
            ).lower()

            candidates.append(
                {
                    "value": value,
                    "provider": provider,
                }
            )

        if not candidates:
            return None

        # --------------------------------------------------------------
        # Provider priority.
        # --------------------------------------------------------------

        for provider in self.provider_priority:

            for candidate in candidates:

                if candidate["provider"] == provider:
                    return candidate["value"]

        # --------------------------------------------------------------
        # Consensus.
        # --------------------------------------------------------------

        counts = Counter(
            candidate["value"].lower()
            for candidate in candidates
        )

        most_common = counts.most_common(1)

        if most_common:

            normalized_value = (
                most_common[0][0]
            )

            for candidate in candidates:

                if (
                    candidate["value"].lower()
                    == normalized_value
                ):
                    return candidate["value"]

        return candidates[0]["value"]

    # ==================================================================
    # CODE RESOLUTION
    # ==================================================================

    def _resolve_code(
        self,
        records: List[Dict[str, Any]],
        field: str,
    ) -> Optional[str]:
        """
        Resolve SIC / NAICS codes.
        """

        candidates = []

        for record in records:

            value = record.get(field)

            if value is None:
                continue

            value = str(value).strip()

            if not value:
                continue

            provider = str(
                record.get("provider")
                or ""
            ).lower()

            candidates.append(
                {
                    "value": value,
                    "provider": provider,
                }
            )

        if not candidates:
            return None

        # --------------------------------------------------------------
        # Provider priority.
        # --------------------------------------------------------------

        for provider in self.provider_priority:

            for candidate in candidates:

                if candidate["provider"] == provider:
                    return candidate["value"]

        # --------------------------------------------------------------
        # Consensus.
        # --------------------------------------------------------------

        counts = Counter(
            candidate["value"]
            for candidate in candidates
        )

        return counts.most_common(1)[0][0]

    # ==================================================================
    # INDUSTRY CANDIDATES
    # ==================================================================

    @staticmethod
    def _industry_candidates(
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """
        Extract usable industry candidates.
        """

        candidates = []

        for record in records:

            value = IndustryResolver._clean(
                record.get("industry")
            )

            if not value:
                continue

            provider = str(
                record.get("provider")
                or ""
            ).strip().lower()

            candidates.append(
                {
                    "value": value,
                    "provider": provider,
                }
            )

        return candidates

    # ==================================================================
    # PROVIDER PRIORITY
    # ==================================================================

    def _provider_priority_from_records(
        self,
        records: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Return configured provider priority while preserving
        the configured ordering.
        """

        available_providers = {
            str(
                record.get("provider")
                or ""
            ).strip().lower()
            for record in records
            if record.get("provider")
        }

        return [
            provider
            for provider in self.provider_priority
            if provider in available_providers
        ]

    # ==================================================================
    # SOURCE COLLECTION
    # ==================================================================

    @staticmethod
    def _collect_sources(
        records: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Collect unique provider/source names.
        """

        sources: List[str] = []

        for record in records:

            source = (
                record.get("source")
                or record.get("provider")
            )

            if source:

                source = str(source).strip()

                if (
                    source
                    and source not in sources
                ):
                    sources.append(source)

        return sources

    # ==================================================================
    # HELPERS
    # ==================================================================

    @staticmethod
    def _extract_industry(
        record: Dict[str, Any],
    ) -> Optional[str]:
        """
        Extract an industry value from a record.

        Supports the different industry/classification field names
        that may be produced by providers or the normalized payload.

        Priority:

            1. canonical_industry
            2. industry
            3. industry_name
            4. classification_name
            5. classification
        """

        if not isinstance(record, dict):
            return None

        for key in (
            "canonical_industry",
            "industry",
            "industry_name",
            "classification_name",
            "classification",
        ):

            value = IndustryResolver._clean(
                record.get(key)
            )

            if value:
                return value

        return None

    @staticmethod
    def _clean(
        value: Any,
    ) -> Optional[str]:
        """
        Normalize a value into a clean string.
        """

        if value is None:
            return None

        if isinstance(value, str):

            value = value.strip()

        else:

            value = str(value).strip()

        return value or None