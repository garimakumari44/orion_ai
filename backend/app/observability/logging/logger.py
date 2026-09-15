"""
Central logging configuration.

Provides application-wide structured logging.
"""

import logging
import sys
from pathlib import Path

from .formatter import JSONFormatter


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class LoggerManager:
    """
    Singleton logger manager.

    Responsible for:
    - Logger creation
    - Formatting
    - File handlers
    - Console output
    """

    _loggers = {}

    @classmethod
    def get_logger(
        cls,
        name: str = "ai-platform"
    ) -> logging.Logger:

        if name in cls._loggers:
            return cls._loggers[name]


        logger = logging.getLogger(name)

        logger.setLevel(logging.INFO)

        logger.propagate = False


        formatter = JSONFormatter()


        # Console handler
        console_handler = logging.StreamHandler(
            sys.stdout
        )

        console_handler.setFormatter(
            formatter
        )


        # File handler
        file_handler = logging.FileHandler(
            LOG_DIR / "application.log"
        )

        file_handler.setFormatter(
            formatter
        )


        logger.addHandler(
            console_handler
        )

        logger.addHandler(
            file_handler
        )


        cls._loggers[name] = logger


        return logger



def get_logger(
    name: str = "ai-platform"
):
    """
    Public logger interface.
    """

    return LoggerManager.get_logger(name)