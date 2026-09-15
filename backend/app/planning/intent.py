from __future__ import annotations

import logging
from typing import Optional

from app.llm.manager import LLMManager


logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Hybrid intent classifier.

    Strategy
    --------
    1. Fast rule-based detection.
    2. Canonical LLMManager fallback for ambiguous queries.

    The classifier NEVER constructs an LLM provider or LLMService.
    """

    INTENT_KEYWORDS = {
        "company_research": [
            "research",
            "analyze",
            "analysis",
            "company",
            "business",
            "stock",
            "profile",
            "fundamentals",
            "overview",
        ],
        "company_comparison": [
            "compare",
            "comparison",
            "vs",
            "versus",
            "better than",
            "peer",
            "relative",
        ],
        "industry_research": [
            "industry",
            "sector",
            "market",
            "competitive landscape",
            "competition",
            "tam",
            "sam",
            "som",
            "porter",
        ],
        "earnings_analysis": [
            "earnings",
            "quarterly",
            "annual report",
            "10-k",
            "10-q",
            "results",
            "guidance",
            "conference call",
            "transcript",
        ],
        "valuation_analysis": [
            "valuation",
            "dcf",
            "discounted cash flow",
            "price target",
            "multiple",
            "ev/ebitda",
            "ev/sales",
            "pe ratio",
            "p/e",
        ],
        "risk_analysis": [
            "risk",
            "risks",
            "bear case",
            "downside",
            "scenario",
            "sensitivity",
        ],
        "macro_research": [
            "macro",
            "economy",
            "inflation",
            "interest rates",
            "fed",
            "central bank",
            "gdp",
            "recession",
        ],
        "portfolio_research": [
            "portfolio",
            "holdings",
            "allocation",
            "rebalance",
            "diversification",
            "watchlist",
        ],
        "theme_research": [
            "theme",
            "megatrend",
            "artificial intelligence",
            "ai",
            "semiconductors",
            "cloud",
            "cybersecurity",
            "renewable energy",
            "electric vehicles",
            "fintech",
        ],
    }

    VALID_INTENTS = {
        "company_research",
        "company_comparison",
        "industry_research",
        "earnings_analysis",
        "valuation_analysis",
        "risk_analysis",
        "macro_research",
        "portfolio_research",
        "theme_research",
        "general",
    }

    def __init__(
        self,
        llm_manager: Optional[LLMManager] = None,
    ) -> None:
        """
        Initialize the classifier.

        An LLMManager is optional because the fast rule-based
        path does not require an LLM. It is required only when
        the classifier reaches the ambiguous-query fallback.
        """

        self.llm_manager = llm_manager

    # ==================================================================
    # PUBLIC API
    # ==================================================================

    def classify(self, text: str) -> str:
        """
        Classify user intent.
        """

        if text is None:
            return "general"

        normalized = str(text).lower().strip()

        if not normalized:
            return "general"

        # --------------------------------------------------------------
        # Rule-based fast path
        # --------------------------------------------------------------

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in normalized:
                    logger.debug(
                        "Intent classified by rule | intent=%s",
                        intent,
                    )
                    return intent

        # --------------------------------------------------------------
        # Canonical LLM fallback
        # --------------------------------------------------------------

        if self.llm_manager is None:
            logger.debug(
                "No LLMManager available for intent fallback"
            )
            return "general"

        return self._llm_classify(normalized)

    # ==================================================================
    # LLM CLASSIFICATION
    # ==================================================================

    def _llm_classify(self, query: str) -> str:
        """
        Classify an ambiguous query using LLMManager.

        IMPORTANT:
        This method does not call LLMService directly.
        """

        prompt = f"""
You are the intent classifier for an enterprise AI research system.

Classify the user query into exactly ONE of these intents:

- company_research
- company_comparison
- industry_research
- earnings_analysis
- valuation_analysis
- risk_analysis
- macro_research
- portfolio_research
- theme_research
- general

Rules:
- Return ONLY the intent name.
- Do not return JSON.
- Do not provide an explanation.
- Do not use markdown.
- Choose the closest matching intent.
- If none clearly applies, return general.

Query:
{query}
""".strip()

        try:
            response = self.llm_manager.generate(
                prompt=prompt,
                task="intent_classification",
                temperature=0.0,
                max_tokens=32,
            )

            if response is None:
                return "general"

            result = str(response).strip().lower()

            # Remove accidental surrounding quotes.
            result = result.strip("\"'")

            if result in self.VALID_INTENTS:
                return result

            logger.warning(
                "LLM returned unsupported intent | response=%s",
                result,
            )

        except Exception:
            logger.exception(
                "LLM intent classification failed"
            )

        return "general"
