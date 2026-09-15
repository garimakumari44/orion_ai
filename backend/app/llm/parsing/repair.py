"""
Repair malformed LLM outputs.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


class OutputRepair:
    """
    Attempts to repair malformed JSON.

    This is intentionally conservative.
    """

    @staticmethod
    def remove_code_blocks(text: str) -> str:
        """
        Remove markdown wrappers.
        """

        text = re.sub(
            r"```[a-zA-Z]*",
            "",
            text,
        )

        return text.replace(
            "```",
            "",
        ).strip()

    @staticmethod
    def remove_trailing_commas(
        text: str,
    ) -> str:
        """
        Remove invalid trailing commas.
        """

        return re.sub(
            r",(\s*[}\]])",
            r"\1",
            text,
        )

    @staticmethod
    def normalize_quotes(
        text: str,
    ) -> str:
        """
        Replace smart quotes.
        """

        return (
            text.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
        )

    @classmethod
    def repair_json(
        cls,
        text: str,
    ) -> str:
        """
        Apply all repair steps.
        """

        text = cls.remove_code_blocks(text)
        text = cls.normalize_quotes(text)
        text = cls.remove_trailing_commas(text)

        return text

    @staticmethod
    def strip_explanation(
        text: str,
    ) -> str:
        """
        Remove explanatory text before JSON.
        """

        start = min(
            [
                idx
                for idx in (
                    text.find("{"),
                    text.find("["),
                )
                if idx != -1
            ],
            default=-1,
        )

        if start == -1:
            return text

        return text[start:]

    @classmethod
    def full_repair(
        cls,
        text: str,
    ) -> str:
        """
        Complete repair pipeline.
        """

        text = cls.strip_explanation(text)
        text = cls.repair_json(text)

        logger.info("Output repaired.")

        return text