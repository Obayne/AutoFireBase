"""Site-level test helper: ensure a QApplication exists when running tests.

This module is imported automatically by Python when it's on sys.path. We use
it to create a QApplication early during pytest runs so modules that import
or construct Qt widgets at import-time don't fail during collection.

It is intentionally conservative: it only attempts to create a QApplication
when we detect pytest on the command line or the PYTEST_CURRENT_TEST env var
is present. If PySide6 isn't available the code silently does nothing so
non-GUI test environments continue to work.
"""

import os
import sys


def _maybe_create_qapp() -> None:
    # Only attempt to create QApplication when running under pytest to
    # avoid side-effects for normal interpreter usage.
    running_pytest = "PYTEST_CURRENT_TEST" in os.environ or any(
        "pytest" in (arg or "") for arg in sys.argv
    )
    if not running_pytest:
        return

    try:
        # Import may fail if PySide6 isn't installed; treat that as a
        # non-fatal condition and return.
        from PySide6.QtWidgets import QApplication
    except ImportError:
        return

    # Construct a minimal QApplication if none exists yet.
    if QApplication.instance() is None:
        QApplication([])


_maybe_create_qapp()
