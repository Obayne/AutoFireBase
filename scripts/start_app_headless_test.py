"""Start the application briefly in a headless/minimal Qt platform to smoke-test startup.

This script sets QT_QPA_PLATFORM to 'minimal' and creates the AppController, waits a few
seconds for initialization, then exits. It is intended for CI or local smoke tests only.
"""

import os
import sys
import time

# Prefer minimal/offscreen platform for headless startup on Windows
os.environ.setdefault("QT_QPA_PLATFORM", "minimal")


def run():
    print("Starting headless app (minimal)...")
    # Ensure repo imports work
    root = os.path.dirname(os.path.dirname(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    try:
        from PySide6.QtWidgets import QApplication

        from app.app_controller import AppController

        app = QApplication(sys.argv)
        # Create app controller which should instantiate windows (headless-safe guards exist)
        ctrl = AppController()
        # Give it a moment to initialize
        time.sleep(2)
        print("AppController initialized successfully; exiting.")
        try:
            app.quit()
        except Exception:
            pass
    except Exception as e:
        print("Error during headless startup:", e)
        raise


if __name__ == "__main__":
    run()
