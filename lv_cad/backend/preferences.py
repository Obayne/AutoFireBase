"""Preferences helpers migrated to lv_cad.backend (parity copy)."""

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
    try:
        with open(_prefs_path(), encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                out = DEFAULT_PREFS.copy()
                out.update(data)
                return out
    except Exception:
        pass
    return DEFAULT_PREFS.copy()


def update_preferences(prefs: dict[str, Any]) -> bool:
    try:
        with open(_prefs_path(), "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=2)
        return True
    except Exception:
        return False
