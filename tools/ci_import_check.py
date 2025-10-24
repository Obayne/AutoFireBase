"""CI helper: robustly check that PySide6 and core GUI modules load.

This script is used in CI to detect missing native dependencies (like
libEGL) that only appear when core GUI modules are imported. It
exits with code 0 on success and non-zero on failure.
"""

import os
import sys
import traceback


def main():
    # Force an offscreen platform so Qt will attempt to load native graphics
    # backends (libEGL/libGL) even without a display.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    try:
        # Importing QtGui and instantiating QGuiApplication forces Qt to load
        # the underlying graphics libraries; if libEGL/libGL are missing
        # this should fail and be visible in stderr/exit code.
        from PySide6 import QtCore, QtGui

        print("PySide6 load OK; QT_VERSION_STR:", getattr(QtCore, "QT_VERSION_STR", "unknown"))

        try:
            app = QtGui.QGuiApplication([])
            # Clean up quickly
            app.quit()
        except Exception:
            print(
                "QGuiApplication creation failed (likely missing native libs):",
                file=sys.stderr,
            )
            traceback.print_exc()
            return 3

        return 0
    except Exception:
        print("PySide6 import failed (native libs may be missing):", file=sys.stderr)
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
