
"""
app/company_catalog/processing/pipeline.py

Company Processing Pipeline.

Transforms raw provider data into a normalized, validated,
deduplicated, merged company record.

Processing Flow:

    Raw Provider Data
          |
          v
       Normalize
          |
          v
    Structural Validation
          |
          v
       Deduplicate
          |
          v
    Classification
      Preservation
          |
          v
         Merge
          |
          v
    Restore Canonical
       Identity
          |
          v
    Classification
      Normalization
          |
          v
       Confidence
          |
          v
     Final Validation
          |
          v
    Processed Company Data

IMPORTANT ARCHITECTURAL RULES

1. Provider-agnostic.
2. No database access.
3. No AsyncSession.
4. No CompanyRepository ownership.
5. No LLM analysis.
6. No investment analysis.
7. Canonical company identity supplied by the caller is preserved.
8. Provider-specific fields may enrich the record.
9. sector, industry and sub_industry are independent fields.
10. sector MUST NEVER be used as an industry fallback.
11. Classification metadata is first-class data.
12. Deduplication candidates are supplied by the caller.
13. Pipeline is synchronous and deterministic.
14. CompanyNormalizer is the canonical classification authority.
15. Missing industry metadata does NOT make a catalog record invalid.
16. Research-level industry validation belongs to ResearchService /
    AgentContext validation, not catalog ingestion.
17. CompanyDeduplicator is injected by the application composition root.
"""

from __future__ import annotations

import logging
from typing import Any

from app.company_catalog.processing.confidence import (
    CompanyConfidenceCalculator,
)
from app.company_catalog.processing.deduplicate import (
    CompanyDeduplicator,
)
from app.company_catalog.processing.merge import (
    CompanyMerger,
)
from app.company_catalog.processing.normalizer import (
    CompanyNormalizer,
)
from app.company_catalog.processing.validator import (
    CompanyValidator,
)

logger = logging.getLogger(__name__)


class CompanyProcessingPipeline:
    """
    Deterministic company ingestion and processing pipeline.

    The pipeline is deliberately database-free.

    Existing company candidates must be supplied by the caller.

    CompanyDeduplicator is injected into the pipeline so that
    application composition remains responsible for constructing
    shared infrastructure.

    Example:

        deduplicator = CompanyDeduplicator()

        pipeline = CompanyProcessingPipeline(
            deduplicator=deduplicator,
        )

        result = pipeline.process(data)

    Or with explicit candidates:

        result = pipeline.process(
            data,
            candidates=existing_records,
        )
    """

    # =========================================================
    # Canonical Identity
    # =========================================================

    CANONICAL_IDENTITY_FIELDS = {
        "id",
        "company_id",
        "company",
        "company_name",
        "name",
        "ticker",
        "symbol",
        "stock_symbol",
        "research_id",
    }

    # =========================================================
    # Classification
    # =========================================================

    CLASSIFICATION_FIELDS = {
        "sector",
        "industry",
        "sub_industry",
    }

    # =========================================================
    # Constructor
    # =========================================================

    def __init__(
        self,
        deduplicator: CompanyDeduplicator,
    ) -> None:
        """
        Initialize the processing pipeline.

        Parameters
        ----------
        deduplicator:
            Application-provided CompanyDeduplicator.

        The pipeline does not construct the deduplicator itself.
        """

        if not isinstance(
            deduplicator,
            CompanyDeduplicator,
        ):
            raise TypeError(
                "CompanyProcessingPipeline requires "
                "a CompanyDeduplicator instance."
            )

        self.deduplicator = deduplicator

        logger.debug(
            "CompanyProcessingPipeline initialized | "
            "deduplicator=%s",
            type(deduplicator).__name__,
        )

    # =========================================================
    # Public API
    # =========================================================

    def process(
        self,
        data: dict[str, Any],
        candidates: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Process raw company/provider data.

        Parameters
        ----------
        data:
            Raw or partially normalized company data.

        candidates:
            Optional existing company dictionaries used for
            dictionary-level deduplication and enrichment.

        Returns
        -------
        dict[str, Any]
            Normalized and validated company record.

        Important
        ---------
        This method does NOT require industry metadata.

        A catalog record may legitimately contain:

            name
            ticker
            cik

        without:

            industry
            sub_industry

        Research workflows are responsible for validating that
        industry metadata exists before creating a research context.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "CompanyProcessingPipeline.process() "
                "requires data to be a dictionary."
            )

        if not data:
            raise ValueError(
                "CompanyProcessingPipeline received empty data."
            )

        if candidates is None:
            candidates = []

        if not isinstance(candidates, list):
            raise TypeError(
                "candidates must be a list of dictionaries."
            )

        if not all(
            isinstance(candidate, dict)
            for candidate in candidates
        ):
            raise TypeError(
                "Every candidate must be a dictionary."
            )

        logger.debug(
            "CompanyProcessingPipeline started | "
            "fields=%s | candidates=%d",
            sorted(data.keys()),
            len(candidates),
        )

        # =====================================================
        # 1. Preserve canonical identity
        # =====================================================

        canonical_identity = (
            self._extract_canonical_identity(data)
        )

        # =====================================================
        # 2. Preserve incoming classification
        # =====================================================

        incoming_classification = (
            self._extract_classification(data)
        )

        # =====================================================
        # 3. Normalize
        # =====================================================

        normalized = CompanyNormalizer.normalize(
            dict(data)
        )

        if not isinstance(normalized, dict):
            raise TypeError(
                "CompanyNormalizer.normalize() must return "
                "a dictionary."
            )

        # =====================================================
        # 4. Normalize classification
        # =====================================================

        self._normalize_classification_fields(
            normalized
        )

        # =====================================================
        # 5. Restore canonical identity
        # =====================================================

        normalized = self._restore_canonical_identity(
            normalized,
            canonical_identity,
        )

        # =====================================================
        # 6. Restore incoming classification
        # =====================================================

        self._restore_classification(
            normalized,
            incoming_classification,
        )

        # =====================================================
        # 7. Structural validation
        # =====================================================

        self._validate_structural_data(
            normalized
        )

        # =====================================================
        # 8. Find duplicate
        # =====================================================
        #
        # IMPORTANT:
        #
        # The deduplicator is injected through __init__.
        #
        # Do NOT create:
        #
        #     CompanyDeduplicator()
        #
        # here.
        #

        existing = self.deduplicator.find_existing(
            normalized,
            candidates,
        )

        # =====================================================
        # 9. Normalize existing candidate
        # =====================================================

        existing_classification: dict[str, Any] = {}

        if isinstance(existing, dict):

            existing_classification = (
                self._extract_classification(existing)
            )

            existing = CompanyNormalizer.normalize(
                dict(existing)
            )

            if not isinstance(existing, dict):
                existing = {}

            self._normalize_classification_fields(
                existing
            )

            self._restore_classification(
                existing,
                existing_classification,
            )

        # =====================================================
        # 10. Merge
        # =====================================================

        merged = CompanyMerger.merge(
            existing,
            normalized,
        )

        if not isinstance(merged, dict):
            raise TypeError(
                "CompanyMerger.merge() must return "
                "a dictionary."
            )

        # =====================================================
        # 11. Restore existing classification
        # =====================================================

        self._restore_classification(
            merged,
            existing_classification,
        )

        # =====================================================
        # 12. Restore incoming classification
        #
        # Incoming provider metadata has precedence over
        # existing metadata when it contains meaningful data.
        # =====================================================

        self._restore_classification(
            merged,
            incoming_classification,
        )

        # =====================================================
        # 13. Normalize classification
        # =====================================================

        self._normalize_classification_fields(
            merged
        )

        # =====================================================
        # 14. Restore canonical identity again
        #
        # Merge must never replace caller-supplied canonical
        # company identity.
        # =====================================================

        merged = self._restore_canonical_identity(
            merged,
            canonical_identity,
        )

        # =====================================================
        # 15. Restore classification one final time
        # =====================================================

        self._restore_classification(
            merged,
            existing_classification,
        )

        self._restore_classification(
            merged,
            incoming_classification,
        )

        # =====================================================
        # 16. Final classification normalization
        # =====================================================

        self._normalize_classification_fields(
            merged
        )

        # =====================================================
        # 17. Calculate confidence
        # =====================================================

        confidence = (
            CompanyConfidenceCalculator.calculate(
                merged
            )
        )

        merged["confidence"] = confidence

        # =====================================================
        # 18. Final identity normalization
        # =====================================================

        merged = self._normalize_final_identity(
            merged
        )

        # =====================================================
        # 19. Final validation
        # =====================================================

        self._validate_processed_company(
            merged
        )

        logger.debug(
            "CompanyProcessingPipeline completed | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "cik=%r | "
            "sector=%r | "
            "industry=%r | "
            "sub_industry=%r | "
            "confidence=%r",
            merged.get("company_id"),
            merged.get("company_name"),
            merged.get("ticker"),
            merged.get("cik"),
            merged.get("sector"),
            merged.get("industry"),
            merged.get("sub_industry"),
            merged.get("confidence"),
        )

        return merged

    # =========================================================
    # Structural Validation
    # =========================================================

    @staticmethod
    def _validate_structural_data(
        data: dict[str, Any],
    ) -> None:
        """
        Validate basic company identity.

        Industry validation intentionally does NOT happen here.

        Catalog records can legitimately be created from SEC,
        ticker, identifier, or other master-data sources without
        classification metadata.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "Normalized company must be a dictionary."
            )

        name = (
            data.get("name")
            or data.get("company_name")
            or data.get("company")
        )

        ticker = (
            data.get("ticker")
            or data.get("symbol")
            or data.get("stock_symbol")
        )

        # A company can be identified by name OR ticker.
        if not name and not ticker:
            raise ValueError(
                "CompanyProcessingPipeline requires "
                "company name or ticker."
            )

        if name:
            CompanyValidator.validate_name(
                name
            )

        if ticker:
            CompanyValidator.validate_ticker(
                ticker
            )

    # =========================================================
    # Classification Extraction
    # =========================================================

    @classmethod
    def _extract_classification(
        cls,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extract canonical classification fields.

        CompanyNormalizer is the single authority for:

            sector
            industry
            sub_industry

        No classification dimension is inferred from another.
        """

        if not isinstance(data, dict):
            return {}

        classification = (
            CompanyNormalizer.normalize_classification(
                data
            )
        )

        if not isinstance(
            classification,
            dict,
        ):
            return {}

        return {
            field: classification.get(field)
            for field in cls.CLASSIFICATION_FIELDS
            if classification.get(field) is not None
        }

    # =========================================================
    # Classification Normalization
    # =========================================================

    @classmethod
    def _normalize_classification_fields(
        cls,
        company: dict[str, Any],
    ) -> None:
        """
        Normalize canonical classification fields.

        IMPORTANT:

        sector does not become industry.

        industry does not become sector.

        sub_industry does not become industry.
        """

        if not isinstance(company, dict):
            return

        classification = (
            CompanyNormalizer.normalize_classification(
                company
            )
        )

        if not isinstance(
            classification,
            dict,
        ):
            return

        for field in cls.CLASSIFICATION_FIELDS:

            value = classification.get(field)

            if (
                isinstance(value, str)
                and value.strip()
            ):
                company[field] = value.strip()

    # =========================================================
    # Classification Restoration
    # =========================================================

    @classmethod
    def _restore_classification(
        cls,
        data: dict[str, Any],
        classification: dict[str, Any],
    ) -> None:
        """
        Restore meaningful classification values.

        Each classification dimension is independent.

        Never performs:

            industry = sector
        """

        if not isinstance(data, dict):
            return

        if not isinstance(
            classification,
            dict,
        ):
            return

        for field in cls.CLASSIFICATION_FIELDS:

            value = classification.get(field)

            if (
                isinstance(value, str)
                and value.strip()
            ):
                data[field] = value.strip()

    # =========================================================
    # Canonical Identity Extraction
    # =========================================================

    @classmethod
    def _extract_canonical_identity(
        cls,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extract caller-supplied canonical identity before
        normalization and merging.

        Classification is intentionally excluded.
        """

        identity: dict[str, Any] = {}

        # -----------------------------------------------------
        # Research ID
        # -----------------------------------------------------

        research_id = data.get(
            "research_id"
        )

        if research_id is not None:
            identity["research_id"] = research_id

        # -----------------------------------------------------
        # Company ID
        # -----------------------------------------------------

        company_id = data.get(
            "company_id"
        )

        if company_id is None:
            company_id = data.get("id")

        if company_id is not None:
            identity["company_id"] = company_id

        # -----------------------------------------------------
        # Company Name
        # -----------------------------------------------------

        company_name = (
            data.get("company_name")
            or data.get("company")
            or data.get("name")
        )

        if company_name:
            identity["company_name"] = str(
                company_name
            ).strip()

        # -----------------------------------------------------
        # Ticker
        # -----------------------------------------------------

        ticker = (
            data.get("ticker")
            or data.get("symbol")
            or data.get("stock_symbol")
        )

        if ticker:
            normalized_ticker = (
                CompanyNormalizer.normalize_ticker(
                    ticker
                )
            )

            if normalized_ticker:
                identity["ticker"] = (
                    normalized_ticker
                )

        return identity

    # =========================================================
    # Restore Canonical Identity
    # =========================================================

    @classmethod
    def _restore_canonical_identity(
        cls,
        data: dict[str, Any],
        canonical_identity: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Restore caller-supplied canonical identity.

        Classification is untouched.
        """

        result = dict(data)

        # -----------------------------------------------------
        # Research ID
        # -----------------------------------------------------

        research_id = canonical_identity.get(
            "research_id"
        )

        if research_id is not None:
            result["research_id"] = research_id

        # -----------------------------------------------------
        # Company ID
        # -----------------------------------------------------

        company_id = canonical_identity.get(
            "company_id"
        )

        if company_id is not None:
            result["company_id"] = company_id
            result["id"] = company_id

        # -----------------------------------------------------
        # Company Name
        # -----------------------------------------------------

        company_name = canonical_identity.get(
            "company_name"
        )

        if company_name:
            result["company_name"] = company_name
            result["company"] = company_name
            result["name"] = company_name

        # -----------------------------------------------------
        # Ticker
        # -----------------------------------------------------

        ticker = canonical_identity.get(
            "ticker"
        )

        if ticker:
            result["ticker"] = ticker
            result["symbol"] = ticker

        return result

    # =========================================================
    # Final Identity Normalization
    # =========================================================

    @classmethod
    def _normalize_final_identity(
        cls,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize final identity aliases.

        Produces canonical aliases:

            company_id
            company_name
            company
            name
            ticker
            symbol
            normalized_name
        """

        result = dict(data)

        # -----------------------------------------------------
        # Company ID
        # -----------------------------------------------------

        company_id = result.get(
            "company_id"
        )

        if company_id is None:
            company_id = result.get("id")

        if company_id is not None:
            result["company_id"] = company_id

        # -----------------------------------------------------
        # Company Name
        # -----------------------------------------------------

        company_name = (
            result.get("company_name")
            or result.get("company")
            or result.get("name")
        )

        if company_name:

            company_name = str(
                company_name
            ).strip()

            result["company_name"] = company_name
            result["company"] = company_name
            result["name"] = company_name

            result["normalized_name"] = (
                CompanyNormalizer.normalize_name_for_matching(
                    company_name
                )
            )

        # -----------------------------------------------------
        # Ticker
        # -----------------------------------------------------

        ticker = (
            result.get("ticker")
            or result.get("symbol")
            or result.get("stock_symbol")
        )

        ticker = (
            CompanyNormalizer.normalize_ticker(
                ticker
            )
        )

        if ticker:
            result["ticker"] = ticker
            result["symbol"] = ticker
        else:
            result["ticker"] = None

        # -----------------------------------------------------
        # Classification
        # -----------------------------------------------------

        cls._normalize_classification_fields(
            result
        )

        return result

    # =========================================================
    # Final Validation
    # =========================================================

    @staticmethod
    def _validate_processed_company(
        data: dict[str, Any],
    ) -> None:
        """
        Validate final catalog company data.

        Required:

            company identity

        Optional:

            industry
            sub_industry

        Industry is deliberately NOT required here.

        Why?

        Company catalog ingestion and research enrichment
        are separate responsibilities.

        Example:

            SEC
              -> name
              -> ticker
              -> CIK

        is a valid company catalog record even when SEC does
        not provide industry metadata.

        ResearchService is responsible for enforcing:

            industry OR sub_industry

        before constructing a research-ready AgentContext.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "Processed company must be a dictionary."
            )

        company_id = data.get(
            "company_id"
        )

        company_name = data.get(
            "company_name"
        )

        ticker = data.get(
            "ticker"
        )

        if not (
            company_id is not None
            or company_name
            or ticker
        ):
            raise ValueError(
                "CompanyProcessingPipeline could not "
                "produce a valid company identity."
            )

        # -----------------------------------------------------
        # Classification sanity checks
        # -----------------------------------------------------

        for field in (
            "sector",
            "industry",
            "sub_industry",
        ):
            value = data.get(field)

            if value is None:
                continue

            if not isinstance(value, str):
                raise ValueError(
                    f"Company classification field "
                    f"'{field}' must be a string or None."
                )

            if not value.strip():
                data[field] = None

        # -----------------------------------------------------
        # IMPORTANT
        # -----------------------------------------------------
        #
        # Do NOT do:
        #
        #     if not industry:
        #         industry = sector
        #
        # or:
        #
        #     if not industry:
        #         industry = sub_industry
        #
        # Classification dimensions are independent.

