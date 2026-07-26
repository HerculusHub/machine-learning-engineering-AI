"""
Central logging configuration.
"""

from __future__ import annotations

import logging
from pathlib import Path

from mobile_ai_system.core.config import get_settings


_LOGGER_INITIALIZED = False


def configure_logging() -> None:
    """
    Configure application logging.

    Safe to call multiple times.
    """

    global _LOGGER_INITIALIZED

    if _LOGGER_INITIALIZED:
        return

    settings = get_settings()

    # Create log directory if it does not exist
    log_dir = Path(
        getattr(settings, "log_directory", "logs")
    )

    log_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_file = getattr(
        settings,
        "log_file",
        "application.log",
    )

    logging.basicConfig(
        level=getattr(
            logging,
            settings.log_level.upper(),
            logging.INFO,
        ),
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(
                log_dir / log_file,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )

    _LOGGER_INITIALIZED = True


def get_logger(
    name: str,
) -> logging.Logger:
    """
    Return a configured logger.
    """

    configure_logging()

    return logging.getLogger(name)