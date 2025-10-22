import pytest


class SignalStub:
    """Minimal no-op signal-like object used for headless tests.

    It provides a connect() method so UI code can wire signals without a
    full QObject/QSignal implementation.
    """

    def connect(self, *_, **__):
        return None


class TestAutoFireController:
    """Lightweight controller used only for tests.

    This mirrors the small surface tests expect (prefs, devices_all and some
    *_changed signals) without importing heavy Qt modules at import-time.
    """

    def __init__(self) -> None:
        self.model_space_window = object()
        self.prefs = {
            "px_per_ft": 12.0,
            "snap_label": "grid",
            "snap_step_in": 0.0,
            "grid": 12,
            "snap": True,
        }
        self.devices_all: list = []
        self.model_space_changed = SignalStub()
        self.prefs_changed = SignalStub()

    def __getattr__(self, name: str):
        if name.endswith("_changed"):
            return SignalStub()
        raise AttributeError(name)


@pytest.fixture
def app_controller():
    """Provide a test-safe controller object for tests that need it.

    Tests should accept an "app_controller" argument to get this stub rather
    than constructing the real application controller which imports Qt.
    """
    return TestAutoFireController()


@pytest.fixture
def qapp():
    """Provide a QApplication when PySide6 is available; otherwise skip.

    Tests that require a running Qt application should request the `qapp`
    fixture. If PySide6 is not installed in the environment the fixture will
    skip the test so CI can run in headless environments.
    """
    try:
        from PySide6.QtWidgets import QApplication
    except Exception:
        pytest.skip("PySide6 not available; skipping Qt GUI test")

    app = QApplication.instance() or QApplication([])
    yield app
    try:
        app.quit()
    except Exception:
        pass
