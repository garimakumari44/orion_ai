"""
Bash / shell execution kernel.
"""

from __future__ import annotations

import os
import subprocess
from typing import Dict, Optional


class BashKernel:
    """
    Executes shell commands.

    On Linux/macOS:
        Uses /bin/bash

    On Windows:
        Uses cmd.exe
    """

    language = "bash"

    def execute(
        self,
        command: str,
        working_directory: Optional[str] = None,
        timeout: int = 30,
        environment: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """
        Execute a shell command.
        """

        if os.name == "nt":
            cmd = ["cmd", "/c", command]
        else:
            cmd = ["/bin/bash", "-c", command]

        try:
            process = subprocess.run(
                cmd,
                cwd=working_directory,
                env=environment,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "language": self.language,
            }

        except subprocess.TimeoutExpired as exc:
            return {
                "success": False,
                "returncode": -1,
                "stdout": exc.stdout or "",
                "stderr": "Execution timed out.",
                "language": self.language,
            }