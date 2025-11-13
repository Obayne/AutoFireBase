"""
Model Space Window - CAD workspace for device placement and design
"""

import os
import sys

# Allow running as `python app\main.py` by fixing sys.path for absolute `app.*` imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
)

from app.logging_config import setup_logging

# Grid scene and defaults used by the main window
from app.scene import DEFAULT_GRID_SIZE, GridScene

# Ensure logging is configured early so module-level loggers emit during
# headless simulators and when the app starts from __main__.
setup_logging()
import logging

_logger = logging.getLogger(__name__)


class ModelSpaceWindow(QMainWindow):
    """
    Model Space Window - Dedicated CAD workspace for device placement and design.
    Contains the main design canvas with device placement, drawing tools, and CAD operations.
    """

    def __init__(self, app_controller, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.setWindowTitle("AutoFire - Model Space")
        self.setObjectName("ModelSpaceWindow")

        # Initialize core attributes
        self.prefs = app_controller.prefs
        self.devices_all = app_controller.devices_all
        self.px_per_ft = float(self.prefs.get("px_per_ft", 12.0))
        self.snap_label = self.prefs.get("snap_label", "grid")
        self.snap_step_in = float(self.prefs.get("snap_step_in", 0.0))

        # Initialize layers early
        self.layers = [{"id": 1, "name": "Default", "visible": True}]
        self.active_layer_id = 1

        # Create the main scene and view
        self._setup_scene_and_view()

        # Setup UI components
        self._setup_ui()

        # Initialize tools and state
        self._initialize_tools()

        # Connect to app controller signals
        self._connect_signals()

        self.resize(1200, 800)

    def _setup_scene_and_view(self):
        """Setup the main CAD scene and view."""
        from app.main import CanvasView

        # Create scene
        self.scene = GridScene(int(self.prefs.get("grid", DEFAULT_GRID_SIZE)), 0, 0, 15000, 10000)
        self.scene.snap_enabled = bool(self.prefs.get("snap", True))

        # Create device and layer groups
        self.devices_group = QtWidgets.QGraphicsItemGroup()
        self.devices_group.setZValue(100)
        self.scene.addItem(self.devices_group)

        self.layer_wires = QtWidgets.QGraphicsItemGroup()
        self.layer_wires.setZValue(60)
        self.scene.addItem(self.layer_wires)

        self.layer_sketch = QtWidgets.QGraphicsItemGroup()
        self.layer_sketch.setZValue(40)
        self.scene.addItem(self.layer_sketch)

        self.layer_overlay = QtWidgets.QGraphicsItemGroup()
        self.layer_overlay.setZValue(200)
        self.scene.addItem(self.layer_overlay)

        # Create view
        self.view = CanvasView(
            self.scene,
            self.devices_group,
            self.layer_wires,
            self.layer_sketch,
            self.layer_overlay,
            self,  # Pass self as window reference
        )

        self.setCentralWidget(self.view)

    def _setup_ui(self):
        """Setup UI components like docks and status bar."""
        self._setup_docks()
        self._setup_status_bar()
        self._setup_menus()

    def _setup_docks(self):
        """Setup dockable panels."""
        # Device palette dock
        self._setup_device_palette()

        # Properties dock
        self._setup_properties_dock()

    def _setup_device_palette(self):
        """Setup the device palette dock."""
        dock = QtWidgets.QDockWidget("Devices", self)
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # Device tree
        self.device_tree = QtWidgets.QTreeWidget()
        self.device_tree.setHeaderLabels(["Devices"])
        self.device_tree.setAlternatingRowColors(True)
        self.device_tree.setSortingEnabled(True)

        # Populate device tree
        self._populate_device_tree()

        lay.addWidget(self.device_tree)
        dock.setWidget(w)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def _populate_device_tree(self):
        """Populate the device tree with available devices."""
        try:
            # Group devices by type for hierarchy
            grouped = {}
            for d in self.devices_all:
                cat = d.get("type", "Unknown") or "Unknown"
                grouped.setdefault(cat, []).append(d)

            for cat in sorted(grouped.keys()):
                cat_item = QtWidgets.QTreeWidgetItem([cat])
                for dev in sorted(grouped[cat], key=lambda x: x.get("name", "")):
                    txt = f"{dev.get('name','<unknown>')} ({dev.get('symbol','')})"
                    if dev.get("part_number"):
                        txt += f" - {dev.get('part_number')}"
                    it = QtWidgets.QTreeWidgetItem([txt])
                    it.setData(0, QtCore.Qt.UserRole, dev)
                    cat_item.addChild(it)
                self.device_tree.addTopLevelItem(cat_item)
            self.device_tree.expandAll()
        except Exception as e:
            _logger.error(f"Failed to populate device tree: {e}")

    def _setup_properties_dock(self):
        """Setup the properties dock."""
        dock = QtWidgets.QDockWidget("Properties", self)
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # Properties will be populated when devices are selected
        self.properties_label = QtWidgets.QLabel("Select a device to view properties")
        lay.addWidget(self.properties_label)

        dock.setWidget(w)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _setup_status_bar(self):
        """Setup the status bar."""
        self.statusBar().showMessage("Model Space - Ready")

        # Add coordinate display
        self.coord_label = QtWidgets.QLabel("0.00, 0.00 ft")
        self.statusBar().addPermanentWidget(self.coord_label)

    def _setup_menus(self):
        """Setup menus using global menu bar."""
        # Use global menu bar from app controller
        self.app_controller.create_global_menu_bar(self)

        # Add window-specific menus after global ones
        menubar = self.menuBar()

        # View menu for model space specific options
        view_menu = menubar.addMenu("&View")
        self.act_grid = QtGui.QAction("Grid", self, checkable=True)
        self.act_grid.setChecked(True)
        self.act_grid.toggled.connect(self.toggle_grid)
        view_menu.addAction(self.act_grid)

        self.act_snap = QtGui.QAction("Snap", self, checkable=True)
        self.act_snap.setChecked(bool(self.prefs.get("snap", True)))
        self.act_snap.toggled.connect(self.toggle_snap)
        view_menu.addAction(self.act_snap)

    def _initialize_tools(self):
        """Initialize CAD tools and state."""
        # Initialize tool state
        self.current_proto = None
        self.current_kind = "other"
        self.ghost = None
        self.show_coverage = bool(self.prefs.get("show_coverage", True))

        # Initialize history
        self.history = []
        self.history_index = -1

    def _connect_signals(self):
        """Connect to app controller signals."""
        # Connect device tree selection
        self.device_tree.itemClicked.connect(self.on_device_selected)

        # Connect to app controller signals for inter-window communication
        self.app_controller.model_space_changed.connect(self.on_model_space_changed)
        self.app_controller.paperspace_changed.connect(self.on_paperspace_changed)
        self.app_controller.project_changed.connect(self.on_project_changed)

        # Note: CanvasView already handles coordinate display in status bar

    def on_device_selected(self, item, column):
        """Handle device selection from palette."""
        dev = item.data(0, 256)  # Qt.UserRole
        if dev:
            self.current_proto = dev
            self.current_kind = dev.get("type", "other").lower()
            self.statusBar().showMessage(f"Selected: {dev.get('name', 'Unknown')}")

            # Create ghost device for placement preview
            self._create_ghost_device(dev)

    def _create_ghost_device(self, device_proto):
        """Create ghost device for placement preview."""
        if self.ghost:
            self.scene.removeItem(self.ghost)
            self.ghost = None

        # Create ghost device (semi-transparent preview)
        # This will be implemented when we move the device creation logic

    def on_model_space_changed(self, change_data):
        """Handle model space changes from other windows."""
        change_type = change_data.get("type", "general")
        # Handle different types of changes
        if change_type == "device_placed":
            # Refresh device display if needed
            self.scene.update()
        elif change_type == "scene_cleared":
            # Handle scene clearing
            pass

    def on_paperspace_changed(self, change_data):
        """Handle paperspace changes from other windows."""
        change_type = change_data.get("type", "general")
        # Model space window might not need to react to paperspace changes
        # but this is here for future expansion
        pass

    def on_project_changed(self, change_data):
        """Handle project state changes."""
        change_type = change_data.get("type", "general")
        if change_type == "new_project":
            # Clear current scene
            self._initialize_tools()
        elif change_type == "project_loaded":
            # Refresh display
            self.scene.update()

    def toggle_grid(self, on):
        """Toggle grid visibility."""
        self.scene.show_grid = bool(on)
        self.scene.update()

    def toggle_snap(self, on):
        """Toggle snap functionality."""
        self.scene.snap_enabled = bool(on)

    def get_scene_state(self):
        """Get the current scene state for serialization."""
        # Return scene data for project saving
        return {
            "scene_type": "model_space",
            "devices": [],  # Will be populated
            "wires": [],  # Will be populated
            "sketch": [],  # Will be populated
        }

    def load_scene_state(self, data):
        """Load scene state from serialized data."""
        # Load scene data from project
        pass

    def closeEvent(self, event):
        """Handle window close event."""
        # Notify controller about window closing
        if hasattr(self.app_controller, "on_model_space_closed"):
            self.app_controller.on_model_space_closed()
        event.accept()
