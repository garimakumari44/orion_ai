"""
Artifact management.

Tracks files generated during sandbox execution.
"""

from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Artifact:
    """Represents a generated file."""

    name: str
    path: Path
    mime_type: str
    size: int

    @classmethod
    def from_path(cls, path: str | Path) -> "Artifact":
        p = Path(path)

        mime, _ = mimetypes.guess_type(str(p))

        return cls(
            name=p.name,
            path=p.resolve(),
            mime_type=mime or "application/octet-stream",
            size=p.stat().st_size if p.exists() else 0,
        )


class ArtifactManager:
    """
    Stores execution artifacts.
    """

    def __init__(self):
        self._artifacts: list[Artifact] = []

    def add(self, path: str | Path) -> Artifact:
        artifact = Artifact.from_path(path)
        self._artifacts.append(artifact)
        return artifact

    def remove(self, name: str) -> None:
        self._artifacts = [
            a for a in self._artifacts
            if a.name != name
        ]

    def clear(self) -> None:
        self._artifacts.clear()

    def all(self) -> list[Artifact]:
        return list(self._artifacts)

    def exists(self, name: str) -> bool:
        return any(a.name == name for a in self._artifacts)

    def __len__(self):
        return len(self._artifacts)

    def __iter__(self):
        return iter(self._artifacts)