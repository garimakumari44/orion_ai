"""
Sandbox filesystem management.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable


class SandboxFilesystem:
    """
    Handles workspace files for an execution session.
    """

    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)

        self.input_dir = self.workspace / "inputs"
        self.output_dir = self.workspace / "outputs"
        self.temp_dir = self.workspace / "temp"

        self._initialize()

    def _initialize(self):
        """
        Create directory structure.
        """

        self.workspace.mkdir(parents=True, exist_ok=True)

        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)

    def input_path(self, filename: str) -> Path:
        return self.input_dir / filename

    def output_path(self, filename: str) -> Path:
        return self.output_dir / filename

    def temp_path(self, filename: str) -> Path:
        return self.temp_dir / filename

    def write_input(
        self,
        filename: str,
        content: str,
    ) -> Path:
        path = self.input_path(filename)

        path.write_text(
            content,
            encoding="utf-8",
        )

        return path

    def copy_input(
        self,
        source: Path,
    ) -> Path:
        destination = self.input_dir / source.name

        shutil.copy2(source, destination)

        return destination

    def list_outputs(self) -> list[Path]:
        return sorted(
            self.output_dir.glob("*")
        )

    def artifacts(self) -> Iterable[Path]:
        """
        Yield generated artifacts.
        """

        yield from self.output_dir.rglob("*")

    def cleanup(self):
        """
        Remove workspace.
        """

        shutil.rmtree(
            self.workspace,
            ignore_errors=True,
        )