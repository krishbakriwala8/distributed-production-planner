"""Logging setup"""

import logging
import sys
from src.utils.config import Config


def setup_logger(name: str) -> logging.Logger:
    """Setup logger for a module"""
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(Config.LOG_LEVEL)

    # Formatter
    formatter = logging.Formatter(Config.LOG_FORMAT)
    handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger