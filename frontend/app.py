"""
Frontend application - Main AutoFire GUI application.
Clean, modular entry point for the fire alarm CAD application.
"""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

# Import our clean application controller
from frontend.controller import AutoFireController
from frontend.project_dialog import show_new_project_dialog
from frontend.splash import show_splash_screen


def main() -> int:
    """Main application entry point."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting AutoFire...")

    try:
        # Create Qt application
        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName("AutoFire")
        app.setApplicationVersion("0.8.0")

        # Show splash screen
        logger.info("Showing splash screen...")
        project_path = show_splash_screen()
        logger.info(f"Splash screen result: {project_path}")

        if project_path is None:
            # New project requested
            logger.info("New project requested, showing project dialog...")
            project_data = show_new_project_dialog()
            if project_data is None:
                # User cancelled
                logger.info("Project creation cancelled")
                return 0
            logger.info(f"Creating new project: {project_data.get('name', 'Unnamed')}")
        else:
            # Existing project opened
            logger.info(f"Opening project: {project_path}")

        # Create and run the application controller
        controller = AutoFireController()

        logger.info("AutoFire started successfully")
        return app.exec()

    except Exception as e:
        logger.error(f"Failed to start AutoFire: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    main()
