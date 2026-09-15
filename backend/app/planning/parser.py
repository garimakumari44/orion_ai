from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from app.llm.manager import LLMManager
from app.planning.intent import IntentClassifier
from app.planning.models.planning_request import PlanningRequest

logger = logging.getLogger(__name__)


class PlanningParser:
    """
    Converts raw user input into PlanningRequest.

    Responsibilities:
    - Normalize query
    - Detect intent
    - Extract entities
    - Extract constraints
    - Attach metadata

    Does NOT:
    - Create tasks
    - Build DAG
    - Execute tools

    Entity extraction is intentionally fail-safe:
    LLM extraction is attempted first, but deterministic rule-based
    extraction is always available as a fallback.
    """

    def __init__(
        self,
        llm_manager: Optional[LLMManager] = None,
    ) -> None:
        if llm_manager is None:
            raise ValueError(
                "PlanningParser requires an LLMManager."
            )

        self.llm_manager = llm_manager

        self.intent_classifier = IntentClassifier(
            self.llm_manager
        )

    # ======================================================================
    # ENTRY POINT
    # ======================================================================

    def parse(
        self,
        query: str,
    ) -> PlanningRequest:

        if not isinstance(query, str):
            raise TypeError(
                "query must be a string."
            )

        normalized = self._normalize(query)

        if not normalized:
            raise ValueError(
                "query cannot be empty."
            )

        # --------------------------------------------------------------
        # Intent
        # --------------------------------------------------------------

        try:
            intent = self.intent_classifier.classify(
                normalized
            )
        except Exception:
            logger.exception(
                "Intent classification failed; using default intent."
            )

            intent = "research"

        # --------------------------------------------------------------
        # Entities
        # --------------------------------------------------------------

        entities = self._extract_entities(
            normalized
        )

        # --------------------------------------------------------------
        # Constraints
        # --------------------------------------------------------------

        constraints = self._extract_constraints(
            normalized
        )

        return PlanningRequest(
            query=query,
            intent=intent,
            entities=entities,
            constraints=constraints,
            context={},
            metadata={
                "normalized_query": normalized,
                "parser": "planning_parser_v4",
                "entity_source": (
                    "llm_with_rule_based_fallback"
                ),
                "domain": "equity_research",
            },
        )

    # ======================================================================
    # ENTITY EXTRACTION
    # ======================================================================

    def _extract_entities(
        self,
        query: str,
    ) -> list[str]:

        prompt = self._build_entity_prompt(
            query
        )

        try:
            # ----------------------------------------------------------
            # IMPORTANT:
            #
            # The LLM layer must receive a non-empty prompt.
            # We deliberately do not call generate with an empty
            # messages list.
            # ----------------------------------------------------------

            response = self.llm_manager.generate(
                prompt
            )

            entities = self._normalize_llm_response(
                response
            )

            extracted = self._extract_entity_values(
                entities
            )

            if extracted:
                logger.debug(
                    "LLM entity extraction succeeded | entities=%s",
                    extracted,
                )

                return extracted

            logger.warning(
                "LLM entity extraction returned no entities; "
                "using rule-based fallback."
            )

        except Exception as exc:
            logger.warning(
                "LLM entity extraction failed: %s. "
                "Using rule-based fallback.",
                exc,
            )

        # --------------------------------------------------------------
        # Deterministic fallback
        # --------------------------------------------------------------

        fallback = self._extract_entities_rule_based(
            query
        )

        if fallback:
            logger.info(
                "Rule-based entity extraction succeeded | entities=%s",
                fallback,
            )

        else:
            logger.warning(
                "Rule-based entity extraction also returned no entities."
            )

        return fallback

    # ======================================================================
    # ENTITY PROMPT
    # ======================================================================

    @staticmethod
    def _build_entity_prompt(
        query: str,
    ) -> str:

        return f"""
You are an entity extraction system for an equity research platform.

Extract the important research entities from the user's request.

Possible entity types:

- company names
- stock tickers
- industries
- sectors
- countries
- investment themes
- financial instruments

Rules:

1. Return ONLY valid JSON.
2. Do not use Markdown.
3. Do not include explanations.
4. Do not invent entities.
5. Preserve company names exactly when possible.
6. Preserve stock tickers exactly.
7. If a field has no value, use null.
8. The "entities" field must contain the important extracted entities.

Return exactly this structure:

{{
    "company": null,
    "ticker": null,
    "industry": null,
    "sector": null,
    "country": null,
    "theme": null,
    "entities": []
}}

User request:

{query}
""".strip()

    # ======================================================================
    # NORMALIZE LLM RESPONSE
    # ======================================================================

    def _normalize_llm_response(
        self,
        response: Any,
    ) -> Any:

        if response is None:
            raise ValueError(
                "LLM returned None."
            )

        # --------------------------------------------------------------
        # Direct dictionary/list response
        # --------------------------------------------------------------

        if isinstance(response, (dict, list)):
            return response

        # --------------------------------------------------------------
        # String response
        # --------------------------------------------------------------

        if isinstance(response, str):

            response = response.strip()

            if not response:
                raise ValueError(
                    "LLM returned an empty string."
                )

            return self._parse_json_response(
                response
            )

        # --------------------------------------------------------------
        # Common response-object patterns
        # --------------------------------------------------------------

        for attribute in (
            "content",
            "text",
            "output",
            "response",
        ):

            value = getattr(
                response,
                attribute,
                None,
            )

            if value is None:
                continue

            if isinstance(value, str):

                return self._parse_json_response(
                    value
                )

            if isinstance(value, (dict, list)):
                return value

        raise ValueError(
            "Unsupported LLM response type: "
            f"{type(response).__name__}"
        )

    # ======================================================================
    # EXTRACT ENTITY VALUES
    # ======================================================================

    def _extract_entity_values(
        self,
        entities: Any,
    ) -> list[str]:

        extracted: list[str] = []

        if isinstance(
            entities,
            dict,
        ):

            # ----------------------------------------------------------
            # Preferred schema fields
            # ----------------------------------------------------------

            preferred_fields = (
                "company",
                "ticker",
                "industry",
                "sector",
                "country",
                "theme",
                "entities",
            )

            for field in preferred_fields:

                value = entities.get(
                    field
                )

                self._append_entity_value(
                    extracted,
                    value,
                )

        elif isinstance(
            entities,
            list,
        ):

            for value in entities:

                self._append_entity_value(
                    extracted,
                    value,
                )

        return self._deduplicate_entities(
            extracted
        )

    # ======================================================================
    # APPEND ENTITY
    # ======================================================================

    def _append_entity_value(
        self,
        output: list[str],
        value: Any,
    ) -> None:

        if value is None:
            return

        if isinstance(
            value,
            str,
        ):

            cleaned = self._clean_entity(
                value
            )

            if cleaned:
                output.append(
                    cleaned
                )

            return

        if isinstance(
            value,
            (list, tuple, set),
        ):

            for item in value:

                self._append_entity_value(
                    output,
                    item,
                )

            return

        if isinstance(
            value,
            dict,
        ):

            # Support structures such as:
            #
            # {
            #   "name": "Dell",
            #   "type": "company"
            # }

            for key in (
                "name",
                "value",
                "entity",
                "text",
            ):

                if key in value:

                    self._append_entity_value(
                        output,
                        value[key],
                    )

                    return

    # ======================================================================
    # SAFE JSON PARSER
    # ======================================================================

    def _parse_json_response(
        self,
        response: str,
    ) -> dict[str, Any] | list[Any]:

        text = response.strip()

        if not text:
            raise ValueError(
                "Empty JSON response."
            )

        # --------------------------------------------------------------
        # Remove Markdown code fences
        # --------------------------------------------------------------

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

        text = text.strip()

        # --------------------------------------------------------------
        # Direct JSON
        # --------------------------------------------------------------

        try:

            parsed = json.loads(
                text
            )

            if isinstance(
                parsed,
                (dict, list),
            ):
                return parsed

        except json.JSONDecodeError:
            pass

        # --------------------------------------------------------------
        # Extract JSON object
        # --------------------------------------------------------------

        object_match = re.search(
            r"\{[\s\S]*\}",
            text,
        )

        if object_match:

            candidate = (
                object_match.group()
                .strip()
            )

            try:

                parsed = json.loads(
                    candidate
                )

                if isinstance(
                    parsed,
                    dict,
                ):
                    return parsed

            except json.JSONDecodeError:
                pass

        # --------------------------------------------------------------
        # Extract JSON array
        # --------------------------------------------------------------

        array_match = re.search(
            r"\[[\s\S]*\]",
            text,
        )

        if array_match:

            candidate = (
                array_match.group()
                .strip()
            )

            try:

                parsed = json.loads(
                    candidate
                )

                if isinstance(
                    parsed,
                    list,
                ):
                    return parsed

            except json.JSONDecodeError:
                pass

        raise ValueError(
            "Invalid JSON response: "
            f"{text[:500]}"
        )

    # ======================================================================
    # RULE-BASED ENTITY EXTRACTION
    # ======================================================================

    def _extract_entities_rule_based(
        self,
        text: str,
    ) -> list[str]:

        entities: list[str] = []

        # --------------------------------------------------------------
        # Common stock ticker patterns
        # --------------------------------------------------------------

        ticker_matches = re.findall(
            r"\b[A-Z]{1,5}(?:\.[A-Z]{1,3})?\b",
            text,
        )

        ignored_tickers = {
            "I",
            "A",
            "AN",
            "THE",
            "AND",
            "OR",
            "FOR",
            "WITH",
            "FROM",
            "IN",
            "ON",
            "OF",
            "TO",
            "IS",
            "ARE",
            "AS",
            "BY",
            "AT",
            "BE",
            "US",
            "USD",
            "AI",
            "API",
            "SEC",
            "GDP",
            "CEO",
            "CFO",
            "Q1",
            "Q2",
            "Q3",
            "Q4",
        }

        for ticker in ticker_matches:

            if ticker not in ignored_tickers:

                entities.append(
                    ticker
                )

        # --------------------------------------------------------------
        # Known research phrases
        # --------------------------------------------------------------

        phrase_patterns = [
            r"\b[A-Z][A-Za-z0-9&.-]*(?:\s+[A-Z][A-Za-z0-9&.-]*){1,5}\b",
        ]

        for pattern in phrase_patterns:

            matches = re.findall(
                pattern,
                text,
            )

            for match in matches:

                cleaned = (
                    match.strip(
                        ",.!?;:()[]{}\"'"
                    )
                )

                if not cleaned:
                    continue

                if cleaned in {
                    "Analyze",
                    "Compare",
                    "Give",
                    "Show",
                    "Latest",
                    "What",
                    "How",
                    "The",
                    "Tell",
                    "Find",
                    "Research",
                    "Explain",
                    "Please",
                }:
                    continue

                entities.append(
                    cleaned
                )

        # --------------------------------------------------------------
        # Single capitalized words
        # --------------------------------------------------------------

        ignored_words = {
            "Analyze",
            "Compare",
            "Give",
            "Show",
            "Latest",
            "What",
            "How",
            "The",
            "Tell",
            "Find",
            "Research",
            "Explain",
            "Please",
            "Can",
            "Could",
            "Would",
            "Should",
            "Does",
            "Do",
            "Is",
            "Are",
            "And",
            "Or",
            "For",
            "With",
            "From",
        }

        for word in text.split():

            cleaned = word.strip(
                ",.!?;:()[]{}\"'"
            )

            if not cleaned:
                continue

            if cleaned in ignored_words:
                continue

            if (
                len(cleaned) > 1
                and cleaned[0].isupper()
            ):

                entities.append(
                    cleaned
                )

        return self._deduplicate_entities(
            entities
        )

    # ======================================================================
    # ENTITY CLEANING
    # ======================================================================

    @staticmethod
    def _clean_entity(
        value: str,
    ) -> str:

        value = value.strip()

        value = value.strip(
            ",.!?;:()[]{}\"'"
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value

    # ======================================================================
    # ENTITY DEDUPLICATION
    # ======================================================================

    @staticmethod
    def _deduplicate_entities(
        entities: list[str],
    ) -> list[str]:

        result: list[str] = []

        seen: set[str] = set()

        for entity in entities:

            cleaned = entity.strip()

            if not cleaned:
                continue

            key = cleaned.casefold()

            if key in seen:
                continue

            seen.add(key)

            result.append(
                cleaned
            )

        return result

    # ======================================================================
    # NORMALIZATION
    # ======================================================================

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ======================================================================
    # CONSTRAINT EXTRACTION
    # ======================================================================

    @staticmethod
    def _extract_constraints(
        text: str,
    ) -> list[str]:

        checks = {
            "latest": "latest",
            "today": "latest",
            "recent": "latest",

            "quarterly": "quarterly",

            "annual": "annual",
            "yearly": "annual",

            "historical": "historical",

            "10-k": "sec_filings",
            "10q": "sec_filings",
            "10-q": "sec_filings",

            "earnings": "earnings",

            "valuation": "valuation",

            "comparison": "comparison",
            "compare": "comparison",

            "macro": "macro",

            "risk": "risk",

            "fundamental": "fundamental",

            "technical": "technical",

            "dividend": "dividend",

            "forecast": "forecast",
            "projection": "forecast",
        }

        lowered = text.lower()

        constraints = [
            value
            for key, value in checks.items()
            if key in lowered
        ]

        return list(
            dict.fromkeys(
                constraints
            )
        )

    # ======================================================================
    # DEBUG REPRESENTATION
    # ======================================================================

    def __repr__(self) -> str:

        return (
            "PlanningParser("
            "llm_manager="
            f"{self.llm_manager!r}"
            ")"
        )