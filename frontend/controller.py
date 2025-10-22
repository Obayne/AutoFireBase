from __future__ import annotations


class SignalStub:
    """Minimal no-op signal-like object used for headless tests.

    It provides a connect() method so UI code can wire signals without a
    full QObject/QSignal implementation.
    """

    def connect(self, *_, **__):
        return None


class AutoFireController:
    """Minimal controller stub for headless testing.

    This class intentionally avoids importing Qt at module import time so
    that tests can safely import it in environments without PySide6.
    """

    def __init__(self) -> None:
        # Placeholder attribute expected by tests; in the full application
        # this would reference the main model space window instance.
        self.model_space_window = object()
        # Provide lightweight default preferences and devices for headless
        # tests that expect controller.prefs and controller.devices_all.
        # Keep values minimal and safe for test runs.
        self.prefs = {
            "px_per_ft": 12.0,
            "snap_label": "grid",
            "snap_step_in": 0.0,
            "grid": 12,
            "snap": True,
        }
        self.devices_all: list = []
        # Minimal signal stubs that provide a connect() method used by UI
        # components during initialization. They are intentionally no-ops so
        # tests don't need a full Qt signal object.
        self.model_space_changed = SignalStub()
        self.prefs_changed = SignalStub()

    def __getattr__(self, name: str):
        # Lazily provide no-op signal stubs for any "*_changed" attribute
        # to keep UI initialization working in headless tests.
        if name.endswith("_changed"):
            return SignalStub()
        raise AttributeError(name)
