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

        # TEMPORARILY SKIP SPLASH SCREENS - go directly to System Builder
        # TODO: Migrate splash screen project info into System Builder interface
        logger.info("Skipping splash screens, starting directly with System Builder...")

        # Create and retain a global reference to the application controller
        global _GLOBAL_CONTROLLER
        _GLOBAL_CONTROLLER = AutoFireController()

        logger.info("AutoFire started successfully")
        return app.exec()

    except Exception as e:
        logger.error("Failed to start AutoFire: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    main()
