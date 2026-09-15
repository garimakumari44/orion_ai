"""
Runtime layer for the Sandbox module.

This package provides the core execution environment responsible for
creating isolated workspaces, managing sandbox sessions, enforcing
resource limits, executing code safely, and cleaning up resources.

Modules
-------
executor
    Main execution engine.

session
    Sandbox session lifecycle management.

environment
    Virtual environment management.

resources
    CPU, memory, and timeout constraints.

filesystem
    Temporary workspace management.

subprocess
    Secure subprocess execution.

cleanup
    Automatic cleanup of sandbox resources.
"""

from .executor import SandboxExecutor
from .session import SandboxSession
from .environment import SandboxEnvironment
from .resources import ResourceLimits, ResourceMonitor
from .filesystem import SandboxFilesystem
from .subprocess import SafeSubprocess, ProcessResult
from .cleanup import SandboxCleanup

__all__ = [
    # Execution
    "SandboxExecutor",

    # Session
    "SandboxSession",

    # Environment
    "SandboxEnvironment",

    # Resources
    "ResourceLimits",
    "ResourceMonitor",

    # Filesystem
    "SandboxFilesystem",

    # Subprocess
    "SafeSubprocess",
    "ProcessResult",

    # Cleanup
    "SandboxCleanup",
]