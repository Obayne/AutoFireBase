"""
Lightweight wrapper to run the optional updater without crashing the app.

- Lives in backend per layering rules (non-UI logic).
- Returns True if any update was applied, False otherwise.
- Silently tolerates missing updater module or any runtime errors.
"""

from __future__ import annotations


def run_updater_safe() -> bool:
    """Attempt to run updater if available; never raises.

    The updater module is optional in dev and may be omitted in some
    environments. This wrapper ensures app startup doesn't fail when it's
    missing, while still invoking updates when present.
    """
    try:
        # Local import so import errors are contained here.
        from updater.auto_update import check_and_apply_updates  # type: ignore

        try:
            return bool(check_and_apply_updates())
        except Exception:
            # Updater present but failed at runtime — treat as no-op.
            return False
    except Exception:
        # Updater package not available — ignore.
        return False
