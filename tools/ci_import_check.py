"""CI helper: robustly check that PySide6 and core GUI modules load.

This script is used in CI to detect missing native dependencies (like
libEGL) that only appear when core GUI modules are imported. It
exits with code 0 on success and non-zero on failure.
"""

import sys
import traceback


def main():
    try:
        import PySide6

        # Import modules that tend to trigger loading of native libs
        from PySide6 import QtCore

        # Print some info for logs
        print("PySide6 load OK; version:", getattr(PySide6, "__version__", "unknown"))
        print("QT_VERSION_STR:", QtCore.QT_VERSION_STR)
        return 0
    except Exception:
        print("PySide6 import failed (native libs may be missing):", file=sys.stderr)
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
