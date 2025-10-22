"""
Pytest configuration for AutoFire tests.
Provides Qt application fixture for GUI tests.
"""

import os
import sys

import pytest


@pytest.fixture(scope="session")
def qapp():
    """Provide a Qt application instance for tests when PySide6 is available."""
    try:
        from PySide6.QtWidgets import QApplication
    except Exception:
        pytest.skip("PySide6 not available; skipping Qt GUI test")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture(scope="session", autouse=True)
def setup_qt():
    """Set up Qt for headless testing when PySide6 is available."""
    # Set Qt to use offscreen platform for headless testing
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


# Provide a minimal qtbot fixture if pytest-qt is unavailable
try:  # pragma: no cover - exercised indirectly in tests
    from pytestqt.qtbot import QtBot  # type: ignore

    @pytest.fixture
    def qtbot(qapp):
        return QtBot()

except Exception:  # pragma: no cover

    @pytest.fixture
    def qtbot(qapp):
        try:
            from PySide6 import QtCore
        except Exception:
            pytest.skip("PySide6 not available; skipping Qt GUI test")

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
