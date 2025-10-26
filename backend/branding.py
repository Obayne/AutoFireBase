"""Centralized product branding and version helpers.

This module provides a single source of truth for the product/app name and
related display strings. Update APP_NAME/PRODUCT_NAME here to rebrand.
"""

from __future__ import annotations

from pathlib import Path

# Default names; adjust here for rebrand (e.g., "AlarmForge")
APP_NAME: str = "AlarmForge"
PRODUCT_NAME: str = APP_NAME


def get_version() -> str:
    """Return version string from VERSION.txt at repo root, fallback to dev."""
    # Resolve assuming this file is backend/branding.py
    repo_root = Path(__file__).resolve().parents[1]
    version_file = repo_root / "VERSION.txt"
    try:
        text = version_file.read_text(encoding="utf-8").strip()
        return text if text else "0.0.0-dev"
    except Exception:
        return "0.0.0-dev"


def full_product_label() -> str:
    """Convenience label like "AutoFire v1.2.3" for UI/report headers."""
    return f"{PRODUCT_NAME} v{get_version()}"
