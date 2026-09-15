"""
Text normalization.

This module removes formatting noise while preserving meaning.
"""

from __future__ import annotations

import re

from .parser import ParsedDocument


class TextCleaner:
    """
    Cleans parsed text.
    """

    MULTIPLE_SPACES = re.compile(r"[ \t]+")
    MULTIPLE_LINES = re.compile(r"\n{3,}")

    def clean(self, document: ParsedDocument) -> ParsedDocument:
        text = document.text

        # Normalize line endings
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove trailing spaces
        text = "\n".join(line.strip() for line in text.splitlines())

        # Collapse spaces
        text = self.MULTIPLE_SPACES.sub(" ", text)

        # Collapse blank lines
        text = self.MULTIPLE_LINES.sub("\n\n", text)

        return ParsedDocument(
            id=document.id,
            source=document.source,
            text=text.strip(),
            metadata=document.metadata,
        )