"""Debug helper: start the Qt app, create controller, show UI briefly, then exit.

Usage (from repo root):
    python tools/debug_show.py

This sets AUTOFIRE_DEBUG_SHOW=1 so controller attempts to create the real
ModelSpaceWindow. It runs the event loop for a short period and then exits.
"""
from __future__ import annotations

import os
import sys
import logging

# Ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ["AUTOFIRE_DEBUG_SHOW"] = "1"

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QTimer

from frontend.controller import AutoFireController

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("AutoFire-Debug")
    # Instantiating controller should cause the ModelSpaceWindow to be created and shown
    log.info("Instantiating AutoFireController for debug run")
    ctrl = AutoFireController()
    # If controller created a model_space_window, ensure it's on top
    try:
        w = getattr(ctrl, "model_space_window", None)
        if w is not None:
            try:
                w.show()
                try:
                    getattr(w, "raise_")()
                except Exception:
                    pass
            except Exception:
                log.exception("Failed to show controller window")
    except Exception:
        log.exception("Error while accessing model_space_window")

    # Capture a screenshot shortly after showing (allow paint time) and quit after 2500ms
    def _capture():
        try:
            w = getattr(ctrl, "model_space_window", None)
            if w is None:
                log.warning("No model_space_window found for screenshot capture")
                return
            screen = QGuiApplication.primaryScreen()
            pix = screen.grabWindow(int(w.winId()))
            out = r'C:\Dev\pwsh-diagnostics\autofire-window-screenshot.png'
            os.makedirs(os.path.dirname(out), exist_ok=True)
            if pix.save(out):
                log.info(f"Saved screenshot to {out}")
            else:
                log.error("Failed to save screenshot")
        except Exception:
            log.exception("Screenshot capture failed")

    QTimer.singleShot(500, _capture)
    QTimer.singleShot(2500, app.quit)
    log.info("Starting Qt event loop for debug window (2.5s) and scheduled screenshot capture")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
