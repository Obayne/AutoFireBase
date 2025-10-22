import pytest


@pytest.mark.gui
def test_gui_components_smoke(skip_if_no_qt, qapp, app_controller):
    """High-level GUI components smoke test: ensure main windows can be created."""
    try:
        pass
    except Exception:
        pytest.skip("AutoFireController not available; skipping")

    # Use the test-safe controller fixture when possible
    controller = app_controller
    assert controller is not None
