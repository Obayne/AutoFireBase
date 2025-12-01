"""Centralized logging setup for AutoFire.

Provide a small helper to configure basic logging consistently for
headless tests, simulators, and the running application.
"""
from __future__ import annotations

import logging

DEFAULT_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"


def setup_logging(level: int = logging.INFO, fmt: str | None = None) -> None:
    """Configure root logging. Safe to call multiple times.

    Args:
        level: logging level (e.g., logging.DEBUG)
        fmt: optional format string
    """
    fmt = fmt or DEFAULT_FORMAT
    root = logging.getLogger()
    # If handlers already configured, just set level and return
    if root.handlers:
        root.setLevel(level)
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
    root.setLevel(level)
