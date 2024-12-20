"""
Logging utility functions
"""

import logging
from typing import Optional

from config.settings import logging_settings


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger instance

    Args:
        name (Optional[str]): Logger name

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name or __name__)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(logging_settings.format))
        logger.addHandler(handler)

    logger.setLevel(logging_settings.level)
    return logger
