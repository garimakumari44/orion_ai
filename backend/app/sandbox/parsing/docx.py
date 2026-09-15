from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any

try:
    from docx import Document
except ImportError:
    Document = None


@dataclass
class ParseResult:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class DOCXParser:
    """
    Parse Microsoft Word documents.
    """

    def parse(self, file_path: str | Path) -> ParseResult:
        if Document is None:
            raise ImportError("Install python-docx")

        doc = Document(file_path)

        paragraphs = [p.text for p in doc.paragraphs]

        return ParseResult(
            text="\n".join(paragraphs),
            metadata={
                "paragraphs": len(paragraphs),
            },
        )