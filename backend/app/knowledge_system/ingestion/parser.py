"""
Parses raw connector output into normalized text.

Examples

PDF
↓

Extract text

Markdown
↓

Plain text

HTML
↓

Visible text

JSON
↓

Pretty serialized text
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .loader import RawDocument


@dataclass(slots=True)
class ParsedDocument:
    """
    Parsed text document.
    """

    id: str
    source: str
    text: str
    metadata: dict


class DocumentParser:
    """
    Converts raw documents into plain text.
    """

    async def parse(self, document: RawDocument) -> ParsedDocument:
        content = document.content

        if isinstance(content, bytes):
            text = content.decode("utf-8", errors="ignore")

        elif isinstance(content, str):
            text = content

        elif isinstance(content, dict):
            text = json.dumps(content, indent=2)

        else:
            text = str(content)

        return ParsedDocument(
            id=document.id,
            source=document.source,
            text=text,
            metadata=document.metadata,
        )