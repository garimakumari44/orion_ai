"""
Execution environment management.
"""

from __future__ import annotations

import os
import shutil
import sys
import venv
from pathlib import Path
from typing import Dict


class ExecutionEnvironment:
    """
    Represents an isolated execution environment.

    Currently supports Python virtual environments.
    """

    def __init__(
        self,
        workspace: Path,
        create_venv: bool = True,
        venv_name: str = ".venv",
    ):
        self.workspace = Path(workspace)
        self.venv_path = self.workspace / venv_name

        if create_venv:
            self.create()

    @property
    def exists(self) -> bool:
        return self.venv_path.exists()

    def create(self) -> None:
        """
        Create a Python virtual environment.
        """

        if self.exists:
            return

        builder = venv.EnvBuilder(
            with_pip=True,
            clear=False,
            upgrade=False,
        )

        builder.create(self.venv_path)

    @property
    def python(self) -> Path:
        """
        Path to Python executable.
        """

        if os.name == "nt":
            return self.venv_path / "Scripts" / "python.exe"

        return self.venv_path / "bin" / "python"

    @property
    def pip(self) -> Path:
        """
        Path to pip executable.
        """

        if os.name == "nt":
            return self.venv_path / "Scripts" / "pip.exe"

        return self.venv_path / "bin" / "pip"

    def environment_variables(self) -> Dict[str, str]:
        """
        Environment variables for subprocess execution.
        """

        env = os.environ.copy()

        env["VIRTUAL_ENV"] = str(self.venv_path)

        if os.name == "nt":
            scripts = self.venv_path / "Scripts"
        else:
            scripts = self.venv_path / "bin"

        env["PATH"] = f"{scripts}{os.pathsep}{env['PATH']}"

        return env

    def remove(self) -> None:
        """
        Delete the virtual environment.
        """

        shutil.rmtree(self.venv_path, ignore_errors=True)