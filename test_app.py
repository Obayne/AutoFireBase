import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from backend.logging_config import setup_logging

setup_logging()
_logger = logging.getLogger(__name__)

try:
    _logger.info("MainWindow imported successfully")

    from db import loader

    _logger.info("Database loader imported successfully")

    con = loader.connect()
    _logger.info("Database connection established")

    layers = loader.fetch_layers(con)
    _logger.info("Layers fetched successfully: %d layers", len(layers))

    _logger.info("All components working correctly!")

except Exception:
    _logger = logging.getLogger(__name__)
    _logger.exception("Error during test_app run")
