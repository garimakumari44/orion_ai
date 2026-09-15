from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


@dataclass
class ParseResult:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class HTMLParser:
    """
    Extract visible text from HTML.
    """

    def parse(self, file_path: str | Path) -> ParseResult:
        if BeautifulSoup is None:
            raise ImportError("Install beautifulsoup4")

        html = Path(file_path).read_text(encoding="utf-8")

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        title = soup.title.string if soup.title else ""

        return ParseResult(
            text=text,
            metadata={"title": title},
        )