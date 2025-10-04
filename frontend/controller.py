"""
import json
import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog

# Import backend services
from backend.catalog import load_catalog
from backend.logging_config import setup_logging
import loggingApplication Controller
Clean, modular application controller for the fire alarm CAD application.
"""

import json
import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox

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

        # Initialize project data
        self.current_project_path: str | None = None
        self.project_data = self._get_default_project_data()

        # Initialize core components
        self._load_preferences()
        self._apply_theme()
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

    def _get_default_project_data(self):
        """Get default project data structure."""
        return {
            "version": "1.0",
            "name": "Untitled Project",
            "description": "",
            "created": "",
            "modified": "",
            "author": "",
            "devices": [],
            "wires": [],
            "drawings": [],
            "layers": {},
            "settings": {},
        }

    def _load_device_catalog(self):
        """Load the device catalog."""
        try:
            self.devices_all = load_catalog()
            logger.info(f"Loaded {len(self.devices_all)} devices")
        except Exception as e:
            logger.error(f"Failed to load device catalog: {e}")
            self.devices_all = []

    def _apply_theme(self):
        """Apply the current theme to the application."""
        from frontend.ui.theme import apply_theme

        app = QApplication.instance()
        if app:
            theme_name = self.prefs.get("theme", "dark")
            apply_theme(app, theme_name)

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
            # ModelSpaceWindow handles its own menu bar
            # self.create_global_menu_bar(self.model_space_window)
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
        menubar.addMenu("&File")
        # Add file actions here

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        # Undo/Redo actions
        undo_action = edit_menu.addAction("&Undo")
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(lambda: self.undo(window))

        redo_action = edit_menu.addAction("&Redo")
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(lambda: self.redo(window))

        edit_menu.addSeparator()

        # Standard edit actions
        # Add more edit actions here as needed

        # View menu
        view_menu = menubar.addMenu("&View")

        # Zoom actions
        zoom_in_action = view_menu.addAction("Zoom &In")
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(lambda: self.zoom_in(window))

        zoom_out_action = view_menu.addAction("Zoom &Out")
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(lambda: self.zoom_out(window))

        zoom_fit_action = view_menu.addAction("&Fit to Screen")
        zoom_fit_action.setShortcut("Ctrl+0")
        zoom_fit_action.triggered.connect(lambda: self.zoom_fit(window))

        view_menu.addSeparator()

        # Grid and snap actions
        grid_action = view_menu.addAction("&Grid")
        grid_action.setCheckable(True)
        grid_action.setChecked(window.prefs.get("show_grid", True))
        grid_action.triggered.connect(lambda: self.toggle_grid(window))

        snap_action = view_menu.addAction("&Snap to Grid")
        snap_action.setCheckable(True)
        snap_action.setChecked(window.prefs.get("snap", True))
        snap_action.triggered.connect(lambda: self.toggle_snap(window))

        # Tools menu
        menubar.addMenu("&Tools")
        # Add tools actions here

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")
        settings_action = settings_menu.addAction("&Preferences...")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(lambda: self.show_settings_dialog(window))

        # Help menu
        menubar.addMenu("&Help")
        # Add help actions here

    def undo(self, window):
        """Perform undo operation on the given window."""
        if hasattr(window, "command_stack"):
            if window.command_stack.undo():
                description = window.command_stack.get_undo_description()
                window.statusBar().showMessage(f"Undid: {description}")
            else:
                window.statusBar().showMessage("Nothing to undo")

    def redo(self, window):
        """Perform redo operation on the given window."""
        if hasattr(window, "command_stack"):
            if window.command_stack.redo():
                description = window.command_stack.get_redo_description()
                window.statusBar().showMessage(f"Redid: {description}")
            else:
                window.statusBar().showMessage("Nothing to redo")

    def show_settings_dialog(self, parent_window):
        """Show the settings dialog."""
        try:
            from frontend.dialogs.settings import SettingsDialog

            dialog = SettingsDialog(self.prefs, parent_window)
            dialog.settings_changed.connect(self.on_settings_changed)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Settings were accepted, they are already applied via the signal
                self.save_preferences()
                QMessageBox.information(parent_window, "Settings", "Settings saved successfully.")
        except Exception as e:
            logger.error(f"Failed to show settings dialog: {e}")
            QMessageBox.critical(parent_window, "Error", f"Failed to open settings: {e}")

    def on_settings_changed(self, new_prefs):
        """Handle settings changes."""
        self.prefs.update(new_prefs)

        # Apply theme changes immediately
        if "theme" in new_prefs:
            from frontend.ui.theme import apply_theme

            apply_theme(QApplication.instance(), new_prefs["theme"])

        # Update window preferences
        self._update_window_preferences()

    def _update_window_preferences(self):
        """Update window preferences based on current settings."""
        # This will be called when settings change to update window visibility, etc.
        pass

    def save_preferences(self):
        """Save user preferences."""
        """Save user preferences."""
        os.makedirs(os.path.dirname(self.prefs_path), exist_ok=True)
        try:
            with open(self.prefs_path, "w") as f:
                json.dump(self.prefs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")

    def save_project(self, file_path: str) -> bool:
        """Save the current project to a file."""
        try:
            # Collect project data from model space window
            if self.model_space_window:
                self.project_data["devices"] = self._serialize_devices()
                self.project_data["wires"] = self._serialize_wires()
                self.project_data["drawings"] = self._serialize_drawings()
                self.project_data["layers"] = self._serialize_layers()

            # Update metadata
            from datetime import datetime

            self.project_data["modified"] = datetime.now().isoformat()

            # Save to file
            with open(file_path, "w") as f:
                json.dump(self.project_data, f, indent=2)

            self.current_project_path = file_path
            logger.info(f"Project saved to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            return False

    def load_project(self, file_path: str) -> bool:
        """Load a project from a file."""
        try:
            with open(file_path) as f:
                self.project_data = json.load(f)

            self.current_project_path = file_path

            # Load data into model space window
            if self.model_space_window:
                self._deserialize_devices()
                self._deserialize_wires()
                self._deserialize_drawings()
                self._deserialize_layers()

            logger.info(f"Project loaded from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            return False

    def _serialize_devices(self) -> list:
        """Serialize placed devices for saving."""
        devices = []
        if self.model_space_window and self.model_space_window.devices_group:
            for item in self.model_space_window.devices_group.childItems():
                if hasattr(item, "name") and hasattr(item, "symbol"):
                    device_info = {
                        "symbol": getattr(item, "symbol", ""),
                        "name": getattr(item, "name", ""),
                        "manufacturer": getattr(item, "manufacturer", ""),
                        "part_number": getattr(item, "part_number", ""),
                        "position": [item.x(), item.y()],
                        "rotation": item.rotation(),
                        "scale": item.scale(),
                        "layer": getattr(item, "layer", None),
                    }
                    devices.append(device_info)
        return devices

    def _serialize_wires(self) -> list:
        """Serialize wires for saving."""
        wires = []
        if self.model_space_window and self.model_space_window.layer_wires:
            for item in self.model_space_window.layer_wires.childItems():
                # TODO: Implement wire serialization
                pass
        return wires

    def _serialize_drawings(self) -> list:
        """Serialize drawing elements for saving."""
        drawings = []
        if self.model_space_window and self.model_space_window.layer_sketch:
            for item in self.model_space_window.layer_sketch.childItems():
                # TODO: Implement drawing serialization
                pass
        return drawings

    def _serialize_layers(self) -> dict:
        """Serialize layer information for saving."""
        layers = {}
        if self.model_space_window and hasattr(self.model_space_window, "layer_manager"):
            # TODO: Implement layer serialization
            pass
        return layers

    def _deserialize_devices(self):
        """Load devices from project data."""
        if not self.model_space_window:
            return

        # Clear existing devices
        self.model_space_window.devices_group.childItems().clear()

        # Load devices from project data
        for device_info in self.project_data.get("devices", []):
            # TODO: Implement device deserialization
            pass

    def _deserialize_wires(self):
        """Load wires from project data."""
        if not self.model_space_window:
            return

        # Clear existing wires
        self.model_space_window.layer_wires.childItems().clear()

        # Load wires from project data
        for wire_info in self.project_data.get("wires", []):
            # TODO: Implement wire deserialization
            pass

    def _deserialize_drawings(self):
        """Load drawings from project data."""
        if not self.model_space_window:
            return

        # Clear existing drawings
        self.model_space_window.layer_sketch.childItems().clear()

        # Load drawings from project data
        for drawing_info in self.project_data.get("drawings", []):
            # TODO: Implement drawing deserialization
            pass

    def _deserialize_layers(self):
        """Load layer information from project data."""
        if not self.model_space_window:
            return

        # Load layer data
        # TODO: Implement layer deserialization

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

    def zoom_in(self, window):
        """Zoom in on the active view."""
        if hasattr(window, "view") and hasattr(window.view, "zoom_in"):
            window.view.zoom_in()

    def zoom_out(self, window):
        """Zoom out on the active view."""
        if hasattr(window, "view") and hasattr(window.view, "zoom_out"):
            window.view.zoom_out()

    def zoom_fit(self, window):
        """Fit view to screen."""
        if hasattr(window, "view") and hasattr(window.view, "zoom_fit"):
            window.view.zoom_fit()

    def toggle_grid(self, window):
        """Toggle grid visibility."""
        if hasattr(window, "view") and hasattr(window.view, "toggle_grid"):
            window.view.toggle_grid()

    def toggle_snap(self, window):
        """Toggle snap to grid."""
        if hasattr(window, "view") and hasattr(window.view, "toggle_snap"):
            window.view.toggle_snap()
