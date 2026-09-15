from dataclasses import dataclass, field
from pathlib import Path
from collections import Counter
from typing import Dict, Any
import re


@dataclass
class ParseResult:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class LogParser:
    """
    Analyze application log files.
    """

    LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def parse(self, file_path: str | Path) -> ParseResult:
        text = Path(file_path).read_text(encoding="utf-8")

        counter = Counter()

        for level in self.LEVELS:
            counter[level] = len(re.findall(level, text))

        metadata = {
            "lines": len(text.splitlines()),
            "levels": dict(counter),
        }

        return ParseResult(
            text=text,
            metadata=metadata,
        )