"""
Safe subprocess execution for the sandbox runtime.

Features
--------
• Timeout support
• Environment isolation
• Working directory control
• Output capture
• Resource-friendly execution
"""

from __future__ import annotations

import os
import signal
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(slots=True)
class ProcessResult:
    """
    Result returned after executing a subprocess.
    """

    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


class SafeSubprocess:
    """
    Secure wrapper around subprocess.Popen.
    """

    def __init__(
        self,
        timeout: int = 30,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        self.timeout = timeout
        self.cwd = cwd
        self.env = env or {}

    def run(self, command: List[str]) -> ProcessResult:
        """
        Execute a subprocess safely.

        Parameters
        ----------
        command:
            Command list.
        """

        environment = os.environ.copy()
        environment.update(self.env)

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cwd,
            env=environment,
            text=True,
            start_new_session=True,
        )

        timer = threading.Timer(self.timeout, self._terminate, [process])

        try:
            timer.start()

            stdout, stderr = process.communicate()

            timed_out = process.returncode is None

            return ProcessResult(
                command=command,
                returncode=process.returncode or -1,
                stdout=stdout,
                stderr=stderr,
                timed_out=timed_out,
            )

        finally:
            timer.cancel()

    @staticmethod
    def _terminate(process: subprocess.Popen):
        """
        Kill an entire process group.
        """
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except Exception:
            pass