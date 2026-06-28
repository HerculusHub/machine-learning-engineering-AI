"""
Central logging configuration.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from mobile_ai_system.core.config import settings
from mobile_ai_system.core.constants import LOG_FORMAT


LOG_DIRECTORY = Path("logs")
LOG_DIRECTORY.mkdir(exist_ok=True)


LOG_FILE = LOG_DIRECTORY / "application.log"


logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=LOG_FORMAT,
)


file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
)

file_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)


root_logger = logging.getLogger()

root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.
    """

    return logging.getLogger(name)