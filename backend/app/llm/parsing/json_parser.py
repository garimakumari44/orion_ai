"""
Robust JSON parsing utilities for LLM outputs.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class JSONParser:
    """
    Handles messy JSON returned by LLMs.

    Features
    --------
    - Removes markdown code blocks
    - Extracts JSON from surrounding text
    - Safe parsing
    - Pretty serialization
    """

    JSON_PATTERN = re.compile(r"\{.*\}|\[.*\]", re.DOTALL)

    @staticmethod
    def clean(text: str) -> str:
        """
        Remove markdown wrappers and whitespace.
        """

        text = text.strip()

        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*", "", text)
            text = text.replace("```", "")

        return text.strip()

    @classmethod
    def extract_json(cls, text: str) -> str:
        """
        Extract first JSON object or array.
        """

        text = cls.clean(text)

        match = cls.JSON_PATTERN.search(text)

        if not match:
            raise ValueError("No JSON found.")

        return match.group(0)

    @classmethod
    def loads(cls, text: str) -> Any:
        """
        Parse JSON safely.
        """

        try:
            raw = cls.extract_json(text)
            return json.loads(raw)

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON: %s", e)
            raise

    @staticmethod
    def dumps(
        obj: Any,
        *,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> str:
        """
        Serialize object to JSON.
        """

        return json.dumps(
            obj,
            indent=indent,
            ensure_ascii=ensure_ascii,
        )

    @classmethod
    def is_valid(cls, text: str) -> bool:
        """
        Check if valid JSON exists.
        """

        try:
            cls.loads(text)
            return True

        except Exception:
            return False