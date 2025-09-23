"""Paperspace minimal mode behavior tests.

Verifies that in minimal mode we stay in Model space and skip Paperspace tabs.
This is a focused, non-brittle test to support v1 testing readiness.
"""

from PySide6 import QtWidgets


def test_minimal_mode_stays_on_model(monkeypatch):
    monkeypatch.setenv("AF_PAPERSPACE_MODE", "minimal")
    # Import late to ensure env has been set
    import app.main as app_main

    # Monkeypatch heavy UI builders to keep the test lightweight
    monkeypatch.setattr(app_main.MainWindow, "_build_left_panel", lambda self: None, raising=False)
    monkeypatch.setattr(app_main.MainWindow, "_build_layers_and_props_dock", lambda self: None, raising=False)
    monkeypatch.setattr(app_main.MainWindow, "_build_dxf_layers_dock", lambda self: None, raising=False)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = app_main.create_window()

    # Only Model tab should exist in minimal mode
    assert hasattr(win, "tab_widget")
    assert win.tab_widget.count() == 1
    assert win.tab_widget.tabText(0) == "Model"

    # Space controls should be hidden in minimal mode
    assert getattr(win, "space_combo").isHidden()
    assert getattr(win, "space_lock").isHidden()

    # Toggling to Paper space should be a no-op
    win.toggle_paper_space(True)
    assert win.tab_widget.currentIndex() == 0
    assert win.tab_widget.tabText(0) == "Model"

    # Verify Layout menu actions are hidden/disabled in minimal mode
    mb = win.menuBar()
    layout_menu = None
    for a in mb.actions():
        if a.menu() and a.text().replace("&", "").strip().lower() == "layout":
            layout_menu = a.menu()
            break
    assert layout_menu is not None
    blocked = {"viewport", "paper space", "model space", "page frame", "title block", "page setup", "print scale"}
    for act in layout_menu.actions():
        t = (act.text() or "").lower()
        if any(k in t for k in blocked):
            assert not act.isEnabled() or not act.isVisible()

    # Cleanup the window to avoid leaking widgets between tests
    win.close()
