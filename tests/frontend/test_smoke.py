import pytest


@pytest.mark.skipif("PyQt5" not in globals(), reason="Qt not installed")
def test_import_frontend_modules():
    # Basic import smoke test; avoids running the event loop in CI.
    import frontend.app  # noqa: F401
    import frontend.main_window  # noqa: F401

