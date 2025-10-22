import pytest


@pytest.mark.gui
def test_model_space_basic(skip_if_no_qt, qapp, app_controller):
    """Basic Model Space GUI smoke test that constructs the ModelSpaceWindow."""
    try:
        from frontend.windows.model_space import ModelSpaceWindow
    except Exception:
        pytest.skip("ModelSpaceWindow not available; skipping")

    controller = app_controller
    window = ModelSpaceWindow(controller)
    assert hasattr(window, "device_tree")
