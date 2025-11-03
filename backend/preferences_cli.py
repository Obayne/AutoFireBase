"""CLI to view/update AutoFire preferences (JSON-backed).

Examples:
  python -m backend.preferences_cli --get hide_conduit_fill
  python -m backend.preferences_cli --set hide_conduit_fill=true
  python -m backend.preferences_cli --list

Notes:
- Values are simple strings; "true/false" (case-insensitive) become booleans, digits become ints.
- File location can be overridden with AUTOFIRE_PREF_FILE env var.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from .preferences import load_preferences, update_preferences

_BOOL_TRUE = {"1", "true", "yes", "on"}
_BOOL_FALSE = {"0", "false", "no", "off"}


def _parse_value(text: str) -> Any:
    t = text.strip().lower()
    if t in _BOOL_TRUE:
        return True
    if t in _BOOL_FALSE:
        return False
    if t.isdigit():
        try:
            return int(t)
        except ValueError:
            pass
    return text


essential_desc = "Inspect and update AutoFire preferences"


def run_cli(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=essential_desc)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="Print all preferences as JSON")
    g.add_argument("--get", metavar="KEY", help="Get a single preference value")
    g.add_argument("--set", metavar="KEY=VALUE", help="Set a single preference (e.g., k=v)")
    args = ap.parse_args(argv)

    if args.list:
        prefs = load_preferences()
        print(json.dumps(prefs, indent=2))
        return 0

    if args.get:
        key = args.get
        val = load_preferences().get(key)
        print(val)
        return 0

    if args.set:
        if "=" not in args.set:
            ap.error("--set requires KEY=VALUE")
        key, raw = args.set.split("=", 1)
        val = _parse_value(raw)
        merged = update_preferences({key: val})
        print(json.dumps({key: merged.get(key)}, indent=2))
        return 0

    return 1


def main() -> None:
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
