"""Minimal CLI entrypoint for development.

Usage:
  python -m autofire.cli [--version] [run]

Commands:
  run       Start the GUI application (calls app.main if available)
  --version Print package version (from VERSION.txt or VERSION.txt fallback)
"""

import importlib
import sys
from pathlib import Path


def _version():
    # Try to read VERSION.txt or fallback to VERSION.txt at repo root
    for candidate in (
        Path(__file__).parents[2] / "VERSION.txt",
        Path(__file__).parents[2] / "VERSION",
    ):
        if candidate.exists():
            return candidate.read_text(encoding="utf-8").strip()
    return "unknown"


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--version":
        print(_version())
        return 0
    if argv[0] == "run":
        # Try to call the GUI app entry point if it exists. Normalize return
        # values to integers so SystemExit(main()) doesn't receive a non-int
        # (which prints the object and yields exit code 1).
        try:
            mod = importlib.import_module("app.main")
            if hasattr(mod, "main"):
                res = mod.main()
                # If the app returned an int use it; otherwise treat as success.
                if isinstance(res, int):
                    return res
                try:
                    return int(res)
                except Exception:
                    return 0
            print("Found app.main but no callable main(); aborting")
            return 1
        except Exception as e:
            print("Could not import app.main to run GUI:", e)
            return 2

    print(f"Unknown command: {' '.join(argv)}")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
