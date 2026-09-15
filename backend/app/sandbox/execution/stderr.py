"""
Utilities for capturing stderr during code execution.
"""

from __future__ import annotations

import io
import sys
from contextlib import contextmanager
from typing import Generator


class StderrCapture:
    """
    Captures everything written to sys.stderr.

    Example:
        capture = StderrCapture()

        with capture:
            raise Exception("Oops")
    """

    def __init__(self) -> None:
        self._buffer = io.StringIO()
        self._original = None
        self.output: str = ""

    def __enter__(self) -> "StderrCapture":
        self._original = sys.stderr
        sys.stderr = self._buffer
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.output = self._buffer.getvalue()
        sys.stderr = self._original
        self._buffer.close()

    def clear(self) -> None:
        self.output = ""
        self._buffer = io.StringIO()

    @property
    def text(self) -> str:
        return self.output


@contextmanager
def capture_stderr() -> Generator[StderrCapture, None, None]:
    """
    Context manager for capturing stderr.

    Example:
        with capture_stderr() as cap:
            print("error", file=sys.stderr)

        print(cap.output)
    """
    cap = StderrCapture()
    with cap:
        yield cap