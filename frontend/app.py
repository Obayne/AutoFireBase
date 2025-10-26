"""
Frontend application - Main AutoFire GUI application.
Clean, modular entry point for the fire alarm CAD application.
"""

from __future__ import annotations

import logging
import os
import sys

# Ensure absolute imports work when running as a script or module
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from frontend.controller import AutoFireController  # noqa: E402

# Keep a module-level reference to the controller to satisfy linters and avoid GC issues
_GLOBAL_CONTROLLER = None


def main() -> int:
    """Main application entry point."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting AutoFire...")

    try:
        # Initialize database connection early in startup
        from db.connection import initialize_database

        logger.info("Initializing database...")
        initialize_database(in_memory=False)  # Use persistent database file
        logger.info("Database initialized successfully")

        # Create Qt application
        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName("AutoFire")
        app.setApplicationVersion("0.8.0")

        # Apply a modern theme early so widgets pick up palette and styles
        try:
            from frontend.ui.theme import apply_theme

            # Allow env override; default to 'dark'
            theme_name = os.environ.get("AUTOFIRE_THEME", "dark")
            apply_theme(app, theme_name)
            logger.info("Applied theme: %s", theme_name)
        except Exception:
            logger.exception("Failed to apply theme; continuing with default palette")

        # Start with main CAD interface - System Builder opens when creating new projects
        logger.info("Starting main CAD interface...")

        # Create and retain a global reference to the application controller.
        # Defer heavy controller initialization until after the event loop starts
        # so the UI can paint immediately and avoid blocking the main thread.
        global _GLOBAL_CONTROLLER

        def _init_controller():
            nonlocal logger
            try:
                logger.info("Deferred: initializing AutoFireController...")
                # instantiate controller (may perform heavier work)
                _GLOBAL_CONTROLLER = AutoFireController()
                logger.info("Deferred: AutoFireController initialized")
            except Exception:
                logger.exception("Deferred controller initialization failed")

        # Schedule controller initialization right after the event loop starts
        QTimer.singleShot(0, _init_controller)

        # For normal GUI runs, set a flag so the controller knows to create
        # and show the main window (this is set only when running the app
        # via `main.py` and won't affect headless tests).
        try:
            os.environ.setdefault("AUTOFIRE_GUI", "1")
        except Exception:
            pass

        # Force a paint/update of top-level widgets shortly after startup.
        # Some platforms need an explicit repaint after show() to avoid an
        # initially-blank window (drivers/x11/wayland/DirectComposition edge cases).
        def _force_paint():
            try:
                for w in app.topLevelWidgets():
                    try:
                        w.show()
                        try:
                            getattr(w, "raise_")()
                        except Exception:
                            pass
                        try:
                            w.repaint()
                        except Exception:
                            pass
                    except Exception:
                        continue
                # Ensure pending paint events are processed
                try:
                    app.processEvents()
                except Exception:
                    pass
            except Exception:
                logger.exception("_force_paint failed")

        QTimer.singleShot(500, _force_paint)

        # Debug helper: force any top-level Qt widgets to show when explicitly requested.
        # This is a low-risk, reversible hook used locally to make the UI visible when
        # running under CI or headless environments during troubleshooting.
        if os.environ.get("AUTOFIRE_DEBUG_SHOW") == "1":
            try:
                logger.info("AUTOFIRE_DEBUG_SHOW=1: forcing top-level widgets to show and raise")
                for w in app.topLevelWidgets():
                    try:
                        # show() + raise_() helps ensure the window becomes visible and focused
                        w.show()
                        try:
                            # Some PySide/QWidget expose raise_(), use getattr to be safe
                            getattr(w, "raise_")()
                        except Exception:
                            # Not critical; continue
                            pass
                    except Exception:
                        # Continue forcing other widgets even if one fails
                        continue
            except Exception:
                logger.exception("Failed while forcing top-level widgets to show")

        logger.info("AutoFire started successfully")

        # Optionally disable custom stylesheet if requested (useful in CI/debug)
        try:
            if os.environ.get("AUTOFIRE_DISABLE_STYLES") == "1":
                try:
                    app.setStyleSheet("")
                    logger.info("Custom stylesheets disabled via AUTOFIRE_DISABLE_STYLES=1")
                except Exception:
                    logger.exception("Failed to disable stylesheets")
        except Exception:
            pass

        return app.exec()

    except Exception as e:
        logger.error("Failed to start AutoFire: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    main()
