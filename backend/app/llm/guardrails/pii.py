"""
PII Detection & Redaction

Detects and optionally redacts Personally Identifiable Information
before prompts are logged or sent to external providers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class PIIType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    SSN = "ssn"
    API_KEY = "api_key"


@dataclass
class PIIMatch:
    type: PIIType
    value: str
    start: int
    end: int


@dataclass
class PIIResult:
    has_pii: bool
    matches: List[PIIMatch]
    redacted_text: str


class PIIGuard:
    """
    Detects and redacts common PII patterns.
    """

    PATTERNS = {
        PIIType.EMAIL: re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),
        PIIType.PHONE: re.compile(
            r"\b(?:\+?\d{1,3})?[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b"
        ),
        PIIType.CREDIT_CARD: re.compile(
            r"\b(?:\d[ -]*?){13,16}\b"
        ),
        PIIType.IP_ADDRESS: re.compile(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        ),
        PIIType.SSN: re.compile(
            r"\b\d{3}-\d{2}-\d{4}\b"
        ),
        PIIType.API_KEY: re.compile(
            r"\b(?:sk-|AIza|ghp_)[A-Za-z0-9_\-]{10,}\b"
        ),
    }

    def detect(self, text: str) -> PIIResult:
        matches: List[PIIMatch] = []
        redacted = text

        for pii_type, pattern in self.PATTERNS.items():
            for match in pattern.finditer(text):
                matches.append(
                    PIIMatch(
                        type=pii_type,
                        value=match.group(),
                        start=match.start(),
                        end=match.end(),
                    )
                )

        # Redact from longest to shortest index
        for match in sorted(matches, key=lambda m: m.start, reverse=True):
            replacement = f"<{match.type.value.upper()}>"
            redacted = (
                redacted[: match.start]
                + replacement
                + redacted[match.end :]
            )

        return PIIResult(
            has_pii=len(matches) > 0,
            matches=matches,
            redacted_text=redacted,
        )

    def contains_pii(self, text: str) -> bool:
        return self.detect(text).has_pii

    def redact(self, text: str) -> str:
        return self.detect(text).redacted_text

    def summary(self, text: str) -> Dict[str, int]:
        result = self.detect(text)

        counts: Dict[str, int] = {}

        for item in result.matches:
            counts[item.type.value] = counts.get(item.type.value, 0) + 1

        return counts