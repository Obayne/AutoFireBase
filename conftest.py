"""
Pytest configuration for AutoFire tests.
Provides Qt application fixture for GUI tests.
"""

import os
import sys

import pytest

# Set Qt to use offscreen platform for headless testing before importing Qt
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import QApplication

    QT_AVAILABLE = True
except Exception:
    QT_AVAILABLE = False


@pytest.fixture(scope="session")
def qapp():
    """Provide a Qt application instance for tests."""
    if not QT_AVAILABLE:
        pytest.skip("PySide6 not available; skipping Qt GUI test")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture(scope="session", autouse=True)
def setup_qt():
    """Set up Qt for headless testing."""
    # Already set above before importing Qt
    pass


# Provide a minimal qtbot fixture if pytest-qt is unavailable
try:  # pragma: no cover - exercised indirectly in tests
    from pytestqt.qtbot import QtBot  # type: ignore

    @pytest.fixture
    def qtbot(qapp):
        return QtBot()

except Exception:  # pragma: no cover
    if QT_AVAILABLE:
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
                if QT_AVAILABLE:
                    QtCore.QThread.msleep(int(ms))

        return _QtBot()
