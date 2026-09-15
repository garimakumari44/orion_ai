from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class ProcessingDocument:
    """
    Document flowing through the processing pipeline.
    """

    id: str

    content: str

    source: str = ""
    title: str = ""
    language: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Chunk:
    """
    Atomic retrieval unit.
    """

    id: str

    document_id: str

    text: str

    index: int

    start_char: int = 0
    end_char: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)