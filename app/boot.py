"""Robust boot loader for AutoFire.

This module prefers the local/stashed improvements: it probes for app.main
robustly (normal import first, then file-based probing for frozen builds),
logs startup tracebacks to ~/AutoFire/logs, and shows a message box on
fatal startup errors.
"""

from __future__ import annotations

import datetime
import importlib
import importlib.util
import os
import sys
import traceback
from collections.abc import Callable

from PySide6 import QtWidgets


def _log_startup_error(text: str) -> str:
    base = os.path.join(os.path.expanduser("~"), "AutoFire", "logs")
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, f"startup_error_{datetime.datetime.now():%Y%m%d_%H%M%S}.log")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        # best effort only
        pass
    return path


def _load_app_main():
    """Load and return the app.main module.

    Try a normal import first (works in development and when the package is
    available). If that fails, probe common locations (PyInstaller's _MEIPASS
    and build/exe directories) and load via importlib.util.
    """
    try:
        return importlib.import_module("app.main")
    except Exception:
        pass

    candidates = []
    exe_dir = (
        os.path.dirname(sys.executable)
        if getattr(sys, "frozen", False)
        else os.path.dirname(__file__)
    )
    meipass = getattr(sys, "_MEIPASS", None)

    for base in [exe_dir, meipass, os.path.dirname(__file__)]:
        if not base:
            continue
        candidates.extend(
            [
                os.path.join(base, "_internal", "app", "main.py"),
                os.path.join(base, "app", "main.py"),
            ]
        )

    for path in candidates:
        if path and os.path.exists(path):
            try:
                spec = importlib.util.spec_from_file_location("app.main", path)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                    sys.modules["app.main"] = mod
                    return mod
            except Exception:
                # try next candidate
                continue

    raise ModuleNotFoundError("app.main")


def resolve_create_window() -> Callable[[], QtWidgets.QWidget]:
    """Return a callable that constructs the main window from app.main.

    Prefer a create_window() factory, otherwise try to instantiate MainWindow.
    """
    main_mod = importlib.import_module("app.main")
    cw = getattr(main_mod, "create_window", None)
    if callable(cw):
        return cw
    MW = getattr(main_mod, "MainWindow", None)
    if MW is not None:

        def _cw() -> QtWidgets.QWidget:
            return MW()

        return _cw
    raise ImportError("app.main does not expose create_window() or MainWindow")


def main() -> None:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    try:
        m = _load_app_main()
        create_window = getattr(m, "create_window", None)
        if callable(create_window):
            w = create_window()
            w.show()
            app.exec()
            return

        # Fallback: try to instantiate MainWindow from the module
        MW = getattr(m, "MainWindow", None)
        if MW is not None:
            w = MW()
            w.show()
            app.exec()
            return

        # Generic fallback UI
        w = QtWidgets.QMainWindow()
        w.setWindowTitle("Auto-Fire — Fallback UI (no create_window)")
        lab = QtWidgets.QLabel("Fallback window loaded.")
        lab.setMargin(16)
        w.setCentralWidget(lab)
        w.resize(900, 600)
        w.show()
        app.exec()
    except Exception:
        tb = traceback.format_exc()
        p = _log_startup_error(tb)
        try:
            QtWidgets.QMessageBox.critical(None, "Startup Error", f"{tb}\n\nSaved: {p}")
        except Exception:
            # If Qt is not available or message box fails, print minimal info
            print("Startup Error: ", p)


if __name__ == "__main__":
    main()
