"""Pytest helpers for GUI tests.

Provides a `skip_if_no_qt` fixture and registers a `gui` marker. GUI tests
should import this fixture or use `@pytest.mark.gui` and rely on the fixture to
skip when Qt or pytest-qt aren't available.
"""

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "gui: mark test as GUI (requires PySide6/pytest-qt)")


@pytest.fixture(autouse=False)
def skip_if_no_qt(request):
    """Skip the test if PySide6 or pytest-qt aren't installed on the runner."""
    try:
        import PySide6  # noqa: F401
    except Exception:
        pytest.skip("PySide6 not available; skipping GUI test")


@pytest.fixture(autouse=True)
def ensure_qapp_for_gui(request):
    """Autouse fixture: for tests marked `gui`, attempt to create the pytest-qt
    `qapp` fixture (which constructs a QApplication). If pytest-qt or PySide6
    aren't available, the test will be skipped.
    """
    if "gui" in request.keywords:
        try:
            # request.getfixturevalue will raise if pytest-qt isn't installed
            request.getfixturevalue("qapp")
        except Exception:
            pytest.skip("pytest-qt or PySide6 not available; skipping GUI test")
