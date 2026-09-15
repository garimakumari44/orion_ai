"""
Utilities for capturing stdout during code execution.
"""

from __future__ import annotations

import io
import sys
from contextlib import contextmanager
from typing import Generator


class StdoutCapture:
    """
    Captures everything written to sys.stdout.

    Example:
        capture = StdoutCapture()

        with capture:
            print("Hello")

        print(capture.output)
    """

    def __init__(self) -> None:
        self._buffer = io.StringIO()
        self._original = None
        self.output: str = ""

    def __enter__(self) -> "StdoutCapture":
        self._original = sys.stdout
        sys.stdout = self._buffer
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.output = self._buffer.getvalue()
        sys.stdout = self._original
        self._buffer.close()

    def clear(self) -> None:
        self.output = ""
        self._buffer = io.StringIO()

    @property
    def text(self) -> str:
        return self.output


@contextmanager
def capture_stdout() -> Generator[StdoutCapture, None, None]:
    """
    Context manager for capturing stdout.

    Example:
        with capture_stdout() as cap:
            print("Hello")

        print(cap.output)
    """
    cap = StdoutCapture()
    with cap:
        yield cap