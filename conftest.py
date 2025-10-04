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
