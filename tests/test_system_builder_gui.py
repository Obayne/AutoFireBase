import pytest


@pytest.mark.gui
def test_system_builder_basic(skip_if_no_qt, qapp):
    """Basic System Builder GUI smoke test.

    Construct PanelSelectionDialog and SystemBuilderPanel and perform a few
    defensive calls. Skip when the GUI components aren't importable.
    """
    try:
        from frontend.panels.panel_system_builder import PanelSelectionDialog, SystemBuilderPanel
    except Exception:
        pytest.skip("System Builder components not available; skipping")

    # Panel selection dialog
    dialog = PanelSelectionDialog()
    if hasattr(dialog, "_load_panel_data"):
        dialog._load_panel_data()
    panels = getattr(dialog, "panels", None)
    assert panels is None or isinstance(panels, (list | tuple))

    # System builder panel
    panel = SystemBuilderPanel()
    # Provide a minimal panel_config if required by implementation
    panel.panel_config = {"panel": {"id": 1, "name": "Test Panel"}}
    if hasattr(panel, "_load_compatible_devices"):
        panel._load_compatible_devices()
    devices = getattr(panel, "devices", None)
    assert devices is None or isinstance(devices, (list | tuple))
