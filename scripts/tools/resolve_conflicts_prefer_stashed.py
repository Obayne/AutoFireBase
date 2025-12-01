"""Wrapper that delegates to scripts.tools._auto_resolve_conflicts.

Keep this file minimal to avoid self-modification during repo-wide runs.
"""

from scripts.tools._auto_resolve_conflicts import main as _auto_main


def main() -> int:
    """Run the canonical auto-resolve implementation and return its exit code."""
    return _auto_main()


if __name__ == "__main__":
    raise SystemExit(main())
