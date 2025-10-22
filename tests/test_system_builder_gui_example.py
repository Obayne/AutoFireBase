import pytest


@pytest.mark.gui
def test_system_builder_gui_example(skip_if_no_qt):
    """Example GUI test template. Replace with real assertions when enabling GUI tests."""
    # Import inside the test so the fixture can skip early if PySide6 isn't present
    from frontend.panels.panel_system_builder import PanelSelectionDialog

    dialog = PanelSelectionDialog()
    # Basic smoke: ensure the dialog can be constructed and has a `panels` attr
    assert hasattr(dialog, "panels")
