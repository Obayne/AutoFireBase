"""Event handlers for MainWindow.

Extracted from main.py to reduce file size and improve maintainability.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.main import MainWindow


def setup_event_handlers(window: MainWindow) -> None:
    """Set up event handlers for MainWindow."""
    # Assign event handler functions to window instance
    window.new_project = lambda: new_project(window)
    window.save_project_as = lambda: save_project_as(window)
    window.open_project = lambda: open_project(window)
    window.start_text = lambda: start_text(window)
    window.start_mtext = lambda: start_mtext(window)
    window.start_freehand = lambda: start_freehand(window)
    window.start_leader = lambda: start_leader(window)
    window.start_cloud = lambda: start_cloud(window)
    window.start_dimension = lambda: start_dimension(window)
    window.start_measure = lambda: start_measure(window)


def new_project(window: MainWindow) -> None:
    """Create a new project."""
    window.clear_underlay()
    for it in list(window.layer_devices.childItems()):
        it.scene().removeItem(it)
    for it in list(window.layer_wires.childItems()):
        it.scene().removeItem(it)
    window.push_history()
    window.statusBar().showMessage("New project")


def save_project_as(window: MainWindow) -> None:
    """Save the current project to a file."""
    import json
    import os
    import zipfile

    from PySide6.QtWidgets import QFileDialog, QMessageBox

    p, _ = QFileDialog.getSaveFileName(window, "Save Project As", "", "LV CAD Bundle (*.lvcad)")
    if not p:
        return
    if not p.lower().endswith(".lvcad"):
        p += ".lvcad"
    try:
        data = window.serialize_state()
        with zipfile.ZipFile(p, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("project.json", json.dumps(data, indent=2))
        window.statusBar().showMessage(f"Saved: {os.path.basename(p)}")
    except Exception as ex:
        QMessageBox.critical(window, "Save Project Error", str(ex))


def open_project(window: MainWindow) -> None:
    """Open a project from a file."""
    import json
    import os
    import zipfile

    from PySide6.QtWidgets import QFileDialog, QMessageBox

    p, _ = QFileDialog.getOpenFileName(window, "Open Project", "", "LV CAD Bundle (*.lvcad)")
    if not p:
        return
    try:
        with zipfile.ZipFile(p, "r") as z:
            data = json.loads(z.read("project.json").decode("utf-8"))
        window.load_state(data)
        window.push_history()
        window.statusBar().showMessage(f"Opened: {os.path.basename(p)}")
    except Exception as ex:
        QMessageBox.critical(window, "Open Project Error", str(ex))


def start_text(window: MainWindow) -> None:
    """Start the text tool."""
    from PySide6.QtWidgets import QMessageBox

    try:
        window.text_tool.start()
    except Exception as ex:
        QMessageBox.critical(window, "Text Tool Error", str(ex))


def start_mtext(window: MainWindow) -> None:
    """Start the mtext tool."""
    from PySide6.QtWidgets import QMessageBox

    try:
        window.mtext_tool.start()
    except Exception as ex:
        QMessageBox.critical(window, "MText Tool Error", str(ex))


def start_freehand(window: MainWindow) -> None:
    """Start the freehand tool."""
    try:
        window.freehand_tool.start()
    except Exception as ex:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(window, "Freehand Tool Error", str(ex))


def start_leader(window: MainWindow) -> None:
    """Start the leader tool."""
    try:
        window.leader_tool.start()
    except Exception as ex:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(window, "Leader Tool Error", str(ex))


def start_cloud(window: MainWindow) -> None:
    """Start the revision cloud tool."""
    try:
        window.cloud_tool.start()
    except Exception as ex:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(window, "Revision Cloud Tool Error", str(ex))


def start_dimension(window: MainWindow) -> None:
    """Start the dimension tool."""
    from PySide6.QtWidgets import QMessageBox

    try:
        window.dim_tool.start()
    except Exception as ex:
        QMessageBox.critical(window, "Dimension Tool Error", str(ex))


def start_measure(window: MainWindow) -> None:
    """Start the measure tool."""
    from PySide6.QtWidgets import QMessageBox

    try:
        window.measure_tool.start()
    except Exception as ex:
        QMessageBox.critical(window, "Measure Tool Error", str(ex))
