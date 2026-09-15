from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ParseResult:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class RepositoryParser:
    """
    Scan a source repository.
    """

    IGNORE = {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "dist",
        "build",
    }

    def parse(self, repo_path: str | Path) -> ParseResult:
        repo = Path(repo_path)

        files = []

        for path in repo.rglob("*"):
            if any(part in self.IGNORE for part in path.parts):
                continue

            if path.is_file():
                files.append(str(path.relative_to(repo)))

        return ParseResult(
            text="\n".join(files),
            metadata={
                "files": len(files),
            },
        )