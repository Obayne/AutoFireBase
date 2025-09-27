import os
import sys
import logging
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(__file__))

try:
    import PySide6

    logger.info("PySide6 imported successfully")
except ImportError as e:
    logger.error("PySide6 import error: %s", e)

try:
    from PySide6 import QtWidgets

    logger.info("PySide6.QtWidgets imported successfully")
except ImportError as e:
    logger.error("PySide6.QtWidgets import error: %s", e)

try:
    from app.main import MainWindow

    logger.info("MainWindow imported successfully")
except ImportError as e:
    logger.error("MainWindow import error: %s", e)

try:
    from db import loader

    logger.info("Database loader imported successfully")
except ImportError as e:
    logger.error("Database loader import error: %s", e)

logger.info("Import check completed")
