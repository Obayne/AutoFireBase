"""
Project Overview Window - Central hub for project management
"""

import os
import sys

# Allow running as `python app\main.py` by fixing sys.path for absolute `app.*` imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCalendarWidget,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from backend.logging_config import setup_logging
from frontend.assistant import AssistantDock

# Ensure logging is configured early
setup_logging()
import logging

_logger = logging.getLogger(__name__)


class ProjectOverviewWindow(QMainWindow):
    """
    Project Overview Window - Central hub for project management.
    Includes organizer sections for notes, milestones, progress, calendar, and AI assistance.
    """

    def __init__(self, app_controller, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.setWindowTitle("AutoFire - Project Overview")
        self.setObjectName("ProjectOverviewWindow")

        # Initialize core attributes
        self.prefs = app_controller.prefs

        # Project data
        self.project_notes = ""
        self.milestones = []
        self.progress_value = 0

        # Setup UI
        self._setup_ui()

        # Load project data
        self._load_project_data()

        self.resize(800, 600)

    def _setup_ui(self):
        """Setup the main UI with tabs."""
        # Create tab widget
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # Overview tab
        self._setup_overview_tab()

        # Calendar tab
        self._setup_calendar_tab()

        # AI Assistant tab
        self._setup_ai_tab()

        # Setup menus
        self._setup_menus()

    def _setup_overview_tab(self):
        """Setup the overview tab with notes, milestones, progress."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Notes section
        notes_group = QtWidgets.QGroupBox("Project Notes")
        notes_layout = QVBoxLayout(notes_group)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter project notes, descriptions, etc.")
        notes_layout.addWidget(self.notes_edit)
        layout.addWidget(notes_group)

        # Milestones section
        milestones_group = QtWidgets.QGroupBox("Milestones")
        milestones_layout = QVBoxLayout(milestones_group)

        self.milestones_list = QListWidget()
        milestones_layout.addWidget(self.milestones_list)

        # Add milestone controls
        controls_layout = QHBoxLayout()
        self.milestone_input = QtWidgets.QLineEdit()
        self.milestone_input.setPlaceholderText("New milestone")
        add_btn = QPushButton("Add Milestone")
        add_btn.clicked.connect(self._add_milestone)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_milestone)

        controls_layout.addWidget(self.milestone_input)
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(remove_btn)
        milestones_layout.addLayout(controls_layout)

        layout.addWidget(milestones_group)

        # Progress section
        progress_group = QtWidgets.QGroupBox("Project Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        progress_controls = QHBoxLayout()
        progress_label = QLabel("Progress (%):")
        self.progress_spin = QtWidgets.QSpinBox()
        self.progress_spin.setRange(0, 100)
        self.progress_spin.valueChanged.connect(self._update_progress)
        progress_controls.addWidget(progress_label)
        progress_controls.addWidget(self.progress_spin)
        progress_controls.addStretch()

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addLayout(progress_controls)

        layout.addWidget(progress_group)

        self.tab_widget.addTab(tab, "Overview")

    def _setup_calendar_tab(self):
        """Setup the calendar tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self._on_date_selected)

        # Selected date info
        self.date_info = QTextEdit()
        self.date_info.setPlaceholderText("Notes for selected date...")
        self.date_info.setMaximumHeight(100)

        layout.addWidget(self.calendar)
        layout.addWidget(QLabel("Date Notes:"))
        layout.addWidget(self.date_info)

        self.tab_widget.addTab(tab, "Calendar")

    def _setup_ai_tab(self):
        """Setup the AI Assistant tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Embed AI assistant
        self.ai_dock = AssistantDock(self)
        layout.addWidget(self.ai_dock)

        self.tab_widget.addTab(tab, "AI Assistant")

    def _setup_menus(self):
        """Setup menus using global menu bar."""
        # Use global menu bar from app controller
        self.app_controller.create_global_menu_bar(self)

    def _add_milestone(self):
        """Add a new milestone."""
        text = self.milestone_input.text().strip()
        if text:
            item = QListWidgetItem(text)
            item.setCheckState(Qt.Unchecked)
            self.milestones_list.addItem(item)
            self.milestone_input.clear()
            self._save_project_data()

    def _remove_milestone(self):
        """Remove selected milestone."""
        current = self.milestones_list.currentItem()
        if current:
            self.milestones_list.takeItem(self.milestones_list.row(current))
            self._save_project_data()

    def _update_progress(self, value):
        """Update progress bar."""
        self.progress_bar.setValue(value)
        self._save_project_data()

    def _on_date_selected(self, date):
        """Handle date selection in calendar."""
        # Could load/save notes per date, but for now just placeholder
        pass

    def _load_project_data(self):
        """Load project-specific data."""
        # For now, use prefs or project file
        # TODO: Integrate with project save/load
        self.project_notes = self.prefs.get("project_notes", "")
        self.notes_edit.setPlainText(self.project_notes)

        self.progress_value = self.prefs.get("project_progress", 0)
        self.progress_spin.setValue(self.progress_value)
        self.progress_bar.setValue(self.progress_value)

        # Load milestones
        milestones_data = self.prefs.get("project_milestones", [])
        for ms in milestones_data:
            item = QListWidgetItem(ms.get("text", ""))
            item.setCheckState(Qt.Checked if ms.get("completed", False) else Qt.Unchecked)
            self.milestones_list.addItem(item)

    def _save_project_data(self):
        """Save project-specific data."""
        # TODO: Integrate with project save/load
        self.prefs["project_notes"] = self.notes_edit.toPlainText()
        self.prefs["project_progress"] = self.progress_spin.value()

        # Save milestones
        milestones = []
        for i in range(self.milestones_list.count()):
            item = self.milestones_list.item(i)
            milestones.append({"text": item.text(), "completed": item.checkState() == Qt.Checked})
        self.prefs["project_milestones"] = milestones

        self.app_controller.save_prefs()

    def closeEvent(self, event):
        """Handle window close."""
        self._save_project_data()
        super().closeEvent(event)
