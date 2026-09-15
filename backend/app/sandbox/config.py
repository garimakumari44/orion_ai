"""
Sandbox configuration.
"""

from pathlib import Path

from pydantic import BaseModel, Field

from .constants import ResourceLimit, SandboxBackend


class SandboxConfig(BaseModel):
    """
    Configuration for sandbox execution.
    """

    backend: SandboxBackend = SandboxBackend.LOCAL

    workspace: Path = Field(
        default=Path("./sandbox_workspace")
    )

    cleanup_after_execution: bool = True

    timeout_seconds: int = ResourceLimit.MAX_RUNTIME_SECONDS

    memory_limit_mb: int = ResourceLimit.MAX_MEMORY_MB

    cpu_limit_seconds: int = ResourceLimit.MAX_CPU_SECONDS

    disk_limit_mb: int = ResourceLimit.MAX_DISK_MB

    process_limit: int = ResourceLimit.MAX_PROCESSES

    enable_network: bool = False

    read_only_filesystem: bool = False

    capture_stdout: bool = True

    capture_stderr: bool = True

    allow_file_upload: bool = True

    allow_plot_generation: bool = True

    allow_package_imports: bool = True

    log_execution: bool = True

    class Config:
        arbitrary_types_allowed = True