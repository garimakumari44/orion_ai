"""
Constants used throughout the sandbox module.
"""

from enum import Enum


class SandboxBackend(str, Enum):
    """Supported execution environments."""

    LOCAL = "local"
    DOCKER = "docker"
    FIREJAIL = "firejail"
    PODMAN = "podman"
    KUBERNETES = "kubernetes"


class ExecutionStatus(str, Enum):
    """Execution lifecycle."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class SandboxError(str, Enum):
    """Sandbox error categories."""

    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"
    CPU_LIMIT = "cpu_limit"
    SECURITY = "security"
    EXECUTION = "execution"
    IMPORT = "import"
    FILESYSTEM = "filesystem"
    UNKNOWN = "unknown"


class ResourceLimit:
    """
    Default resource limits.
    """

    MAX_CPU_SECONDS = 30
    MAX_MEMORY_MB = 2048
    MAX_DISK_MB = 2048
    MAX_PROCESSES = 10
    MAX_OPEN_FILES = 128
    MAX_RUNTIME_SECONDS = 60
    MAX_OUTPUT_SIZE = 10 * 1024 * 1024
    MAX_FILE_SIZE = 100 * 1024 * 1024


SUPPORTED_IMAGE_FORMATS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".pdf",
}

SUPPORTED_DATA_FORMATS = {
    ".csv",
    ".json",
    ".xlsx",
    ".parquet",
    ".txt",
}

SUPPORTED_CODE_LANGUAGES = {
    "python",
}