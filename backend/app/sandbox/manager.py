"""
Central sandbox manager.

Responsible for:
- creating execution sessions
- selecting execution backend
- lifecycle management
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from .config import SandboxConfig

logger = logging.getLogger(__name__)


class SandboxManager:
    """
    Coordinates sandbox execution sessions.
    """

    def __init__(
        self,
        config: Optional[SandboxConfig] = None,
    ):
        self.config = config or SandboxConfig()

        self.workspace = self.config.workspace
        self.workspace.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Sandbox initialized at %s",
            self.workspace,
        )

    def create_session(self) -> Path:
        """
        Create isolated workspace.
        """

        session_id = str(uuid.uuid4())

        session = self.workspace / session_id
        session.mkdir(parents=True, exist_ok=True)

        logger.info("Created sandbox %s", session_id)

        return session

    def cleanup_session(self, session: Path) -> None:
        """
        Remove sandbox directory.
        """

        if (
            self.config.cleanup_after_execution
            and session.exists()
        ):
            shutil.rmtree(session, ignore_errors=True)

            logger.info("Removed sandbox %s", session)

    def temporary_directory(self) -> tempfile.TemporaryDirectory:
        """
        Temporary working directory.
        """

        return tempfile.TemporaryDirectory()

    def backend(self) -> str:
        """
        Return configured backend.
        """

        return self.config.backend.value

    def health(self) -> dict:
        """
        Simple health information.
        """

        return {
            "backend": self.config.backend.value,
            "workspace": str(self.workspace),
            "network": self.config.enable_network,
            "cleanup": self.config.cleanup_after_execution,
            "plots": self.config.allow_plot_generation,
        }

    def shutdown(self) -> None:
        """
        Cleanup manager resources.
        """

        logger.info("Sandbox manager shut down.")