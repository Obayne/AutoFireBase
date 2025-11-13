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

from app.tools import draw as draw_tools
from app.tools.chamfer_tool import ChamferTool
from app.tools.extend_tool import ExtendTool
from app.tools.fillet_radius_tool import FilletRadiusTool
from app.tools.fillet_tool import FilletTool
from app.tools.freehand import FreehandTool
from app.tools.leader import LeaderTool
from app.tools.measure_tool import MeasureTool
from app.tools.mirror_tool import MirrorTool
from app.tools.move_tool import MoveTool
from app.tools.revision_cloud import RevisionCloudTool
from app.tools.rotate_tool import RotateTool
from app.tools.scale_tool import ScaleTool
from app.tools.scale_underlay import (
    ScaleUnderlayDragTool,
    ScaleUnderlayRefTool,
)
from app.tools.text_tool import MTextTool, TextTool
from app.tools.trim_tool import TrimTool

try:
    from app.tools.dimension import DimensionTool
except Exception:

    class DimensionTool:
        def __init__(self, *a, **k):
            self.active = False


class ModelSpaceWindow(QMainWindow):
    """
    Model Space Window - Dedicated CAD workspace for device placement and design.
    Contains the main design canvas with device placement, drawing tools, and CAD operations.
    """

    def __init__(self, app_controller, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.setWindowTitle("LV CAD - Model Space")
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

        # Add modern toolbar
        self._setup_toolbar()

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

        self.layer_underlay = QtWidgets.QGraphicsItemGroup()
        self.layer_underlay.setZValue(-100)
        self.scene.addItem(self.layer_underlay)

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

        # AI Assistant dock
        self._setup_assistant_dock()

        # System Builder dock
        self._setup_system_builder_dock()

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

    def _setup_assistant_dock(self):
        """Setup the AI assistant dock."""
        from app.assistant import AssistantDock

        self.assistant_dock = AssistantDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.assistant_dock)

    def _setup_system_builder_dock(self):
        """Setup the system builder dock for automatic system design."""
        # from app.system_builder import SystemBuilder

        # self.system_builder = SystemBuilder()

        dock = QtWidgets.QDockWidget("System Builder", self)
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # System type selection
        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(QtWidgets.QLabel("System Type:"))
        self.system_type_combo = QtWidgets.QComboBox()
        self.system_type_combo.addItems(
            [
                "Conventional Fire Alarm",
                "Addressable Fire Alarm",
                "Emergency Voice/Alarm",
                "Mass Notification",
            ]
        )
        type_layout.addWidget(self.system_type_combo)
        lay.addLayout(type_layout)

        # Building parameters
        params_group = QtWidgets.QGroupBox("Building Parameters")
        params_lay = QtWidgets.QFormLayout(params_group)

        self.building_area = QtWidgets.QSpinBox()
        self.building_area.setRange(100, 100000)
        self.building_area.setValue(10000)
        self.building_area.setSuffix(" sq ft")
        params_lay.addRow("Total Area:", self.building_area)

        self.stories = QtWidgets.QSpinBox()
        self.stories.setRange(1, 50)
        self.stories.setValue(1)
        params_lay.addRow("Stories:", self.stories)

        self.occupancy_type = QtWidgets.QComboBox()
        self.occupancy_type.addItems(
            [
                "Business",
                "Educational",
                "Healthcare",
                "Residential",
                "Mercantile",
                "Assembly",
                "Industrial",
                "Storage",
            ]
        )
        params_lay.addRow("Occupancy:", self.occupancy_type)

        lay.addWidget(params_group)

        # Design buttons
        design_group = QtWidgets.QGroupBox("System Design")
        design_lay = QtWidgets.QVBoxLayout(design_group)

        self.btn_design_system = QtWidgets.QPushButton("🎯 Design System")
        self.btn_design_system.clicked.connect(self.design_system)
        design_lay.addWidget(self.btn_design_system)

        self.btn_calculate_wiring = QtWidgets.QPushButton("⚡ Calculate Wiring")
        self.btn_calculate_wiring.clicked.connect(self.calculate_wiring)
        design_lay.addWidget(self.btn_calculate_wiring)

        self.btn_generate_spool = QtWidgets.QPushButton("🧵 Generate Wire Spool")
        self.btn_generate_spool.clicked.connect(self.generate_wire_spool)
        design_lay.addWidget(self.btn_generate_spool)

        lay.addWidget(design_group)

        # Results display
        results_group = QtWidgets.QGroupBox("Design Results")
        results_lay = QtWidgets.QVBoxLayout(results_group)

        self.results_text = QtWidgets.QTextEdit()
        self.results_text.setMaximumHeight(400)
        self.results_text.setPlaceholderText("NFPA 72 compliant design results will appear here...")
        results_lay.addWidget(self.results_text)

        lay.addWidget(results_group)

        dock.setWidget(w)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

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

        # Modify menu for CAD tools
        modify_menu = menubar.addMenu("&Modify")
        modify_menu.addAction("Offset Selected…", self.offset_selected_dialog)
        modify_menu.addAction("Trim Lines", self.start_trim)
        modify_menu.addAction("Finish Trim", self.finish_trim)
        modify_menu.addAction("Extend Lines", self.start_extend)
        modify_menu.addAction("Fillet (Corner)", self.start_fillet)
        modify_menu.addAction("Fillet (Radius)…", self.start_fillet_radius)
        modify_menu.addAction("Move", self.start_move)
        modify_menu.addAction("Copy", self.start_copy)
        modify_menu.addAction("Rotate", self.start_rotate)
        modify_menu.addAction("Mirror", self.start_mirror)
        modify_menu.addAction("Scale", self.start_scale)
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

        # Modify menu for CAD tools
        modify_menu = menubar.addMenu("&Modify")
        modify_menu.addAction("Offset Selected…", self.offset_selected_dialog)
        modify_menu.addAction("Trim Lines", self.start_trim)
        modify_menu.addAction("Finish Trim", self.finish_trim)
        modify_menu.addAction("Extend Lines", self.start_extend)
        modify_menu.addAction("Fillet (Corner)", self.start_fillet)
        modify_menu.addAction("Fillet (Radius)…", self.start_fillet_radius)
        modify_menu.addAction("Move", self.start_move)
        modify_menu.addAction("Copy", self.start_copy)
        modify_menu.addAction("Rotate", self.start_rotate)
        modify_menu.addAction("Mirror", self.start_mirror)
        modify_menu.addAction("Scale", self.start_scale)
        modify_menu.addAction("Chamfer…", self.start_chamfer)

    def _setup_toolbar(self):
        """Setup modern toolbar with drawing tools."""
        # Create main toolbar
        self.toolbar = self.addToolBar("Drawing Tools")
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toolbar.setIconSize(QtCore.QSize(20, 20))

        # Drawing tools
        self.act_draw_line = QtGui.QAction("📏 Line", self)
        self.act_draw_line.triggered.connect(lambda: self.draw.select_tool("line"))
        self.toolbar.addAction(self.act_draw_line)

        self.act_draw_rect = QtGui.QAction("▭ Rect", self)
        self.act_draw_rect.triggered.connect(lambda: self.draw.select_tool("rect"))
        self.toolbar.addAction(self.act_draw_rect)

        self.act_draw_circle = QtGui.QAction("○ Circle", self)
        self.act_draw_circle.triggered.connect(lambda: self.draw.select_tool("circle"))
        self.toolbar.addAction(self.act_draw_circle)

        self.act_draw_poly = QtGui.QAction("△ Poly", self)
        self.act_draw_poly.triggered.connect(lambda: self.draw.select_tool("polyline"))
        self.toolbar.addAction(self.act_draw_poly)

        self.act_draw_arc = QtGui.QAction("⌒ Arc", self)
        self.act_draw_arc.triggered.connect(lambda: self.draw.select_tool("arc"))
        self.toolbar.addAction(self.act_draw_arc)

        self.toolbar.addSeparator()

        # Device placement
        self.act_place_device = QtGui.QAction("🔥 Device", self)
        self.act_place_device.triggered.connect(self.start_device_placement)
        self.toolbar.addAction(self.act_place_device)

        self.act_place_wire = QtGui.QAction("⚡ Wire", self)
        self.act_place_wire.triggered.connect(lambda: self.draw.select_tool("wire"))
        self.toolbar.addAction(self.act_place_wire)

        self.toolbar.addSeparator()

        # Text and dimensions
        self.act_text = QtGui.QAction("T Text", self)
        self.act_text.triggered.connect(lambda: self.text_tool.start())
        self.toolbar.addAction(self.act_text)

        self.act_dimension = QtGui.QAction("📐 Dim", self)
        self.act_dimension.triggered.connect(lambda: self.dim_tool.start())
        self.toolbar.addAction(self.act_dimension)

    def start_device_placement(self):
        """Start device placement mode."""
        self.statusBar().showMessage("Click to place selected device. Right-click to cancel.")
        # Device placement logic would go here

    # CAD tool methods
    def start_trim(self):
        self.trim_tool.start()

    def finish_trim(self):
        self.trim_tool.finish()

    def start_extend(self):
        self.extend_tool.start()

    def start_fillet(self):
        self.fillet_tool.start()

    def start_fillet_radius(self):
        self.fillet_radius_tool.start()

    def start_move(self):
        self.move_tool.start()

    def start_copy(self):
        self.move_tool.start_copy()

    def start_rotate(self):
        self.rotate_tool.start()

    def start_mirror(self):
        self.mirror_tool.start()

    def start_scale(self):
        self.scale_tool.start()

    def start_chamfer(self):
        self.chamfer_tool.start()

    def offset_selected_dialog(self):
        # Placeholder for offset tool
        pass

    # System builder methods
    def design_system(self):
        """Automatically design a fire alarm system based on building parameters."""
        system_type = self.system_type_combo.currentText()
        area = self.building_area.value()
        stories = self.stories.value()
        occupancy = self.occupancy_type.currentText()

        result = f"System design placeholder for {system_type}, {area} sq ft, {stories} stories, {occupancy} occupancy"
        self.results_text.setPlainText(result)

    def calculate_wiring(self):
        """Calculate wiring requirements for the system."""
        result = "Wiring calculation placeholder"
        self.results_text.setPlainText(result)

    def generate_wire_spool(self):
        """Generate wire spool list for installation."""
        result = "Wire spool placeholder"
        self.results_text.setPlainText(result)
{chr(10).join(f"• Circuit {i+1}: {circuit['devices']} devices ({circuit['current']:.1f}A load, {circuit['wire_size']} AWG)"
