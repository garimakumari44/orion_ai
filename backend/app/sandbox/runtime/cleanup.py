"""
Automatic cleanup utilities.

Responsible for removing temporary files,
destroying sandbox directories,
and terminating remaining processes.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Iterable


class SandboxCleanup:
    """
    Handles cleanup of sandbox resources.
    """

    def remove_directory(self, directory: Path) -> None:
        """
        Delete a sandbox directory recursively.
        """
        if directory.exists():
            shutil.rmtree(directory, ignore_errors=True)

    def remove_files(self, files: Iterable[Path]) -> None:
        """
        Delete a collection of files.
        """
        for file in files:
            try:
                file.unlink(missing_ok=True)
            except Exception:
                pass

    def create_temp_directory(self, prefix: str = "sandbox_") -> Path:
        """
        Create a temporary sandbox workspace.
        """
        return Path(tempfile.mkdtemp(prefix=prefix))

    def cleanup_workspace(self, workspace: Path) -> None:
        """
        Clean an entire workspace.
        """
        self.remove_directory(workspace)

    def __call__(self, workspace: Path):
        """
        Allow object(workspace) syntax.
        """
        self.cleanup_workspace(workspace)