#!/usr/bin/env python3
"""Test script to debug device loading thread issue."""

import logging
import os
import sys

# Setup path
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication

from backend.catalog import load_catalog

# Setup logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeviceLoader(QObject):
    devices_ready = Signal(list)
    error = Signal(str)

    @Slot()
    def run(self):
        logger.info("DeviceLoader.run() started")
        try:
            logger.info("Calling load_catalog()...")
            devs = load_catalog()
            logger.info(f"load_catalog() returned {len(devs)} devices")
            logger.info("Emitting devices_ready signal...")
            self.devices_ready.emit(devs)
            logger.info("devices_ready signal emitted")
        except Exception as e:
            logger.error(f"DeviceLoader error: {e}")
            import traceback

            traceback.print_exc()
            self.error.emit(str(e))


def test_device_loading():
    logger.info("Starting device loading test...")

    app = QApplication.instance() or QApplication(sys.argv)

    loader = DeviceLoader()
    thread = QThread()
    loader.moveToThread(thread)

    def on_devices_ready(devs):
        logger.info(f"✅ SUCCESS: Received {len(devs)} devices")
        app.quit()

    def on_error(msg):
        logger.error(f"❌ ERROR: {msg}")
        app.quit()

    loader.devices_ready.connect(on_devices_ready)
    loader.error.connect(on_error)
    thread.started.connect(loader.run)
    thread.finished.connect(thread.deleteLater)

    # Timeout in case thread doesn't respond
    def timeout():
        logger.error("❌ TIMEOUT: Device loading thread didn't respond in 10 seconds")
        thread.quit()
        thread.wait(1000)
        app.quit()

    QTimer.singleShot(10000, timeout)

    logger.info("Starting thread...")
    thread.start()

    logger.info("Starting event loop...")
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_device_loading())
