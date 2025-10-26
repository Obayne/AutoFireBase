"""
Lightweight JSON-backed user preferences.

Design goals
- No heavy imports or module-level side effects
- Simple schema with safe defaults
- Merge-based updates (preserve unknown keys for forward-compat)

Current keys
- report_default_dir: str
- include_device_docs_in_submittal: bool
- export_image_dpi: int

Environment overrides (optional, mostly for tests)
- AUTOFIRE_PREF_FILE: absolute path to the preferences JSON
- AUTOFIRE_PREF_DIR: directory used when file path isn't given
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def _default_report_dir(cwd: Optional[Path] = None) -> str:
    base = Path(cwd) if cwd is not None else Path(os.getcwd())
    return str(base / "artifacts" / "reports")


def get_default_preferences(cwd: Optional[Path] = None) -> Dict[str, Any]:
    return {
        "report_default_dir": _default_report_dir(cwd),
        "include_device_docs_in_submittal": True,
        "export_image_dpi": 300,
    }


def get_preferences_path(path: Optional[os.PathLike[str] | str] = None) -> Path:
    if path:
        return Path(path)

    # Allow explicit override
    env_file = os.environ.get("AUTOFIRE_PREF_FILE")
    if env_file:
        return Path(env_file)

    # Fall back to an app-specific folder under the user's home directory
    env_dir = os.environ.get("AUTOFIRE_PREF_DIR")
    if env_dir:
        pref_dir = Path(env_dir)
    else:
        pref_dir = Path.home() / ".autofire"
    return pref_dir / "preferences.json"


def _ensure_dir(p: Path) -> None:
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Best effort; callers should still handle failures on write
        pass


def _merge_defaults(loaded: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    # Shallow merge: keep unknown keys, but ensure defaults exist for known ones
    out = dict(loaded) if loaded else {}
    for k, v in defaults.items():
        if k not in out:
            out[k] = v
    # Normalize expected types
    out["report_default_dir"] = str(out.get("report_default_dir", defaults["report_default_dir"]))
    try:
        out["export_image_dpi"] = int(out.get("export_image_dpi", defaults["export_image_dpi"]))
    except (TypeError, ValueError):
        out["export_image_dpi"] = defaults["export_image_dpi"]
    out["include_device_docs_in_submittal"] = bool(
        out.get("include_device_docs_in_submittal", defaults["include_device_docs_in_submittal"])
    )
    return out


def load_preferences(
    path: Optional[os.PathLike[str] | str] = None,
    *,
    cwd: Optional[Path] = None,
) -> Dict[str, Any]:
    pref_path = get_preferences_path(path)
    defaults = get_default_preferences(cwd)
    if not pref_path.exists():
        return dict(defaults)
    try:
        with pref_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return dict(defaults)
            return _merge_defaults(data, defaults)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, ValueError):
        # Corrupt or unreadable file -> fall back to defaults
        return dict(defaults)


def save_preferences(
    prefs: Dict[str, Any],
    path: Optional[os.PathLike[str] | str] = None,
) -> Path:
    pref_path = get_preferences_path(path)
    _ensure_dir(pref_path)
    # Preserve unknown keys, but write in a stable order for diffs
    try:
        with pref_path.open("w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=2, sort_keys=True)
    except OSError as e:
        raise OSError(f"Failed to write preferences to {pref_path}: {e}") from e
    return pref_path


def update_preferences(
    updates: Dict[str, Any],
    path: Optional[os.PathLike[str] | str] = None,
    *,
    cwd: Optional[Path] = None,
) -> Dict[str, Any]:
    """Load, apply partial updates, normalize, and save.

    Returns the merged preferences.
    """
    current = load_preferences(path, cwd=cwd)
    current.update(updates or {})
    # Normalize against defaults to ensure types
    merged = _merge_defaults(current, get_default_preferences(cwd))
    save_preferences(merged, path)
    return merged


__all__ = [
    "get_default_preferences",
    "get_preferences_path",
    "load_preferences",
    "save_preferences",
    "update_preferences",
]
