"""
Sandbox execution framework.

Provides a unified interface for executing code,
capturing outputs, handling timeouts, retries,
and collecting generated artifacts.
"""

from .artifacts import (
    Artifact,
    ArtifactManager,
)
from .result import (
    ExecutionMetrics,
    ExecutionResult,
)
from .runner import ExecutionRunner
from .stderr import (
    StderrCapture,
    capture_stderr,
)
from .stdout import (
    StdoutCapture,
    capture_stdout,
)
from .timeout import (
    Timeout,
    TimeoutError,
    timeout,
)
from .retries import retry

__all__ = [
    # Runner
    "ExecutionRunner",

    # Results
    "ExecutionResult",
    "ExecutionMetrics",

    # Stdout / Stderr
    "StdoutCapture",
    "StderrCapture",
    "capture_stdout",
    "capture_stderr",

    # Artifacts
    "Artifact",
    "ArtifactManager",

    # Timeout
    "Timeout",
    "TimeoutError",
    "timeout",

    # Retry
    "retry",
]

__version__ = "1.0.0"