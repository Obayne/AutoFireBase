"""
AutoFire Application Controller
Clean, modular application controller for the fire alarm CAD application.
"""

import json
import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

# Import backend services
from backend.catalog import load_catalog
from backend.logging_config import setup_logging

# Import our UI components
from frontend.windows.model_space import ModelSpaceWindow
from frontend.windows.paperspace import PaperspaceWindow
from frontend.windows.project_overview import ProjectOverviewWindow

# Setup logging
setup_logging()
import logging

logger = logging.getLogger(__name__)


class AutoFireController(QMainWindow):
    """
    Main application controller for AutoFire.
    Manages the multi-window application and coordinates between components.
    """

    # Signals
    model_space_changed = Signal(dict)
    paperspace_changed = Signal(dict)
    project_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoFire Controller")
        self.hide()  # This is a controller window, not shown to user

        # Initialize core components
        self._load_preferences()
        self._load_device_catalog()

        # Create application windows
        self.model_space_window: ModelSpaceWindow | None = None
        self.paperspace_window: PaperspaceWindow | None = None
        self.project_overview_window: ProjectOverviewWindow | None = None

        # Initialize windows
        self._create_windows()

        logger.info("AutoFire controller initialized")

    def _load_preferences(self):
        """Load user preferences."""
        self.prefs_path = os.path.join(os.path.expanduser("~"), "AutoFire", "prefs.json")
        try:
            with open(self.prefs_path) as f:
                self.prefs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.prefs = self._get_default_prefs()

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
            "units": "Imperial (feet)",
            "drawing_scale": "1:1",
            "default_line_weight": 1,
            "default_color": "#000000",
            "show_device_palette": True,
            "show_properties_dock": True,
            "show_status_bar": True,
            "auto_save_interval": 5,
            "enable_osnap": True,
            "show_grid": True,
        }

    def _load_device_catalog(self):
        """Load the device catalog."""
        try:
            self.devices_all = load_catalog()
            logger.info(f"Loaded {len(self.devices_all)} devices")
        except Exception as e:
            logger.error(f"Failed to load device catalog: {e}")
            self.devices_all = []

    def _create_windows(self):
        """Create and show the main application windows."""
        try:
            # Create Model Space window first
            from frontend.windows.model_space import ModelSpaceWindow

            self.model_space_window = ModelSpaceWindow(self)
            model_scene = self.model_space_window.scene  # Get the scene from model space
            self.model_space_window.show()

            # Create Paperspace window with model scene
            from frontend.windows.paperspace import PaperspaceWindow

            self.paperspace_window = PaperspaceWindow(self, model_scene)
            self.paperspace_window.show()

            # Create Project Overview window (optional)
            if self.prefs.get("show_project_overview", False):
                from frontend.windows.project_overview import ProjectOverviewWindow

                self.project_overview_window = ProjectOverviewWindow(self)
                self.project_overview_window.show()

            # Arrange windows
            self._arrange_windows()

            # Create menu bars for each window
            self.create_global_menu_bar(self.model_space_window)
            self.create_global_menu_bar(self.paperspace_window)
            if self.project_overview_window:
                self.create_global_menu_bar(self.project_overview_window)

        except Exception as e:
            logger.error(f"Failed to create windows: {e}")
            QMessageBox.critical(None, "Startup Error", f"Failed to start AutoFire: {e}")
            QApplication.quit()

    def _arrange_windows(self):
        """Arrange windows on screen."""
        screens = QApplication.screens()
        if len(screens) >= 2:
            # Multi-monitor setup
            primary = screens[0].availableGeometry()
            secondary = screens[1].availableGeometry()

            if self.model_space_window:
                self.model_space_window.setGeometry(primary)
            if self.paperspace_window:
                self.paperspace_window.setGeometry(secondary)
        else:
            # Single monitor - tile windows
            screen = screens[0].availableGeometry()
            width = screen.width()
            height = screen.height()

            if self.model_space_window:
                self.model_space_window.setGeometry(0, 0, width // 2, height)
            if self.paperspace_window:
                self.paperspace_window.setGeometry(width // 2, 0, width // 2, height)

    def create_global_menu_bar(self, window):
        """Create global menu bar for a window."""
        menubar = window.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        # Add file actions here

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        # Add edit actions here

        # View menu
        view_menu = menubar.addMenu("&View")
        # Add view actions here

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        # Add tools actions here

        # Help menu
        help_menu = menubar.addMenu("&Help")
        # Add help actions here

    def save_preferences(self):
        """Save user preferences."""
        os.makedirs(os.path.dirname(self.prefs_path), exist_ok=True)
        try:
            with open(self.prefs_path, "w") as f:
                json.dump(self.prefs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")

    def closeEvent(self, event):
        """Handle application close."""
        # Save preferences
        self.save_preferences()

        # Close all windows
        if self.model_space_window:
            self.model_space_window.close()
        if self.paperspace_window:
            self.paperspace_window.close()
        if self.project_overview_window:
            self.project_overview_window.close()

        event.accept()
