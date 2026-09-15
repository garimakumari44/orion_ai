from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any
import ast


@dataclass
class ParseResult:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class SourceCodeParser:
    """
    Analyze source code files.

    Currently provides rich parsing for Python and
    basic parsing for other languages.
    """

    def parse(self, file_path: str | Path) -> ParseResult:
        path = Path(file_path)

        source = path.read_text(encoding="utf-8")

        metadata = {
            "language": path.suffix.lstrip("."),
            "lines": len(source.splitlines()),
        }

        if path.suffix == ".py":
            tree = ast.parse(source)

            functions = [
                n.name for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef)
            ]

            classes = [
                n.name for n in ast.walk(tree)
                if isinstance(n, ast.ClassDef)
            ]

            imports = [
                getattr(n, "module", None)
                for n in ast.walk(tree)
                if isinstance(n, ast.ImportFrom)
            ]

            metadata.update({
                "functions": functions,
                "classes": classes,
                "imports": [i for i in imports if i],
            })

        return ParseResult(
            text=source,
            metadata=metadata,
        )