import os
import sys


def test_headless_startup():
    """
    Smoke test to verify that the application can start up in a headless environment.
    """
    # Ensure minimal platform for headless startup
    os.environ.setdefault("QT_QPA_PLATFORM", "minimal")

    # Ensure repo root is importable
    repo_root = os.path.dirname(os.path.dirname(__file__))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)

    # Import and construct the AppController (should be headless-safe)
    from app.app_controller import AppController

    ctrl = AppController()

    # Basic assertion: controller exists and exposes the expected attributes
    assert hasattr(ctrl, "model_space_window")
    # Clean up without entering the event loop
    try:
        app.quit()
    except Exception:
        pass
