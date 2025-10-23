from __future__ import annotations

import logging
import os


class SignalStub:
    """Minimal no-op signal-like object used for headless tests.

    It provides a connect() method so UI code can wire signals without a
    full QObject/QSignal implementation.
    """

    def connect(self, *_, **__):
        return None


class AutoFireController:
    """Minimal controller stub for headless testing.

    This class intentionally avoids importing Qt at module import time so
    that tests can safely import it in environments without PySide6.
    """

    def __init__(self) -> None:
        import time

        logger = logging.getLogger(__name__)
        start_ts = time.time()
        logger.info("AutoFireController.__init__ start")

        # Placeholder attribute expected by tests; in the full application
        # this would reference the main model space window instance.
        self.model_space_window = object()
        # Provide lightweight default preferences and devices for headless
        # tests that expect controller.prefs and controller.devices_all.
        # Keep values minimal and safe for test runs.
        self.prefs = {
            "px_per_ft": 12.0,
            "snap_label": "grid",
            "snap_step_in": 0.0,
            "grid": 12,
            "snap": True,
        }
        self.devices_all: list = []
        # Minimal signal stubs that provide a connect() method used by UI
        # components during initialization. They are intentionally no-ops so
        # tests don't need a full Qt signal object.
        self.model_space_changed = SignalStub()
        self.prefs_changed = SignalStub()

        # Debug helper: when AUTOFIRE_DEBUG_SHOW=1 is set in the environment
        # attempt to create the full ModelSpaceWindow (preferred) so the
        # running application shows the populated System Builder and real
        # UI content. If that fails (missing modules or environment issues),
        # fall back to a tiny debug QMainWindow so at least a visible
        # top-level window appears for troubleshooting.
        if os.environ.get("AUTOFIRE_DEBUG_SHOW") == "1":
            logger = logging.getLogger(__name__)
            try:
                # Prefer creating the real ModelSpaceWindow if available.
                try:
                    from frontend.windows.model_space import ModelSpaceWindow

                    win = ModelSpaceWindow(self)
                    win.setWindowTitle("AutoFire - Debug Visible")
                    self.model_space_window = win
                    try:
                        win.show()
                        try:
                            getattr(win, "raise_")()
                        except Exception:
                            pass
                        logger.info("Created and showed ModelSpaceWindow for debug run")
                    except Exception:
                        logger.exception("Failed to show ModelSpaceWindow; falling back")
                except Exception:
                    # If ModelSpaceWindow can't be created, fallback to a minimal window
                    from PySide6.QtWidgets import QMainWindow

                    class _DebugMainWindow(QMainWindow):
                        def __init__(self):
                            super().__init__()
                            self.setWindowTitle("AutoFire (Debug Visible)")

                    win = _DebugMainWindow()
                    self.model_space_window = win
                    try:
                        win.show()
                        try:
                            getattr(win, "raise_")()
                        except Exception:
                            pass
                        logger.info("Created fallback debug QMainWindow")
                    except Exception:
                        logger.exception("Failed to show fallback debug window")
            except Exception:
                # Non-fatal: debug helper should never raise during normal test runs
                logging.getLogger(__name__).exception("Debug UI helper failed")

                # If running as a GUI application (autofire main launcher), create
                # and show the main ModelSpaceWindow so the app is immediately visible.
                if os.environ.get("AUTOFIRE_GUI") == "1":
                    try:
                        from frontend.windows.model_space import ModelSpaceWindow

                        try:
                            win = ModelSpaceWindow(self)
                            self.model_space_window = win
                            try:
                                win.show()
                                try:
                                    getattr(win, "raise_")()
                                except Exception:
                                    pass
                                logging.getLogger(__name__).info(
                                    "ModelSpaceWindow created and shown for AUTOFIRE_GUI run"
                                )
                            except Exception:
                                logging.getLogger(__name__).exception(
                                    "Failed to show ModelSpaceWindow in AUTOFIRE_GUI run"
                                )
                        except Exception:
                            logging.getLogger(__name__).exception(
                                "Failed to create ModelSpaceWindow in AUTOFIRE_GUI run"
                            )
                    except Exception:
                        # Import failed or PySide not available - not fatal for tests
                        pass

        # End timing
        try:
            end_ts = time.time()
            logger.info("AutoFireController.__init__ complete (%.3fs)", end_ts - start_ts)
        except Exception:
            pass

    def __getattr__(self, name: str):
        # Lazily provide no-op signal stubs for any "*_changed" attribute
        # to keep UI initialization working in headless tests.
        if name.endswith("_changed"):
            return SignalStub()
        raise AttributeError(name)
