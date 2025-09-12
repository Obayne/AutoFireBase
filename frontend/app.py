"""
Frontend application entrypoint.

Phase 1 integration extracts a stable entrypoint that calls the
existing boot logic (`app.boot.main`). Future phases will migrate
window construction into `frontend/` modules behind a clean API.
"""

from __future__ import annotations


def main() -> None:
    # Delegate to existing resilient boot.
    from app.boot import main as _boot

    _boot()


if __name__ == "__main__":
    main()

