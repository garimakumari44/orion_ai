from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any
import re


@dataclass
class ParseResult:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class MarkdownParser:
    """
    Parse Markdown into plain text.
    """

    def parse(self, file_path: str | Path) -> ParseResult:
        text = Path(file_path).read_text(encoding="utf-8")

        cleaned = re.sub(r"`{1,3}.*?`{1,3}", "", text, flags=re.S)
        cleaned = re.sub(r"#+ ", "", cleaned)

        return ParseResult(
            text=cleaned,
            metadata={
                "lines": len(cleaned.splitlines())
            },
        )