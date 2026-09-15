"""
Content moderation layer.

Checks prompts and responses for unsafe content before
they reach the language model.

Provider independent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import List


class ModerationAction(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"


@dataclass
class ModerationResult:
    allowed: bool
    action: ModerationAction
    categories: List[str]
    reason: str = ""


class ModerationGuard:
    """
    Lightweight rule-based moderation.

    Can later be replaced with:
        - OpenAI Moderation API
        - Azure AI Content Safety
        - Perspective API
        - Llama Guard
    """

    HATE_PATTERNS = [
        r"\bkill all\b",
        r"\bexterminate\b",
        r"\bethnic cleansing\b",
    ]

    SELF_HARM = [
        r"\bsuicide\b",
        r"\bhow to kill myself\b",
        r"\bself harm\b",
    ]

    VIOLENCE = [
        r"\bbuild a bomb\b",
        r"\bmake explosives\b",
        r"\bmurder\b",
    ]

    SEXUAL = [
        r"\bchild porn\b",
        r"\bexplicit sexual\b",
    ]

    def __init__(self):
        self.patterns = {
            "hate": self.HATE_PATTERNS,
            "self_harm": self.SELF_HARM,
            "violence": self.VIOLENCE,
            "sexual": self.SEXUAL,
        }

    def moderate(self, text: str) -> ModerationResult:
        """
        Moderate user input.

        Returns
        -------
        ModerationResult
        """

        lowered = text.lower()
        categories = []

        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, lowered):
                    categories.append(category)
                    break

        if categories:
            return ModerationResult(
                allowed=False,
                action=ModerationAction.BLOCK,
                categories=categories,
                reason="Unsafe content detected.",
            )

        return ModerationResult(
            allowed=True,
            action=ModerationAction.ALLOW,
            categories=[],
        )