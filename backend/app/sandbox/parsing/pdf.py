from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any
import io

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


@dataclass
class ParseResult:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class PDFParser:
    """
    Extract text from PDF files.
    """

    def parse(self, file_path: str | Path) -> ParseResult:
        if PdfReader is None:
            raise ImportError("Install pypdf")

        path = Path(file_path)

        reader = PdfReader(str(path))

        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        text = "\n".join(pages)

        metadata = {
            "pages": len(reader.pages),
            "encrypted": reader.is_encrypted,
        }

        return ParseResult(text=text, metadata=metadata)

    def parse_bytes(self, data: bytes) -> ParseResult:
        if PdfReader is None:
            raise ImportError("Install pypdf")

        reader = PdfReader(io.BytesIO(data))

        pages = [p.extract_text() or "" for p in reader.pages]

        return ParseResult(
            text="\n".join(pages),
            metadata={"pages": len(reader.pages)},
        )