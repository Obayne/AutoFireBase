"""Stable wrapper (v2): delegate to scripts.tools._auto_resolve_conflicts.

This tiny file prevents duplicated resolver logic and avoids self-modifying
corruption. It simply calls the canonical implementation.
"""

from scripts.tools._auto_resolve_conflicts import main as _auto_main


def main() -> int:
    """Run the canonical resolver and return its exit code."""
    return _auto_main()


if __name__ == "__main__":
    """Stable wrapper (v2): delegate to scripts.tools._auto_resolve_conflicts.

    This tiny file prevents duplicated resolver logic and avoids self-modifying
    corruption. It simply calls the canonical implementation.
    """

    from scripts.tools._auto_resolve_conflicts import main as _auto_main

    def main() -> int:
        """Run the canonical resolver and return its exit code."""
        return _auto_main()

    if __name__ == "__main__":
        raise SystemExit(main())
