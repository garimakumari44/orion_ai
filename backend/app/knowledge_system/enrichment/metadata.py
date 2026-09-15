"""
Metadata extraction.

This module enriches documents with structured metadata that can
later improve retrieval, filtering, ranking, and analytics.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Metadata:
    title: str | None = None
    source: str | None = None
    author: str | None = None
    language: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    file_type: str | None = None
    tags: list[str] | None = None
    extra: dict[str, Any] | None = None


class MetadataExtractor:
    """
    Extracts metadata from a document.
    """

    def extract(
        self,
        text: str,
        *,
        source: str | None = None,
    ) -> Metadata:

        path = Path(source) if source else None

        return Metadata(
            title=self._guess_title(text),
            source=source,
            file_type=path.suffix if path else None,
            language="unknown",
            tags=[],
            extra={},
        )

    @staticmethod
    def _guess_title(text: str) -> str | None:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return None

        return lines[0]