"""
app/industry_catalog/processing/pipeline.py

Industry metadata processing pipeline.

Responsibilities
----------------
Transforms acquired industry/provider data into:

    normalized
        ↓
    validated
        ↓
    resolved
        ↓
    confidence-scored
        ↓
    canonical industry metadata

Architecture
------------

IndustryCatalogService
        |
        +--> IndustryProviderManager
        |       |
        |       +--> provider acquisition
        |
        +--> IndustryProcessingPipeline
                |
                +--> Normalize
                +--> Validate
                +--> Resolve
                +--> Confidence

Important
---------
This pipeline does NOT persist data.

Provider acquisition is intentionally separated:

    process()
        -> processes already-acquired data

    enrich()
        -> acquires provider data
        -> verifies a classification exists
        -> processes acquired data

Canonical provider API:

    search_industry()
    get_industry()
    classify_company()

Industry invariant
------------------
Sector is NEVER promoted to industry.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


from app.industry_catalog.processing.confidence import (
    IndustryConfidenceCalculator,
)
from app.industry_catalog.processing.normalizer import (
    IndustryNormalizer,
)
from app.industry_catalog.processing.resolver import (
    IndustryResolver,
)
from app.industry_catalog.processing.validator import (
    IndustryValidator,
)


@dataclass
class IndustryProcessingPipeline:
    """
    Processing pipeline for industry metadata.

    Flow:

        Provider data
            ↓
        Normalize
            ↓
        Validate
            ↓
        Resolve
            ↓
        Confidence
            ↓
        Structured industry metadata
    """

    provider_manager: Any | None = None
    normalizer: IndustryNormalizer | None = None
    validator: IndustryValidator | None = None
    resolver: IndustryResolver | None = None
    confidence: IndustryConfidenceCalculator | None = None

    def __post_init__(self) -> None:
        """
        Initialize default processing components.
        """

        if self.normalizer is None:
            self.normalizer = IndustryNormalizer()

        if self.validator is None:
            self.validator = IndustryValidator()

        if self.resolver is None:
            self.resolver = IndustryResolver()

        if self.confidence is None:
            self.confidence = IndustryConfidenceCalculator()

    # ==================================================================
    # PROCESS
    # ==================================================================

    async def process(
        self,
        data: Mapping[str, Any] | None = None,
        *,
        company: str | None = None,
        ticker: str | None = None,
        industry: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Process already-acquired industry metadata.

        This method does NOT perform provider acquisition.

        Parameters
        ----------
        data:
            Already acquired provider/manual metadata.

        company:
            Optional company name.

        ticker:
            Optional ticker symbol.

        industry:
            Optional explicit industry classification.

        kwargs:
            Additional metadata.

        Returns
        -------
        dict[str, Any]
            Canonical processed industry metadata.
        """

        payload: dict[str, Any] = dict(data or {})

        # --------------------------------------------------------------
        # Merge explicit arguments.
        # --------------------------------------------------------------

        if company is not None:
            payload.setdefault("company", company)

        if ticker is not None:
            payload.setdefault("ticker", ticker)

        if industry is not None:
            payload.setdefault("industry", industry)

        if kwargs:
            payload.update(kwargs)

        # --------------------------------------------------------------
        # Preserve provider source records.
        # --------------------------------------------------------------

        source_records = self._extract_source_records(payload)

        if not source_records:
            source_records = [dict(payload)]

        # --------------------------------------------------------------
        # HARD INDUSTRY INVARIANT
        #
        # Industry must exist before normalization.
        # Sector alone is never sufficient.
        # --------------------------------------------------------------

        canonical_industry = self._extract_industry(payload)

        if not canonical_industry:
            canonical_industry = self._extract_industry_from_records(
                source_records
            )

        if not canonical_industry:
            raise ValueError(
                "IndustryProcessingPipeline.process() requires "
                "a canonical industry classification. "
                f"company={payload.get('company')!r} "
                f"ticker={payload.get('ticker')!r}"
            )

        payload["industry"] = canonical_industry

        # --------------------------------------------------------------
        # 1. NORMALIZE
        # --------------------------------------------------------------

        assert self.normalizer is not None

        normalized_result = self.normalizer.normalize(payload)

        if inspect.isawaitable(normalized_result):
            normalized_result = await normalized_result

        if normalized_result is None:
            normalized_result = {}

        if not isinstance(normalized_result, dict):
            raise TypeError(
                "IndustryNormalizer.normalize() "
                "must return a dict or None."
            )

        normalized = normalized_result

        # --------------------------------------------------------------
        # Ensure industry survived normalization.
        # --------------------------------------------------------------

        normalized_industry = self._extract_industry(normalized)

        if not normalized_industry:
            normalized_industry = self._extract_industry_from_records(
                source_records
            )

        if not normalized_industry:
            raise ValueError(
                "IndustryNormalizer removed or failed "
                "to preserve the canonical industry "
                "classification. "
                f"company={normalized.get('company')!r} "
                f"ticker={normalized.get('ticker')!r}"
            )

        normalized["industry"] = normalized_industry

        # --------------------------------------------------------------
        # Preserve source records after normalization.
        # --------------------------------------------------------------

        normalized["provider_records"] = self._copy_records(
            source_records
        )

        # --------------------------------------------------------------
        # Preserve original provider/source information.
        # --------------------------------------------------------------

        self._preserve_metadata(
            source=payload,
            target=normalized,
            keys=(
                "provider",
                "source",
                "source_name",
                "provider_name",
            ),
        )

        # --------------------------------------------------------------
        # 2. VALIDATE
        # --------------------------------------------------------------

        assert self.validator is not None

        validation_result = self.validator.validate(normalized)

        if inspect.isawaitable(validation_result):
            validation_result = await validation_result

        if isinstance(validation_result, bool):

            if not validation_result:
                raise ValueError(
                    "Industry metadata validation failed."
                )

            normalized["validation"] = {
                "valid": True,
            }

        elif isinstance(validation_result, dict):

            normalized["validation"] = validation_result

        elif validation_result is not None:

            normalized["validation"] = validation_result

        # --------------------------------------------------------------
        # 3. RESOLVE
        # --------------------------------------------------------------

        assert self.resolver is not None

        resolved_result = self.resolver.resolve(normalized)

        if inspect.isawaitable(resolved_result):
            resolved_result = await resolved_result

        if resolved_result is None:
            resolved_result = normalized

        if not isinstance(resolved_result, dict):
            raise TypeError(
                "IndustryResolver.resolve() "
                "must return a dict or None."
            )

        resolved = resolved_result

        # --------------------------------------------------------------
        # Preserve important metadata from normalized payload.
        # --------------------------------------------------------------

        self._preserve_metadata(
            source=normalized,
            target=resolved,
            keys=(
                "company",
                "ticker",
                "provider",
                "source",
                "source_name",
                "provider_name",
                "validation",
            ),
        )

        # --------------------------------------------------------------
        # Always preserve provider records.
        # --------------------------------------------------------------

        resolved_records = self._extract_source_records(
            resolved
        )

        if not resolved_records:
            resolved["provider_records"] = self._copy_records(
                source_records
            )
        else:
            resolved["provider_records"] = resolved_records

        # --------------------------------------------------------------
        # Resolver must preserve industry.
        # --------------------------------------------------------------

        resolved_industry = self._extract_industry(resolved)

        if not resolved_industry:
            resolved_industry = self._extract_industry(normalized)

        if not resolved_industry:
            resolved_industry = self._extract_industry_from_records(
                source_records
            )

        if not resolved_industry:
            raise ValueError(
                "IndustryResolver returned metadata "
                "without a canonical industry classification."
            )

        resolved["industry"] = resolved_industry

        # --------------------------------------------------------------
        # Resolver becomes the canonical metadata.
        # --------------------------------------------------------------

        normalized = resolved

        # --------------------------------------------------------------
        # 4. CONFIDENCE
        # --------------------------------------------------------------

        assert self.confidence is not None

        confidence_result = self.confidence.calculate(
            normalized,
            source_records,
        )

        if inspect.isawaitable(confidence_result):
            confidence_result = await confidence_result

        if confidence_result is not None:
            normalized["confidence"] = confidence_result

        # --------------------------------------------------------------
        # Final invariant check.
        # --------------------------------------------------------------

        final_industry = self._extract_industry(normalized)

        if not final_industry:
            raise ValueError(
                "IndustryProcessingPipeline produced "
                "metadata without a canonical industry."
            )

        normalized["industry"] = final_industry

        return normalized

    # ==================================================================
    # PROCESS MANY
    # ==================================================================

    async def process_many(
        self,
        records: Iterable[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Process multiple already-acquired industry records.

        Invalid/non-dictionary records are skipped.
        Processing errors are intentionally propagated.
        """

        results: list[dict[str, Any]] = []

        for record in records:

            if not isinstance(record, Mapping):
                continue

            results.append(
                await self.process(record)
            )

        return results

    # ==================================================================
    # ENRICH
    # ==================================================================

    async def enrich(
        self,
        *,
        company: str | None = None,
        ticker: str | None = None,
        industry: str | None = None,
        limit: int = 20,
        providers: list[str]
        | tuple[str, ...]
        | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Acquire and process industry metadata.

        Acquisition is delegated entirely to
        IndustryProviderManager.
        """

        if limit <= 0:
            raise ValueError(
                "Industry enrichment limit must be greater than zero."
            )

        normalized_company = self._clean(company)
        normalized_ticker = self._normalize_ticker(ticker)
        normalized_industry = self._clean(industry)

        manager = self.provider_manager

        if manager is None:
            raise RuntimeError(
                "IndustryProviderManager is required "
                "for industry enrichment."
            )

        raw_data: dict[str, Any]

        # --------------------------------------------------------------
        # 1. COMPANY CLASSIFICATION
        # --------------------------------------------------------------

        if normalized_company or normalized_ticker:

            classify_method = getattr(
                manager,
                "classify_company",
                None,
            )

            if classify_method is None:
                raise AttributeError(
                    "IndustryProviderManager must expose "
                    "classify_company()."
                )

            result = classify_method(
                company=normalized_company,
                ticker=normalized_ticker,
                providers=providers,
                limit=limit,
                **kwargs,
            )

            if inspect.isawaitable(result):
                result = await result

            raw_data = self._normalize_provider_result(result)

        # --------------------------------------------------------------
        # 2. INDUSTRY LOOKUP
        # --------------------------------------------------------------

        elif normalized_industry:

            get_industry_method = getattr(
                manager,
                "get_industry",
                None,
            )

            if get_industry_method is None:
                raise AttributeError(
                    "IndustryProviderManager must expose "
                    "get_industry()."
                )

            result = get_industry_method(
                normalized_industry,
                providers=providers,
                limit=limit,
                **kwargs,
            )

            if inspect.isawaitable(result):
                result = await result

            raw_data = self._normalize_provider_result(result)

        else:

            raise ValueError(
                "Industry enrichment requires either "
                "company/ticker or an industry classification."
            )

        # --------------------------------------------------------------
        # Preserve company.
        # --------------------------------------------------------------

        if normalized_company:
            raw_data.setdefault(
                "company",
                normalized_company,
            )

        # --------------------------------------------------------------
        # Preserve ticker.
        # --------------------------------------------------------------

        if normalized_ticker:
            raw_data.setdefault(
                "ticker",
                normalized_ticker,
            )

        # --------------------------------------------------------------
        # Preserve explicitly supplied industry.
        # --------------------------------------------------------------

        if normalized_industry:
            raw_data.setdefault(
                "requested_industry",
                normalized_industry,
            )

        # --------------------------------------------------------------
        # Provider records.
        # --------------------------------------------------------------

        provider_records = self._extract_source_records(
            raw_data
        )

        if not provider_records:
            provider_records = [dict(raw_data)]

        raw_data["provider_records"] = provider_records

        # --------------------------------------------------------------
        # Provider classification has priority.
        #
        # Explicit industry is only used if the provider did not
        # produce one.
        # --------------------------------------------------------------

        provider_industry = self._extract_industry(
            raw_data
        )

        if provider_industry:
            raw_data["industry"] = provider_industry

        elif normalized_industry:
            raw_data["industry"] = normalized_industry

        else:
            record_industry = (
                self._extract_industry_from_records(
                    provider_records
                )
            )

            if record_industry:
                raw_data["industry"] = record_industry

        # --------------------------------------------------------------
        # HARD INVARIANT
        # --------------------------------------------------------------

        final_industry = self._extract_industry(
            raw_data
        )

        if not final_industry:
            final_industry = self._extract_industry_from_records(
                provider_records
            )

        if not final_industry:
            raise ValueError(
                "Industry provider enrichment failed "
                "to produce a canonical industry "
                "classification. "
                f"company={normalized_company!r} "
                f"ticker={normalized_ticker!r}. "
                f"Provider result keys="
                f"{list(raw_data.keys())!r}"
            )

        raw_data["industry"] = final_industry

        # --------------------------------------------------------------
        # Process acquired provider data.
        # --------------------------------------------------------------

        return await self.process(raw_data)

    # ==================================================================
    # PROVIDER RESULT NORMALIZATION
    # ==================================================================

    @classmethod
    def _normalize_provider_result(
        cls,
        result: Any,
    ) -> dict[str, Any]:
        """
        Convert supported provider-manager responses into
        one canonical dictionary.

        Supported shapes:

            dict
            nested dict
            list[dict]
            classification/result/data containers
            candidate lists

        Sector-only responses are rejected.
        """

        if result is None:
            return {}

        # --------------------------------------------------------------
        # Direct dictionary.
        # --------------------------------------------------------------

        if isinstance(result, Mapping):

            result_dict = dict(result)

            direct_industry = cls._extract_industry(
                result_dict
            )

            if direct_industry:

                normalized = dict(result_dict)

                normalized["industry"] = (
                    direct_industry
                )

                records = cls._extract_source_records(
                    result_dict
                )

                if not records:
                    records = [dict(result_dict)]

                normalized["provider_records"] = records

                return normalized

            # ----------------------------------------------------------
            # Nested provider payload.
            # ----------------------------------------------------------

            nested_keys = (
                "data",
                "result",
                "classification",
                "industry",
                "company",
                "response",
                "payload",
            )

            for key in nested_keys:

                nested = result_dict.get(key)

                if not isinstance(nested, Mapping):
                    continue

                nested_dict = dict(nested)

                nested_industry = cls._extract_industry(
                    nested_dict
                )

                if not nested_industry:
                    continue

                normalized = dict(result_dict)

                normalized.update(nested_dict)

                normalized["industry"] = (
                    nested_industry
                )

                normalized["provider_records"] = [
                    nested_dict
                ]

                return normalized

            # ----------------------------------------------------------
            # Candidate lists.
            # ----------------------------------------------------------

            candidate_keys = (
                "classifications",
                "results",
                "candidates",
                "industries",
                "data",
                "items",
            )

            for key in candidate_keys:

                candidates = result_dict.get(key)

                if not isinstance(candidates, list):
                    continue

                candidate = cls._select_best_candidate(
                    candidates
                )

                if candidate is None:
                    continue

                provider_records = [
                    dict(item)
                    for item in candidates
                    if isinstance(item, Mapping)
                ]

                normalized = dict(result_dict)
                normalized.update(candidate)

                normalized["industry"] = (
                    cls._extract_industry(candidate)
                )

                normalized["provider_records"] = (
                    provider_records
                )

                return normalized

            # ----------------------------------------------------------
            # No recognized industry.
            # ----------------------------------------------------------

            return result_dict

        # --------------------------------------------------------------
        # List of provider candidates.
        # --------------------------------------------------------------

        if isinstance(result, Sequence) and not isinstance(
            result,
            (str, bytes, bytearray),
        ):

            candidates = list(result)

            candidate = cls._select_best_candidate(
                candidates
            )

            if candidate is None:
                return {}

            provider_records = [
                dict(item)
                for item in candidates
                if isinstance(item, Mapping)
            ]

            normalized = dict(candidate)

            normalized["provider_records"] = (
                provider_records
            )

            return normalized

        return {}

    # ==================================================================
    # SELECT BEST PROVIDER CANDIDATE
    # ==================================================================

    @classmethod
    def _select_best_candidate(
        cls,
        candidates: Sequence[Any],
    ) -> dict[str, Any] | None:
        """
        Select the best usable industry classification candidate.

        Preference:

            1. Candidate containing industry
            2. Highest explicit confidence
            3. Highest explicit score
            4. First valid candidate

        Sector alone is never sufficient.
        """

        valid: list[dict[str, Any]] = []

        for candidate in candidates:

            if not isinstance(candidate, Mapping):
                continue

            candidate_dict = dict(candidate)

            industry = cls._extract_industry(
                candidate_dict
            )

            if not industry:
                continue

            candidate_dict["industry"] = industry

            valid.append(candidate_dict)

        if not valid:
            return None

        def confidence_value(
            item: dict[str, Any],
        ) -> float:

            raw_confidence = item.get(
                "confidence"
            )

            if raw_confidence is None:
                raw_confidence = item.get(
                    "confidence_score"
                )

            if raw_confidence is None:
                raw_confidence = item.get(
                    "score"
                )

            if raw_confidence is None:
                return 0.0

            try:
                return float(raw_confidence)

            except (TypeError, ValueError):
                return 0.0

        # Stable sorting means ties preserve provider order.
        valid.sort(
            key=confidence_value,
            reverse=True,
        )

        return valid[0]

    # ==================================================================
    # SEARCH + PROCESS
    # ==================================================================

    async def search_and_process(
        self,
        query: str,
        *,
        limit: int = 20,
        providers: list[str]
        | tuple[str, ...]
        | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Search industry providers and process results.
        """

        normalized_query = self._clean(query)

        if not normalized_query:
            raise ValueError(
                "Industry search query cannot be empty."
            )

        if limit <= 0:
            raise ValueError(
                "Industry search limit must be greater than zero."
            )

        manager = self.provider_manager

        if manager is None:
            raise RuntimeError(
                "IndustryProviderManager is required "
                "for industry search."
            )

        search_method = getattr(
            manager,
            "search_industry",
            None,
        )

        if search_method is None:
            raise AttributeError(
                "IndustryProviderManager must expose "
                "search_industry()."
            )

        results = search_method(
            normalized_query,
            limit=limit,
            providers=providers,
            **kwargs,
        )

        if inspect.isawaitable(results):
            results = await results

        if not results:
            return []

        if not isinstance(results, Sequence) or isinstance(
            results,
            (str, bytes, bytearray),
        ):
            raise TypeError(
                "IndustryProviderManager.search_industry() "
                "must return a list or sequence."
            )

        return await self.process_many(
            result
            for result in results
            if isinstance(result, Mapping)
        )

    # ==================================================================
    # SOURCE RECORD EXTRACTION
    # ==================================================================

    @staticmethod
    def _extract_source_records(
        payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Extract provider source records from payload.
        """

        records = payload.get(
            "provider_records"
        )

        if not isinstance(records, Sequence) or isinstance(
            records,
            (str, bytes, bytearray),
        ):
            return []

        return [
            dict(record)
            for record in records
            if isinstance(record, Mapping)
        ]

    @staticmethod
    def _copy_records(
        records: Iterable[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Safely copy provider source records.
        """

        return [
            dict(record)
            for record in records
            if isinstance(record, Mapping)
        ]

    # ==================================================================
    # INDUSTRY EXTRACTION
    # ==================================================================

    @classmethod
    def _extract_industry(
        cls,
        data: Any,
    ) -> str | None:
        """
        Extract a real industry classification.

        Sector is intentionally excluded.

        Supported industry fields:

            industry
            industry_name
            canonical_industry
            classification
            classification_name

        Important:
            "sector" is NEVER checked here.
        """

        if not isinstance(data, Mapping):
            return None

        for key in (
            "industry",
            "industry_name",
            "canonical_industry",
            "classification",
            "classification_name",
        ):

            value = cls._clean(
                data.get(key)
            )

            if value:
                return value

        return None

    @classmethod
    def _extract_industry_from_records(
        cls,
        records: Iterable[Mapping[str, Any]],
    ) -> str | None:
        """
        Extract industry from provider records.

        Sector-only records are ignored.
        """

        for record in records:

            if not isinstance(record, Mapping):
                continue

            industry = cls._extract_industry(
                record
            )

            if industry:
                return industry

        return None

    # ==================================================================
    # METADATA PRESERVATION
    # ==================================================================

    @staticmethod
    def _preserve_metadata(
        *,
        source: Mapping[str, Any],
        target: dict[str, Any],
        keys: Iterable[str],
    ) -> None:
        """
        Preserve metadata from source without overwriting
        resolver/normalizer decisions.
        """

        for key in keys:

            if (
                key not in target
                and key in source
            ):
                target[key] = source[key]

    # ==================================================================
    # STRING HELPERS
    # ==================================================================

    @staticmethod
    def _clean(
        value: Any,
    ) -> str | None:
        """
        Normalize a value into a clean string.
        """

        if value is None:
            return None

        if isinstance(value, str):
            cleaned = value.strip()

        else:
            cleaned = str(value).strip()

        return cleaned or None

    @classmethod
    def _normalize_ticker(
        cls,
        value: Any,
    ) -> str | None:
        """
        Normalize ticker into canonical uppercase form.
        """

        value = cls._clean(value)

        if not value:
            return None

        return value.upper()