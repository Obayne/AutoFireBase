"""
Pytest configuration for AutoFire tests.
Provides Qt application fixture for GUI tests.
"""

import sys

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Provide a Qt application instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture(scope="session", autouse=True)
def setup_qt():
    """Set up Qt for headless testing."""
    # Set Qt to use offscreen platform for headless testing
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


# Provide a minimal qtbot fixture if pytest-qt is unavailable
try:  # pragma: no cover - exercised indirectly in tests
    from pytestqt.qtbot import QtBot  # type: ignore

    @pytest.fixture
    def qtbot(qapp):
        return QtBot()

except Exception:  # pragma: no cover
    from PySide6 import QtCore

    @pytest.fixture
    def qtbot(qapp):
        class _QtBot:
            def __init__(self) -> None:
                self._widgets = []

            def addWidget(self, w):
                # Store for lifetime management; tests only require registration
                self._widgets.append(w)

            # Minimal helpers used by some tests (no-ops here)
            def wait(self, ms: int):
                QtCore.QThread.msleep(int(ms))

        return _QtBot()
