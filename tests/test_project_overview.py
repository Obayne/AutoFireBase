"""
Tests for Project Overview Window
"""

import pytest
from PySide6 import QtWidgets

from frontend.windows.project_overview import ProjectOverviewWindow


@pytest.mark.gui
def test_project_overview_window_creation(qtbot):
    """Test that Project Overview window can be created."""

    # Mock app controller
    class MockController:
        def __init__(self):
            self.prefs = {}

        def create_global_menu_bar(self, window):
            pass

    controller = MockController()
    window = ProjectOverviewWindow(controller)
    qtbot.addWidget(window)

    assert window.windowTitle() == "AutoFire - Project Overview"
    assert window.tab_widget.count() == 3  # Overview, Calendar, AI

    # Test notes
    window.notes_edit.setPlainText("Test note")
    assert window.notes_edit.toPlainText() == "Test note"

    # Test progress
    window.progress_spin.setValue(50)
    assert window.progress_bar.value() == 50

    window.close()


def test_ai_assistant_parsing():
    """Test AI assistant command parsing."""
    from frontend.assistant import AssistantDock

    # Mock parent
    parent = QtWidgets.QWidget()
    dock = AssistantDock(parent)

    # Test commands
    response = dock._parse_command("place detector")
    assert "Simulation: Would place a detector" in response

    response = dock._parse_command("draw line")
    assert "Simulation: Would start the Draw Line tool" in response

    response = dock._parse_command("unknown command")
    assert "I understand your request" in response

    parent.deleteLater()
