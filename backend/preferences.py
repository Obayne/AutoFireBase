"""Minimal preferences backend shim used by ModelSpaceWindow.

Provides load_preferences and update_preferences functions expected by
the UI. This is intentionally small: it reads/writes a JSON file in the
user's AutoFire folder and falls back to sensible defaults.
"""

from __future__ import annotations

import json
import os
from typing import Any

DEFAULT_PREFS = {
    "px_per_ft": 12.0,
    "grid": 12,
    "snap": True,
    "show_coverage": True,
    "theme": "dark",
}


def _prefs_path() -> str:
    p = os.path.join(os.path.expanduser("~"), "AutoFire")
    os.makedirs(p, exist_ok=True)
    return os.path.join(p, "prefs.json")


def load_preferences() -> dict[str, Any]:
    """Load preferences from disk; return defaults on error."""
    try:
        with open(_prefs_path(), encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                # merge with defaults
                out = DEFAULT_PREFS.copy()
                out.update(data)
                return out
    except Exception:
        pass
    return DEFAULT_PREFS.copy()


def update_preferences(prefs: dict[str, Any]) -> bool:
    """Write preferences to disk. Returns True on success."""
    try:
        with open(_prefs_path(), "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=2)
        return True
    except Exception:
        return False
