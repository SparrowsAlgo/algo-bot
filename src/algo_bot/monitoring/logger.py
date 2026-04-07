"""Application logging setup."""

from __future__ import annotations

import logging


def get_logger(name: str = "algo_bot") -> logging.Logger:
    """Return a console logger with a readable format."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
