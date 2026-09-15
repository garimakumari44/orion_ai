"""
Entity extraction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

URL_PATTERN = re.compile(
    r"https?://[^\s]+"
)


@dataclass(slots=True)
class Entity:
    text: str
    label: str


class EntityExtractor:
    """
    Extract entities from text.
    """

    def extract(self, text: str) -> list[Entity]:

        entities: list[Entity] = []

        for email in EMAIL_PATTERN.findall(text):
            entities.append(Entity(email, "EMAIL"))

        for url in URL_PATTERN.findall(text):
            entities.append(Entity(url, "URL"))

        return entities