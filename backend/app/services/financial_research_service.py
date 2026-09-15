"""
app/services/financial_research_service.py

Financial Research Service.

Responsible for acquiring and normalizing financial
information for FinancialAnalysisAgent.

Architecture:

    FinancialAnalysisAgent
            |
            v
    FinancialResearchService
            |
            v
    FinancialProviderManager
            |
       +----+----+
       |         |
       v         v
   Providers   Future Providers
       |
       v
YahooFinanceProvider
       |
       v
YahooFinanceTool
       |
       v
    yfinance

IMPORTANT ARCHITECTURAL RULES

1. FinancialResearchService is application-scoped /
   singleton-safe.

2. FinancialProviderManager is a shared application-level
   dependency.

3. FinancialResearchService MUST NOT store AgentContext.

4. FinancialResearchService MUST NOT store Task.

5. FinancialResearchService MUST NOT create AgentContext.

6. FinancialResearchService receives the SAME AgentContext
   instance created by ResearchService.

7. FinancialResearchService does not perform financial analysis.

8. FinancialResearchService only acquires and normalizes
   financial data.

9. Canonical company identity comes from AgentContext:

       context.research_id
       context.company_id
       context.company
       context.ticker
       context.industry

10. Provider data is financial enrichment only.

11. Provider output must never overwrite canonical company
    identity supplied by AgentContext.

12. FinancialProviderManager is the only dependency that knows
    about individual financial providers.

13. FinancialResearchService does not interact directly with
    YahooFinanceTool or yfinance.

14. Provider failures are allowed to propagate to the agent,
    where AgentResult.failure() is constructed.

15. This service does not own database sessions.

16. FinancialResearchService defensively sanitizes provider
    output so non-JSON-safe values such as NaN, inf, -inf,
    pandas.NA, and numpy scalar values cannot leak downstream.
"""

from __future__ import annotations

import logging
import math
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from app.financial.providers.provider_manager import (
    FinancialProviderManager,
)

if TYPE_CHECKING:
    from app.agents.base.agent_context import AgentContext


logger = logging.getLogger(__name__)


class FinancialResearchService:
    """
    Financial-data acquisition service.

    Responsibilities:

    - Acquire financial data through FinancialProviderManager.
    - Preserve canonical company identity.
    - Normalize provider output.
    - Normalize financial statements.
    - Normalize financial metrics.
    - Normalize sources.
    - Sanitize non-JSON-safe provider values.
    - Attach research/runtime identity.
    - Return provider-agnostic financial data.

    Financial analysis belongs to FinancialAnalysisAgent.

    The service is application-scoped and singleton-safe.

    FinancialProviderManager is injected once at construction.
    AgentContext is supplied per research call.
    """

    # =========================================================
    # Construction
    # =========================================================

    def __init__(
        self,
        *,
        provider_manager: FinancialProviderManager,
    ) -> None:
        """
        Initialize the financial research service.

        FinancialProviderManager is a shared application-level
        dependency and is therefore injected through the
        composition root.

        AgentContext is intentionally NOT stored on the service.
        """

        if provider_manager is None:
            raise ValueError(
                "FinancialResearchService requires "
                "FinancialProviderManager."
            )

        if not isinstance(
            provider_manager,
            FinancialProviderManager,
        ):
            raise TypeError(
                "provider_manager must be a "
                "FinancialProviderManager instance, "
                f"got {type(provider_manager).__name__}."
            )

        self.provider_manager = provider_manager

    # =========================================================
    # Public API
    # =========================================================

    async def get_financial_data(
        self,
        *,
        context: AgentContext,
    ) -> dict[str, Any]:
        """
        Acquire and normalize financial data.

        Canonical contract:

            await service.get_financial_data(
                context=context
            )

        The exact AgentContext instance supplied by
        FinancialAnalysisAgent is used.

        No Task is accepted.

        No AgentContext is created.

        No context dictionary is created.
        """

        # -----------------------------------------------------
        # Validate context
        # -----------------------------------------------------

        if context is None:
            raise ValueError(
                "FinancialResearchService requires an AgentContext."
            )

        # -----------------------------------------------------
        # Validate required context shape.
        #
        # We intentionally avoid importing AgentContext at
        # runtime because it is only required for type checking.
        # -----------------------------------------------------

        required_attributes = (
            "research_id",
            "company_id",
            "company",
            "ticker",
            "industry",
        )

        missing_attributes = [
            attribute
            for attribute in required_attributes
            if not hasattr(context, attribute)
        ]

        if missing_attributes:
            raise TypeError(
                "FinancialResearchService received an invalid "
                "AgentContext. Missing attributes: "
                + ", ".join(missing_attributes)
            )

        # -----------------------------------------------------
        # Runtime identity
        # -----------------------------------------------------

        research_id = context.research_id
        company_id = context.company_id
        company = context.company
        ticker = context.ticker
        industry = context.industry

        # -----------------------------------------------------
        # Log request.
        # -----------------------------------------------------

        logger.info(
            "FinancialResearchService started | "
            "research_id=%r | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "industry=%r | "
            "context_object_id=%s",
            research_id,
            company_id,
            company,
            ticker,
            industry,
            id(context),
        )

        # =====================================================
        # Validate runtime company identity
        # =====================================================

        if not company and not ticker:
            raise ValueError(
                "FinancialResearchService requires "
                "context.company or context.ticker."
            )

        # =====================================================
        # Validate ticker
        # =====================================================

        #
        # Financial providers generally require a ticker.
        #
        # We do not invent one from company name here.
        # Company identity resolution belongs upstream.
        #

        if not ticker:
            logger.warning(
                "FinancialResearchService received no ticker | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r",
                research_id,
                company_id,
                company,
            )

        # =====================================================
        # Provider Manager
        # =====================================================

        try:
            logger.info(
                "FinancialResearchService → "
                "FinancialProviderManager | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r",
                research_id,
                company_id,
                company,
                ticker,
            )

            data = await self._get_provider_data(
                company=company,
                ticker=ticker,
            )

        except Exception:
            logger.exception(
                "FinancialProviderManager failed | "
                "research_id=%r | "
                "company_id=%r | "
                "company=%r | "
                "ticker=%r",
                research_id,
                company_id,
                company,
                ticker,
            )

            # Provider failures intentionally propagate.
            raise

        # =====================================================
        # Validate provider output
        # =====================================================

        if data is None:
            raise RuntimeError(
                "FinancialProviderManager returned no financial data."
            )

        if not isinstance(data, dict):
            raise RuntimeError(
                "FinancialProviderManager returned invalid "
                "financial data. Expected dict, got "
                f"{type(data).__name__}."
            )

        # =====================================================
        # Defensive JSON-safe sanitization
        # =====================================================

        #
        # Even though YahooFinanceTool already sanitizes values,
        # this service is a provider-agnostic boundary and must
        # not assume every future provider does the same.
        #

        data = self._sanitize_value(data)

        if not isinstance(data, dict):
            raise RuntimeError(
                "Financial provider output became invalid after "
                "normalization. Expected dict."
            )

        # =====================================================
        # Normalize
        # =====================================================

        normalized = self._normalize_financial_data(
            data=data,
            context=context,
        )

        # =====================================================
        # Final JSON-safe sanitization
        # =====================================================

        normalized = self._sanitize_value(normalized)

        if not isinstance(normalized, dict):
            raise RuntimeError(
                "Normalized financial data is invalid. "
                "Expected dict."
            )

        # =====================================================
        # Final canonical identity protection
        # =====================================================

        normalized = self._apply_canonical_identity(
            data=normalized,
            context=context,
        )

        logger.info(
            "FinancialResearchService completed | "
            "research_id=%r | "
            "company_id=%r | "
            "company=%r | "
            "ticker=%r | "
            "industry=%r | "
            "context_object_id=%s",
            research_id,
            company_id,
            normalized.get("company"),
            normalized.get("ticker"),
            normalized.get("industry"),
            id(context),
        )

        return normalized

    # =========================================================
    # JSON-Safe Sanitization
    # =========================================================

    @classmethod
    def _sanitize_value(
        cls,
        value: Any,
    ) -> Any:
        """
        Recursively convert provider values into JSON-safe values.

        Converts:

            NaN       -> None
            +inf      -> None
            -inf      -> None
            pandas.NA -> None
            pandas.NaT -> None

        Also converts:

            numpy scalar -> native Python scalar
            datetime/date -> ISO-8601 string
            dict         -> recursively sanitized dict
            list/tuple   -> recursively sanitized list
            set          -> recursively sanitized list

        This is intentionally provider-agnostic.
        """

        # -----------------------------------------------------
        # None
        # -----------------------------------------------------

        if value is None:
            return None

        # -----------------------------------------------------
        # pandas missing values
        # -----------------------------------------------------

        try:
            if value is pd.NA or value is pd.NaT:
                return None
        except Exception:
            pass

        # -----------------------------------------------------
        # Dictionary
        # -----------------------------------------------------

        if isinstance(value, dict):
            sanitized: dict[str, Any] = {}

            for key, item in value.items():
                sanitized[str(key)] = cls._sanitize_value(item)

            return sanitized

        # -----------------------------------------------------
        # Sequence
        # -----------------------------------------------------

        if isinstance(value, (list, tuple, set)):
            return [
                cls._sanitize_value(item)
                for item in value
            ]

        # -----------------------------------------------------
        # Datetime / date
        # -----------------------------------------------------

        if isinstance(value, (datetime, date)):
            try:
                return value.isoformat()
            except Exception:
                return str(value)

        # -----------------------------------------------------
        # NumPy scalar
        # -----------------------------------------------------

        if isinstance(value, np.generic):
            try:
                value = value.item()
            except Exception:
                pass

        # -----------------------------------------------------
        # Boolean
        # -----------------------------------------------------

        if isinstance(value, bool):
            return value

        # -----------------------------------------------------
        # Numeric values
        # -----------------------------------------------------

        if isinstance(value, (int, float)):
            if isinstance(value, float):
                try:
                    if not math.isfinite(value):
                        return None
                except Exception:
                    return None

            return value

        # -----------------------------------------------------
        # Complex numbers
        #
        # Complex numbers are not JSON-safe. If the imaginary
        # component is zero, preserve the real value.
        # Otherwise convert to None.
        # -----------------------------------------------------

        if isinstance(value, complex):
            try:
                if value.imag == 0:
                    real_value = float(value.real)

                    if not math.isfinite(real_value):
                        return None

                    return real_value

            except Exception:
                pass

            return None

        # -----------------------------------------------------
        # pandas / numpy missing-value detection
        #
        # pd.isna() can return an array/Series for some objects,
        # so only scalar boolean results are accepted.
        # -----------------------------------------------------

        try:
            missing = pd.isna(value)

            if isinstance(missing, (bool, np.bool_)):
                if bool(missing):
                    return None

        except Exception:
            pass

        # -----------------------------------------------------
        # Objects exposing .item()
        # -----------------------------------------------------

        try:
            item_method = getattr(value, "item", None)

            if callable(item_method):
                converted = item_method()

                if converted is not value:
                    return cls._sanitize_value(converted)

        except Exception:
            pass

        # -----------------------------------------------------
        # Strings
        # -----------------------------------------------------

        if isinstance(value, str):
            return value

        # -----------------------------------------------------
        # Bytes
        # -----------------------------------------------------

        if isinstance(value, bytes):
            try:
                return value.decode("utf-8")
            except Exception:
                return str(value)

        # -----------------------------------------------------
        # Final fallback
        # -----------------------------------------------------

        return value

    # =========================================================
    # Provider Invocation
    # =========================================================

    async def _get_provider_data(
        self,
        *,
        company: str | None,
        ticker: str | None,
    ) -> dict[str, Any]:
        """
        Invoke FinancialProviderManager.

        FinancialResearchService does not know which provider
        is selected internally.

        Preferred manager API:

            get_financial_data(
                company=...,
                ticker=...,
            )

        The provider manager remains responsible for provider
        selection, fallback, and provider-specific behavior.
        """

        method = getattr(
            self.provider_manager,
            "get_financial_data",
            None,
        )

        if not callable(method):
            raise AttributeError(
                "FinancialProviderManager does not expose "
                "get_financial_data()."
            )

        result = method(
            company=company,
            ticker=ticker,
        )

        # -----------------------------------------------------
        # Support synchronous manager implementations during
        # migration.
        # -----------------------------------------------------

        if hasattr(result, "__await__"):
            result = await result

        if not isinstance(result, dict):
            raise RuntimeError(
                "FinancialProviderManager.get_financial_data() "
                "must return a dictionary."
            )

        return result

    # =========================================================
    # Normalization
    # =========================================================

    @classmethod
    def _normalize_financial_data(
        cls,
        *,
        data: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """
        Normalize provider output into the canonical
        FinancialResearchService contract.

        Supported statement aliases include:

            income_statement
            income_statement_data
            income

            balance_sheet
            balance_sheet_data
            balance

            cash_flow_statement
            cash_flow
            cash_flow_data

        Different financial providers can represent statements
        differently. The canonical service contract accepts
        dictionaries or lists.
        """

        if not isinstance(data, dict):
            data = {}

        # =====================================================
        # Financial Statements
        # =====================================================

        income_statement = cls._first_present_value(
            data,
            (
                "income_statement",
                "income_statement_data",
                "income",
            ),
            default=[],
        )

        balance_sheet = cls._first_present_value(
            data,
            (
                "balance_sheet",
                "balance_sheet_data",
                "balance",
            ),
            default=[],
        )

        cash_flow_statement = cls._first_present_value(
            data,
            (
                "cash_flow_statement",
                "cash_flow",
                "cash_flow_data",
            ),
            default=[],
        )

        # =====================================================
        # Financial Metrics
        # =====================================================

        financial_metrics = cls._first_present_value(
            data,
            (
                "financial_metrics",
                "metrics",
                "valuation",
            ),
            default={},
        )

        # =====================================================
        # Overview
        # =====================================================

        overview = data.get(
            "overview",
            {},
        )

        if not isinstance(overview, dict):
            overview = {}

        # =====================================================
        # Sources
        # =====================================================

        sources = data.get(
            "sources",
            [],
        )

        singular_source = data.get(
            "source"
        )

        if singular_source is not None:
            sources = cls._normalize_sources(
                sources
            )

            if singular_source not in sources:
                sources.append(
                    singular_source
                )

        # =====================================================
        # Defensive Statement Validation
        # =====================================================

        income_statement = cls._normalize_statement(
            income_statement,
            "income_statement",
        )

        balance_sheet = cls._normalize_statement(
            balance_sheet,
            "balance_sheet",
        )

        cash_flow_statement = cls._normalize_statement(
            cash_flow_statement,
            "cash_flow_statement",
        )

        # =====================================================
        # Defensive Metrics Validation
        # =====================================================

        if not isinstance(
            financial_metrics,
            dict,
        ):
            logger.warning(
                "Invalid financial_metrics received from "
                "financial provider. Replacing with empty dict."
            )

            financial_metrics = {}

        # =====================================================
        # Defensive Sources Validation
        # =====================================================

        sources = cls._normalize_sources(
            sources
        )

        # =====================================================
        # Company Identity
        # =====================================================

        #
        # Provider identity is NOT canonical.
        #
        # The final canonical identity is reapplied from
        # AgentContext below.
        #

        provider_company = (
            data.get("company")
            or data.get("company_name")
            or data.get("name")
        )

        provider_company_name = (
            data.get("company_name")
            or data.get("company")
            or data.get("name")
        )

        provider_ticker = (
            data.get("ticker")
            or data.get("symbol")
            or data.get("stock_symbol")
        )

        # =====================================================
        # Metadata
        # =====================================================

        metadata = data.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        metadata = dict(metadata)

        # Preserve runtime identity.

        if context.research_id is not None:
            metadata["research_id"] = (
                context.research_id
            )

        if context.company_id is not None:
            metadata["company_id"] = (
                context.company_id
            )

        # =====================================================
        # Canonical Financial Data Contract
        # =====================================================

        normalized: dict[str, Any] = {
            # -------------------------------------------------
            # Runtime identity
            # -------------------------------------------------

            "research_id": context.research_id,
            "company_id": context.company_id,

            # -------------------------------------------------
            # Company
            # -------------------------------------------------

            "company": (
                provider_company
                or context.company
                or context.ticker
            ),

            "company_name": (
                provider_company_name
                or context.company
                or context.ticker
            ),

            "ticker": (
                provider_ticker
                or context.ticker
            ),

            # -------------------------------------------------
            # Company Metadata
            # -------------------------------------------------

            # Industry is canonical from AgentContext.
            "industry": context.industry,

            # Sector is provider metadata only.
            "sector": data.get(
                "sector"
            ),

            "country": (
                data.get("country")
                or overview.get("country")
            ),

            "exchange": (
                data.get("exchange")
                or overview.get("exchange")
            ),

            "currency": (
                data.get("currency")
                or overview.get("currency")
            ),

            "description": (
                data.get("description")
                or overview.get("description")
            ),

            # -------------------------------------------------
            # Financial Statements
            # -------------------------------------------------

            "income_statement": income_statement,

            "balance_sheet": balance_sheet,

            "cash_flow_statement": cash_flow_statement,

            # -------------------------------------------------
            # Financial Metrics
            # -------------------------------------------------

            "financial_metrics": financial_metrics,

            # -------------------------------------------------
            # Overview
            # -------------------------------------------------

            "overview": overview,

            # -------------------------------------------------
            # Sources
            # -------------------------------------------------

            "sources": sources,

            # -------------------------------------------------
            # Metadata
            # -------------------------------------------------

            "metadata": metadata,
        }

        # =====================================================
        # Preserve Additional Provider Fields
        # =====================================================

        #
        # Keep useful financial information that does not have
        # a dedicated canonical field yet.
        #
        # We deliberately do not blindly copy identity fields.
        #

        protected_fields = {
            "research_id",
            "company_id",
            "company",
            "company_name",
            "name",
            "ticker",
            "symbol",
            "stock_symbol",
            "industry",
            "sub_industry",
            "sector",
            "sources",
            "source",
            "metadata",
            "income_statement",
            "income_statement_data",
            "income",
            "balance_sheet",
            "balance_sheet_data",
            "balance",
            "cash_flow_statement",
            "cash_flow",
            "cash_flow_data",
            "financial_metrics",
            "metrics",
            "valuation",
            "overview",
        }

        for key, value in data.items():
            if key in protected_fields:
                continue

            if value is None:
                continue

            if key not in normalized:
                normalized[key] = value

        # =====================================================
        # Reassert canonical identity
        # =====================================================

        normalized = cls._apply_canonical_identity(
            data=normalized,
            context=context,
        )

        # =====================================================
        # Final recursive sanitization
        # =====================================================

        sanitized = cls._sanitize_value(
            normalized
        )

        if not isinstance(sanitized, dict):
            raise RuntimeError(
                "Financial normalization produced an invalid "
                "result. Expected dictionary."
            )

        return sanitized

    # =========================================================
    # Canonical Identity
    # =========================================================

    @staticmethod
    def _apply_canonical_identity(
        *,
        data: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """
        Reapply canonical company identity from AgentContext.

        AgentContext always wins.

        Provider output cannot replace:

            research_id
            company_id
            company
            company_name
            ticker
            industry
        """

        result = dict(data)

        # -----------------------------------------------------
        # Research identity
        # -----------------------------------------------------

        result["research_id"] = (
            context.research_id
        )

        # -----------------------------------------------------
        # Company ID
        # -----------------------------------------------------

        if context.company_id is not None:
            result["company_id"] = (
                context.company_id
            )

        # -----------------------------------------------------
        # Company
        # -----------------------------------------------------

        if context.company:
            result["company"] = (
                context.company
            )

            result["company_name"] = (
                context.company
            )

        # -----------------------------------------------------
        # Ticker
        # -----------------------------------------------------

        if context.ticker:
            result["ticker"] = (
                str(context.ticker)
                .strip()
                .upper()
            )

        # -----------------------------------------------------
        # Industry
        # -----------------------------------------------------

        if context.industry:
            result["industry"] = (
                str(context.industry)
                .strip()
            )

        return result

    # =========================================================
    # Statement Normalization
    # =========================================================

    @staticmethod
    def _normalize_statement(
        value: Any,
        field_name: str,
    ) -> dict[str, Any] | list[Any]:
        """
        Normalize a financial statement.

        Financial providers may return either:

            dict

        or:

            list

        Invalid values are replaced with an empty list.
        """

        if isinstance(
            value,
            (dict, list),
        ):
            return value

        if value is None:
            return []

        logger.warning(
            "Invalid %s received from financial provider. "
            "Replacing with empty list | type=%s",
            field_name,
            type(value).__name__,
        )

        return []

    # =========================================================
    # First Present Value
    # =========================================================

    @staticmethod
    def _first_present_value(
        data: dict[str, Any],
        keys: tuple[str, ...],
        *,
        default: Any,
    ) -> Any:
        """
        Return the first meaningful value for the supplied keys.

        Empty values include:

            None
            ""
            empty list
            empty dict
            empty tuple
            empty set

        This implementation intentionally avoids expressions
        such as:

            value == []

        because pandas/numpy objects can return array-like
        boolean results from such comparisons.
        """

        for key in keys:
            if key not in data:
                continue

            value = data.get(key)

            if value is None:
                continue

            if isinstance(value, str):
                if not value.strip():
                    continue

                return value

            if isinstance(
                value,
                (list, tuple, dict, set),
            ):
                if len(value) == 0:
                    continue

                return value

            return value

        return default

    # =========================================================
    # Sources
    # =========================================================

    @staticmethod
    def _normalize_sources(
        sources: Any,
    ) -> list[Any]:
        """
        Normalize source information into a unique list.
        """

        if sources is None:
            return []

        if isinstance(
            sources,
            (list, tuple, set),
        ):
            values = list(sources)

        else:
            values = [
                sources
            ]

        normalized: list[Any] = []

        for source in values:
            if source is None:
                continue

            #
            # Source values should normally be strings, URLs,
            # or small provider metadata objects. Sanitize them
            # before attempting deduplication.
            #

            source = FinancialResearchService._sanitize_value(
                source
            )

            #
            # Avoid equality operations against complex numpy/
            # pandas objects.
            #

            duplicate = False

            for existing in normalized:
                try:
                    equality = source == existing

                    if isinstance(
                        equality,
                        (bool, np.bool_),
                    ):
                        if bool(equality):
                            duplicate = True
                            break

                except Exception:
                    continue

            if not duplicate:
                normalized.append(source)

        return normalized