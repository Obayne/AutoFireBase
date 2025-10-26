"""
Pytest configuration for AutoFire tests.
Provides Qt application fixture for GUI tests.
"""

import importlib.util
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


@pytest.fixture(scope="session", autouse=True)
def _qt_session_teardown():
    """Best-effort cleanup of Qt threads to avoid teardown noise/exits.

    Ensures any background QThreads are asked to stop by emitting aboutToQuit,
    and waits briefly for thread pools to finish. This helps prevent
    "QThread: Destroyed while thread '' is still running" at process exit.
    """
    yield
    try:
        from PySide6 import QtCore, QtWidgets  # type: ignore

        app = QtWidgets.QApplication.instance()
        if app is not None:
            try:
                # Emit the aboutToQuit signal so any connected slots can stop threads
                app.aboutToQuit.emit()
            except Exception:
                pass

        # Give Qt a moment to process any posted events and finish worker threads
        try:
            QtCore.QCoreApplication.processEvents()
        except Exception:
            pass
        try:
            QtCore.QThread.msleep(50)
        except Exception:
            pass
        try:
            QtCore.QThreadPool.globalInstance().waitForDone(1000)
        except Exception:
            pass
    except Exception:
        # If PySide6 isn't present or any import fails, just ignore
        pass


# Provide a minimal qtbot fixture only if pytest-qt is unavailable. If
# pytest-qt is installed it exposes a fully-featured `qtbot` fixture and we
# must not override it here.
if importlib.util.find_spec("pytestqt") is None:

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

    @pytest.fixture(autouse=True)
    def ensure_qapp_for_gui(request):
        """Ensure a QApplication is constructed for tests marked with `gui`.

        Uses pytest-qt's `qapp` fixture when available; otherwise uses the
        repository's `qapp` fixture defined above. Skips the test if PySide6
        isn't installed.
        """
        if "gui" in request.keywords:
            try:
                request.getfixturevalue("qapp")
            except Exception:
                pytest.skip("pytest-qt or PySide6 not available; skipping GUI test")
