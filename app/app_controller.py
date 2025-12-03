"""
App Controller - Central coordinator for multi-window AutoFire application
"""

import json
import os
import sys
import zipfile
from typing import TYPE_CHECKING, Any

# Allow running as `python app\main.py` by fixing sys.path for absolute `app.*` imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
)

from app import catalog
from app.logging_config import setup_logging

if TYPE_CHECKING:
    from app.model_space_window import ModelSpaceWindow
    from app.paperspace_window import PaperspaceWindow

    # from app.summary_window import SummaryWindow  # Not yet implemented

# Ensure logging is configured early
setup_logging()
import logging

_logger = logging.getLogger(__name__)


class AppController(QMainWindow):
    """
    Central application controller for multi-window AutoFire.
    Acts as a dummy main window for boot.py compatibility while managing multiple windows.
    """

    # Signals for inter-window communication
    model_space_changed = QtCore.Signal(dict)  # Emitted when model space content changes
    paperspace_changed = QtCore.Signal(dict)  # Emitted when paperspace content changes
    project_changed = QtCore.Signal(str)  # Emitted when project state changes

    def __init__(self):
        # Initialize as QMainWindow first (QApplication should already exist)
        super().__init__()

        # Get the existing Qt application
        self.app = QApplication.instance()

        self.setWindowTitle("LV CAD Controller")
        # Hide this dummy window
        self.hide()

        # Initialize preferences
        self.prefs = self._load_prefs()

    def _apply_modern_theme(self):
        """Apply modern dark theme to the application."""
        dark_theme = """
        /* Modern Dark Theme for AutoFire */
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }

        QDockWidget {
            background-color: #3a3a3a;
            color: #ffffff;
            border: 1px solid #555;
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }

        QDockWidget::title {
            background-color: #4a4a4a;
            color: #ffffff;
            padding: 6px;
            border-bottom: 1px solid #555;
            font-weight: bold;
        }

        QTreeWidget, QListWidget, QTextEdit, QLineEdit {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666;
            border-radius: 4px;
            padding: 4px;
        }

        QTreeWidget::item:hover, QListWidget::item:hover {
            background-color: #505050;
        }

        QTreeWidget::item:selected, QListWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }

        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: 500;
        }

        QPushButton:hover {
            background-color: #106ebe;
        }

        QPushButton:pressed {
            background-color: #005a9e;
        }

        QPushButton:disabled {
            background-color: #666;
            color: #999;
        }

        QMenuBar {
            background-color: #2b2b2b;
            color: #ffffff;
            border-bottom: 1px solid #555;
        }

        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
        }

        QMenuBar::item:selected {
            background-color: #4a4a4a;
        }

        QMenu {
            background-color: #3a3a3a;
            color: #ffffff;
            border: 1px solid #555;
        }

        QMenu::item {
            padding: 6px 20px;
        }

        QMenu::item:selected {
            background-color: #0078d4;
        }

        QStatusBar {
            background-color: #2b2b2b;
            color: #ffffff;
            border-top: 1px solid #555;
        }

        QGraphicsView {
            background-color: #1e1e1e;
            border: 1px solid #555;
        }

        /* Scroll bars */
        QScrollBar:vertical {
            background-color: #404040;
            width: 16px;
            border-radius: 8px;
        }

        QScrollBar::handle:vertical {
            background-color: #666;
            border-radius: 8px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #888;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
        }
        """
        self.app.setStyleSheet(dark_theme)

        # Load preferences
        self.prefs = self._load_prefs()

        # Load device catalog
        self.devices_all = catalog.load_catalog()

        # Window management
        self.model_space_window: ModelSpaceWindow | None = None
        self.paperspace_window: PaperspaceWindow | None = None
        self.summary_window: Any | None = None  # SummaryWindow not yet implemented

        # Application state
        self.current_project_path: str | None = None
        self.is_modified = False

        # Setup global menus first
        self._setup_global_menus()

        # Show the actual application windows
        self._initialize_windows()

    def show(self):
        """Override show() to do nothing - this controller window should remain hidden."""
        # The controller window is a dummy for boot.py compatibility and should not be shown
        pass

    def _setup_global_menus(self):
        """Setup global menu actions that work across windows."""
        # File menu actions
        self.action_new_project = QtGui.QAction("New Project", self)
        self.action_new_project.setShortcut(QtGui.QKeySequence.StandardKey.New)
        self.action_new_project.triggered.connect(self.new_project)

        self.action_open_project = QtGui.QAction("Open Project...", self)
        self.action_open_project.setShortcut(QtGui.QKeySequence.StandardKey.Open)
        self.action_open_project.triggered.connect(self.open_project)

        self.action_save_project = QtGui.QAction("Save Project", self)
        self.action_save_project.setShortcut(QtGui.QKeySequence.StandardKey.Save)
        self.action_save_project.triggered.connect(self.save_project)

        self.action_save_project_as = QtGui.QAction("Save Project As...", self)
        self.action_save_project_as.setShortcut(QtGui.QKeySequence.StandardKey.SaveAs)
        self.action_save_project_as.triggered.connect(self.save_project_as)

        # Window menu actions
        self.action_show_model_space = QtGui.QAction("Model Space", self)
        self.action_show_model_space.triggered.connect(self.show_model_space)

        self.action_show_paperspace = QtGui.QAction("Paperspace", self)
        self.action_show_paperspace.triggered.connect(self.show_paperspace)

        self.action_show_summary = QtGui.QAction("Summary", self)
        self.action_show_summary.triggered.connect(self.show_summary_window)

        self.action_arrange_windows = QtGui.QAction("Arrange Windows", self)
        self.action_arrange_windows.triggered.connect(self.arrange_windows)

    def create_global_menu_bar(self, parent_window):
        """Create a standardized menu bar for a window."""
        menubar = parent_window.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.action_new_project)
        file_menu.addAction(self.action_open_project)
        file_menu.addSeparator()
        file_menu.addAction(self.action_save_project)
        file_menu.addAction(self.action_save_project_as)

        # Window menu
        window_menu = menubar.addMenu("&Window")
        window_menu.addAction(self.action_show_model_space)
        window_menu.addAction(self.action_show_paperspace)
        window_menu.addAction(self.action_show_summary)
        window_menu.addSeparator()
        window_menu.addAction(self.action_arrange_windows)

        return menubar

    def _initialize_windows(self):
        """Initialize and show the main application windows."""
        # Show initial windows
        self.show_model_space()
        self.show_paperspace()

        if self.prefs.get("show_summary_window", False):
            self.show_summary_window()

        # Arrange windows
        QtCore.QTimer.singleShot(100, self.arrange_windows)

        # Ensure model space is visible and on top initially
        QtCore.QTimer.singleShot(200, self._ensure_model_space_visible)

    def _ensure_model_space_visible(self):
        """Ensure the model space window is visible and activated."""
        if self.model_space_window:
            self.model_space_window.show()
            self.model_space_window.raise_()
            self.model_space_window.activateWindow()

    def _load_prefs(self):
        """Load user preferences."""
        prefs_path = os.path.join(os.path.expanduser("~"), "AutoFire", "prefs.json")
        try:
            with open(prefs_path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._get_default_prefs()

    def _get_default_prefs(self):
        """Get default preferences."""
        return {
            "px_per_ft": 12.0,
            "grid": 12,
            "snap": True,
            "show_coverage": True,
            "page_size": "Letter",
            "page_orient": "Landscape",
            "page_margin_in": 0.5,
            "grid_opacity": 0.25,
            "grid_width_px": 0.0,
            "grid_major_every": 5,
            "print_in_per_ft": 0.125,
            "print_dpi": 300,
            "theme": "dark",
            # Project metadata
            "proj_project": "",
            "proj_address": "",
            "proj_sheet": "",
            "proj_date": "",
            "proj_by": "",
            # Multi-window settings
            "multiview_enabled": True,
            "show_summary_window": False,
            "window_positions": {},
        }

    def save_prefs(self):
        """Save user preferences."""
        prefs_path = os.path.join(os.path.expanduser("~"), "AutoFire", "prefs.json")
        os.makedirs(os.path.dirname(prefs_path), exist_ok=True)
        try:
            with open(prefs_path, "w") as f:
                json.dump(self.prefs, f, indent=2)
        except Exception as e:
            _logger.error(f"Failed to save preferences: {e}")

    def show_model_space(self):
        """Show or create the model space window."""
        if self.model_space_window is None:
            try:
                from app.model_space_window import ModelSpaceWindow

                self.model_space_window = ModelSpaceWindow(self)
                self.model_space_window.show()
                self.model_space_window.raise_()
                self.model_space_window.activateWindow()
            except Exception as e:
                print(f"Error creating model space window: {e}")
                import traceback

                traceback.print_exc()
                return
        else:
            self.model_space_window.raise_()
            self.model_space_window.activateWindow()

    def show_paperspace(self):
        """Show or create the paperspace window."""
        if self.paperspace_window is None:
            from app.paperspace_window import PaperspaceWindow

            # Pass the model space scene to paperspace
            model_scene = self.model_space_window.scene if self.model_space_window else None
            self.paperspace_window = PaperspaceWindow(self, model_scene)
            self.paperspace_window.show()
            self.paperspace_window.raise_()
            self.paperspace_window.activateWindow()
        else:
            self.paperspace_window.raise_()
            self.paperspace_window.activateWindow()

    def show_summary_window(self):
        """Show or create the summary window."""
        if not self.prefs.get("show_summary_window", False):
            return

        if self.summary_window is None:
            # SummaryWindow will be implemented later
            _logger.info("Summary window not yet implemented")
        else:
            self.summary_window.raise_()
            self.summary_window.activateWindow()

    def arrange_windows(self):
        """Arrange windows for optimal multi-monitor workflow."""
        screens = QApplication.screens()
        if len(screens) >= 2:
            # Multi-monitor setup
            primary = screens[0].geometry()
            secondary = screens[1].geometry()

            # Model space on primary monitor
            if self.model_space_window:
                self.model_space_window.setGeometry(primary)

            # Paperspace on secondary monitor
            if self.paperspace_window:
                self.paperspace_window.setGeometry(secondary)

            # Summary window overlay if enabled
            if self.summary_window:
                # Position summary window on secondary monitor
                summary_geom = QtCore.QRect(secondary.x() + 50, secondary.y() + 50, 400, 600)
                self.summary_window.setGeometry(summary_geom)
        else:
            # Single monitor - tile windows
            screen = screens[0].geometry()
            width = screen.width()
            height = screen.height()

            # Model space - left half
            if self.model_space_window:
                self.model_space_window.setGeometry(0, 0, width // 2, height)
                self.model_space_window.show()
                self.model_space_window.raise_()

            # Paperspace - right half, top
            if self.paperspace_window:
                self.paperspace_window.setGeometry(width // 2, 0, width // 2, height // 2)
                self.paperspace_window.show()

            # Summary - right half, bottom
            if self.summary_window:
                self.summary_window.setGeometry(width // 2, height // 2, width // 2, height // 2)
                self.summary_window.show()

    def new_project(self):
        """Create a new project."""
        # Close existing project
        self.close_project()

        # Reset windows
        if self.model_space_window:
            self.model_space_window._initialize_tools()
        if self.paperspace_window:
            # Reset paperspace to single sheet
            self.paperspace_window.sheets = []
            self.paperspace_window._create_new_sheet()

        self.current_project_path = None
        self.is_modified = False
        self._update_window_titles()

    def open_project(self):
        """Open an existing project."""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            None, "Open Project", "", "AutoFire Bundle (*.autofire)"
        )

        if not file_path:
            return

        try:
            with zipfile.ZipFile(file_path, "r") as z:
                data = json.loads(z.read("project.json").decode("utf-8"))

            self.load_project_state(data)
            self.current_project_path = file_path
            self.is_modified = False
            self._update_window_titles()

        except Exception as e:
            QMessageBox.critical(None, "Open Project Error", str(e))

    def save_project(self):
        """Save the current project."""
        if not self.current_project_path:
            self.save_project_as()
            return

        try:
            data = self.serialize_project_state()
            with zipfile.ZipFile(
                self.current_project_path, "w", compression=zipfile.ZIP_DEFLATED
            ) as z:
                z.writestr("project.json", json.dumps(data, indent=2))

            self.is_modified = False
            self._update_window_titles()

        except Exception as e:
            QMessageBox.critical(None, "Save Project Error", str(e))

    def save_project_as(self):
        """Save project with a new filename."""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save Project As", "", "AutoFire Bundle (*.autofire)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".autofire"):
            file_path += ".autofire"

        self.current_project_path = file_path
        self.save_project()

    def serialize_project_state(self):
        """Serialize the complete project state."""
        data = {
            "version": "1.0",
            "metadata": {
                "created": QtCore.QDateTime.currentDateTime().toString(),
                "app_version": self.app.applicationVersion(),
            },
            "preferences": self.prefs.copy(),
        }

        # Get model space state
        if self.model_space_window:
            data["model_space"] = self.model_space_window.get_scene_state()

        # Get paperspace state
        if self.paperspace_window:
            data["paperspace"] = self.paperspace_window.get_sheets_state()

        return data

    def load_project_state(self, data):
        """Load project state from serialized data."""
        # Load preferences
        if "preferences" in data:
            self.prefs.update(data["preferences"])
            self.save_prefs()

        # Load model space
        if "model_space" in data and self.model_space_window:
            self.model_space_window.load_scene_state(data["model_space"])

        # Load paperspace
        if "paperspace" in data and self.paperspace_window:
            self.paperspace_window.load_sheets_state(data["paperspace"])

    def close_project(self):
        """Close the current project."""
        # Clear model space
        if self.model_space_window:
            # Clear devices, wires, sketch
            for item in self.model_space_window.devices_group.childItems():
                item.scene().removeItem(item)
            for item in self.model_space_window.layer_wires.childItems():
                item.scene().removeItem(item)
            for item in self.model_space_window.layer_sketch.childItems():
                item.scene().removeItem(item)

        # Reset paperspace
        if self.paperspace_window:
            self.paperspace_window.sheets = []
            self.paperspace_window._create_new_sheet()

    def _update_window_titles(self):
        """Update window titles with project information."""
        project_name = "Untitled"
        if self.current_project_path:
            project_name = os.path.splitext(os.path.basename(self.current_project_path))[0]

        modified_indicator = " *" if self.is_modified else ""

        if self.model_space_window:
            self.model_space_window.setWindowTitle(
                f"AutoFire - Model Space - {project_name}{modified_indicator}"
            )

        if self.paperspace_window:
            self.paperspace_window.setWindowTitle(
                f"AutoFire - Paperspace - {project_name}{modified_indicator}"
            )

    def on_model_space_closed(self):
        """Handle model space window closure."""
        self.model_space_window = None
        # If both main windows are closed, exit app
        if self.paperspace_window is None:
            self.app.quit()

    def on_paperspace_closed(self):
        """Handle paperspace window closure."""
        self.paperspace_window = None
        # If both main windows are closed, exit app
        if self.model_space_window is None:
            self.app.quit()

    def notify_model_space_changed(self, change_type="general", data=None):
        """Notify all windows that model space has changed."""
        change_data = {
            "type": change_type,
            "data": data or {},
            "timestamp": QtCore.QDateTime.currentDateTime().toString(),
        }
        self.model_space_changed.emit(change_data)

    def notify_paperspace_changed(self, change_type="general", data=None):
        """Notify all windows that paperspace has changed."""
        change_data = {
            "type": change_type,
            "data": data or {},
            "timestamp": QtCore.QDateTime.currentDateTime().toString(),
        }
        self.paperspace_changed.emit(change_data)

    def notify_project_changed(self, change_type="general", data=None):
        """Notify all windows that project state has changed."""
        change_data = {
            "type": change_type,
            "data": data or {},
            "timestamp": QtCore.QDateTime.currentDateTime().toString(),
        }
        self.project_changed.emit(change_data)

    def run(self):
        """Start the application (called by boot.py)."""
        # The boot.py will call app.exec(), so we just return self
        return self


def main():
    """Main application entry point."""
    # Ensure QApplication exists before creating any Qt widgets
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setApplicationName("LV CAD")
        app.setApplicationVersion("0.6.0")

    controller = AppController()
    controller._apply_modern_theme()

    # Show the main window
    controller.show()

    return app.exec()


if __name__ == "__main__":
    main()
