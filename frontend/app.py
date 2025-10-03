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

        # Create and run the application controller
        controller = AutoFireController()

        logger.info("AutoFire started successfully")
        return app.exec()

    except Exception as e:
        logger.error(f"Failed to start AutoFire: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    main()
