"""
Python execution kernel.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional


class PythonKernel:
    """
    Executes Python code inside a temporary file.

    Example:
        kernel = PythonKernel()

        result = kernel.execute(
            "print('Hello World')",
            timeout=10
        )
    """

    language = "python"

    def execute(
        self,
        code: str,
        working_directory: Optional[str] = None,
        timeout: int = 30,
        environment: Optional[Dict[str, str]] = None,
        python_executable: Optional[str] = None,
    ) -> Dict:
        """
        Execute Python source code.

        Returns:
            Structured execution result.
        """

        python_exec = python_executable or sys.executable

        with tempfile.NamedTemporaryFile(
            suffix=".py",
            delete=False,
            mode="w",
            encoding="utf-8",
        ) as fp:
            fp.write(code)
            script_path = fp.name

        try:
            process = subprocess.run(
                [python_exec, script_path],
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

        finally:
            Path(script_path).unlink(missing_ok=True)