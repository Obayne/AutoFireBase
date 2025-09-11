import sys, traceback
from PySide6 import QtWidgets
from . import logger_bridge

def excepthook(exc_type, exc, tb):
    logger = logger_bridge.get_app_logger()
    lines = "".join(traceback.format_exception(exc_type, exc, tb))
    try:
        logger.error("UNCAUGHT EXCEPTION\n" + lines)
    except Exception:
        pass
    try:
        QtWidgets.QMessageBox.critical(None, "Auto-Fire Error", lines[:2000])
    except Exception:
        pass
sys.excepthook = excepthook