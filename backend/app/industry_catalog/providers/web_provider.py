"""
app/industry_catalog/providers/web_provider.py

Web-based industry metadata provider.

Responsibilities:
- discover industry information from web search results
- extract candidate industry metadata
- provide external evidence for industry classification

This provider is an enrichment/discovery provider.

It does NOT:
- perform deep industry research
- write to the database
- run research agents
- decide the final canonical industry
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from .base import IndustryProvider

logger = logging.getLogger(__name__)


class WebIndustryProvider(IndustryProvider):
    """
    Web-based industry metadata provider.

    A search adapter can be injected.

    Expected adapter contract:

        search(query, limit=10)

    It may return:

        [
            {
                "title": "...",
                "url": "...",
                "snippet": "..."
            }
        ]

    or:

        {
            "results": [...]
        }
    """

    name = "web"
    priority = 80

    def __init__(
        self,
        search_provider: Optional[Any] = None,
        *,
        enabled: bool = True,
    ) -> None:
        super().__init__()

        self.enabled = enabled
        self.search_provider = search_provider

    # ========================================================================
    # Search
    # ========================================================================

    def search_industry(
        self,
        query: str,
        *,
        limit: int = 20,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Search the web for industry metadata.

        The web provider returns candidate metadata rather than claiming
        that the discovered classification is authoritative.
        """

        if not query or not query.strip():
            return []

        if self.search_provider is None:
            logger.warning(
                "WebIndustryProvider has no search provider configured"
            )
            return []

        search_query = self._build_query(query)

        try:
            raw_results = self._execute_search(
                search_query,
                limit=limit,
            )

        except Exception:
            logger.exception(
                "Web industry search failed for query '%s'",
                query,
            )
            return []

        return self._normalize_search_results(
            raw_results,
            query=query,
            limit=limit,
        )

    # ========================================================================
    # Lookup
    # ========================================================================

    def get_industry(
        self,
        industry: str,
        
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Search the web for a specific industry.
        """

        results = self.search_industry(
            industry,
            limit=5,
            **kwargs,
        )

        if not results:
            return None

        return results[0]

    # ========================================================================
    # Company classification
    # ========================================================================

    def classify_company(
        self,
        company: Optional[str] = None,
        *,
        ticker: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Discover industry metadata for a company from web sources.

        The result is explicitly marked as web-derived and should be
        treated as lower-confidence evidence than authoritative
        classification sources.
        """

        if not company and not ticker:
            return None

        identity = company or ticker

        query = (
            f'"{identity}" company industry sector '
            f'classification'
        )

        results = self.search_industry(
            query,
            limit=10,
            **kwargs,
        )

        if not results:
            return None

        result = dict(results[0])

        result["company"] = company
        result["ticker"] = ticker
        result["source"] = "web"
        result["classification"] = "Web-derived"
        result["classification_system"] = "Web"

        # Web discovery should not outrank formal classifications.
        result["confidence"] = min(
            float(result.get("confidence", 0.40)),
            0.40,
        )

        return result

    # ========================================================================
    # Taxonomy
    # ========================================================================

    def get_taxonomy(
        self,
        *,
        taxonomy: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Web search is not treated as an authoritative taxonomy.
        """

        return []

    # ========================================================================
    # Health
    # ========================================================================

    def health_check(self) -> bool:
        return (
            self.enabled
            and self.search_provider is not None
        )

    # ========================================================================
    # Search adapter
    # ========================================================================

    def _execute_search(
        self,
        query: str,
        *,
        limit: int,
    ) -> Any:
        """
        Execute the injected search adapter.

        Supports several common adapter shapes.
        """

        provider = self.search_provider

        if hasattr(provider, "search"):
            return provider.search(
                query,
                limit=limit,
            )

        if hasattr(provider, "execute"):
            return provider.execute(
                query=query,
                limit=limit,
            )

        if callable(provider):
            return provider(
                query=query,
                limit=limit,
            )

        raise TypeError(
            "search_provider must expose search(), execute(), "
            "or be callable"
        )

    # ========================================================================
    # Query construction
    # ========================================================================

    @staticmethod
    def _build_query(query: str) -> str:
        """
        Build a focused industry metadata query.
        """

        return (
            f'"{query}" '
            f'industry sector sub-industry classification'
        )

    # ========================================================================
    # Result normalization
    # ========================================================================

    def _normalize_search_results(
        self,
        raw_results: Any,
        *,
        query: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """
        Normalize arbitrary search adapter output.
        """

        if raw_results is None:
            return []

        if isinstance(raw_results, dict):
            raw_results = (
                raw_results.get("results")
                or raw_results.get("items")
                or raw_results.get("data")
                or []
            )

        if not isinstance(raw_results, list):
            return []

        results: List[Dict[str, Any]] = []

        for item in raw_results:
            if not isinstance(item, dict):
                continue

            normalized = self._normalize_search_result(
                item,
                query=query,
            )

            if normalized:
                results.append(normalized)

            if len(results) >= limit:
                break

        return results

    @staticmethod
    def _normalize_search_result(
        item: Dict[str, Any],
        *,
        query: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Convert a search result into an industry evidence object.
        """

        title = (
            item.get("title")
            or item.get("name")
            or ""
        )

        url = (
            item.get("url")
            or item.get("link")
            or ""
        )

        snippet = (
            item.get("snippet")
            or item.get("description")
            or item.get("text")
            or ""
        )

        if not title and not snippet:
            return None

        combined_text = (
            f"{title} {snippet}"
        ).strip()

        extracted = WebIndustryProvider._extract_industry(
            combined_text
        )

        result: Dict[str, Any] = {
            "industry": extracted,
            "sub_industry": None,
            "sector": None,

            "classification": "Web-derived",
            "classification_system": "Web",
            "source": "web",

            "query": query,
            "title": title,
            "url": url,
            "snippet": snippet,

            "confidence": 0.35,
        }

        return result

    # ========================================================================
    # Basic extraction
    # ========================================================================

    @staticmethod
    def _extract_industry(
        text: str,
    ) -> Optional[str]:
        """
        Perform lightweight extraction of industry wording.

        This is deliberately conservative.

        It is NOT an LLM classifier.
        """

        if not text:
            return None

        patterns = [
            r"industry\s*[:\-]\s*([^.;,\n]+)",
            r"sector\s*[:\-]\s*([^.;,\n]+)",
            r"operates in the\s+([^.;,\n]+)\s+industry",
            r"company operates in\s+([^.;,\n]+)",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                value = match.group(1).strip()

                if value:
                    return value

        return None