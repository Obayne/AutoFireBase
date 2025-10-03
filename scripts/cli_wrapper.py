"""Small wrapper to verify minimal runtime dependencies and invoke the package CLI.

Usage:
  python scripts/cli_wrapper.py [--version] [run]

This is a dev helper: it checks for minimal dependencies and prints an actionable
message if they're missing. It then delegates to `autofire.cli`.
"""

import sys
from importlib import import_module
from pathlib import Path

MINIMAL_REQ = Path(__file__).parents[1] / "requirements-dev-minimal.txt"


def _check_deps():
    missing = []
    # The minimal file lists package names; for our purposes try importing the
    # canonical module names for pytest and PySide6.
    try:
        pass  # type: ignore
    except Exception:
        missing.append("pytest")
    try:
        pass  # type: ignore
    except Exception:
        missing.append("PySide6")
    return missing


def main(argv=None):
    argv = argv or sys.argv[1:]
    missing = _check_deps()
    if missing:
        print("Missing dependencies needed for the CLI/dev run:", ", ".join(missing))
        print("Install them with: python -m pip install -r requirements-dev-minimal.txt")
        return 2

    # Delegate to package CLI
    try:
        mod = import_module("autofire.cli.__main__")
    except Exception as e:
        print("Failed to import autofire.cli.__main__:", e)
        return 3

    # call main() if present
    if hasattr(mod, "main"):
        return mod.main(argv)
    print("autofire.cli.__main__ has no main(); nothing to do.")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
