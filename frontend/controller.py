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
        # Preferences: merge UI/runtime defaults with persisted user prefs.
        # Keep base values minimal and safe for test runs, then overlay
        # backend.preferences (JSON) values if available.
        base_prefs = {
            "px_per_ft": 12.0,
            "snap_label": "grid",
            "snap_step_in": 0.0,
            "grid": 12,
            "snap": True,
        }
        try:
            from backend.preferences import load_preferences

            persisted = load_preferences()
            base_prefs.update(persisted)
        except Exception:
            # Non-fatal: continue with base prefs if preferences unavailable
            pass
        self.prefs = base_prefs
        self.devices_all: list = []
        # Minimal signal stubs that provide a connect() method used by UI
        # components during initialization. They are intentionally no-ops so
        # tests don't need a full Qt signal object.
        self.model_space_changed = SignalStub()
        self.prefs_changed = SignalStub()

        # Initialize optional professional Window Manager if available.
        # This enables intelligent positioning, multi-monitor awareness, and
        # saved workspace layouts. Fallback gracefully if not present.
        self.window_manager = None
        try:
            # Only initialize when a Qt application exists (tests may be headless)
            from PySide6.QtWidgets import QApplication  # type: ignore

            if QApplication.instance() is not None:
                from window_management_system import WindowManager  # type: ignore

                self.window_manager = WindowManager()
                logger.info("WindowManager initialized")
        except Exception:
            # Not fatal for tests or minimal runs
            logger.debug("WindowManager not available; continuing without it")

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
                        try:
                            # Mark that a GUI window was shown to avoid duplicate creation later
                            self._gui_shown = True
                        except Exception:
                            pass
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
                        try:
                            self._gui_shown = True
                        except Exception:
                            pass
                    except Exception:
                        logger.exception("Failed to show fallback debug window")
            except Exception:
                # Non-fatal: debug helper should never raise during normal test runs
                logging.getLogger(__name__).exception("Debug UI helper failed")

        # If running as a GUI application (autofire main launcher), create
        # and show the main ModelSpaceWindow so the app is immediately visible.
        # This runs regardless of AUTOFIRE_DEBUG_SHOW and ensures the window appears in normal runs.
        try:
            if os.environ.get("AUTOFIRE_GUI") == "1" and not getattr(self, "_gui_shown", False):
                from frontend.windows.model_space import ModelSpaceWindow

                try:
                    win = ModelSpaceWindow(self)
                    self.model_space_window = win
                    try:
                        # Register with Window Manager (if available) before showing
                        wm = getattr(self, "window_manager", None)
                        if wm:
                            wm.register_window(win, "model_space_main", "model_space")
                    except Exception:
                        logger.debug("Failed to register window with WindowManager")
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
                    try:
                        self._gui_shown = True
                    except Exception:
                        pass
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

    def on_model_space_closed(self):
        """Handle model space window closure - close all windows and quit."""
        try:
            from PySide6.QtWidgets import QApplication

            # Clear the reference
            self.model_space_window = None

            # Close any other windows (like paperspace, layer manager, etc.)
            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                # Find all top-level windows and close them
                for widget in app.topLevelWidgets():
                    if hasattr(widget, "close") and widget.isVisible():
                        try:
                            widget.close()
                        except Exception:
                            pass
                # Quit the application
                app.quit()
        except Exception:
            # Fallback: just quit
            import sys

            sys.exit(0)

    def on_paperspace_closed(self):
        """Handle paperspace window closure."""
        # Paperspace can close independently, but if model space is also closed, quit
        if self.model_space_window is None:
            try:
                from PySide6.QtWidgets import QApplication

                app = QApplication.instance()
                if app:
                    app.quit()
            except Exception:
                import sys

                sys.exit(0)

    def __getattr__(self, name: str):
        # Lazily provide no-op signal stubs for any "*_changed" attribute
        # to keep UI initialization working in headless tests.
        if name.endswith("_changed"):
            return SignalStub()
        raise AttributeError(name)
