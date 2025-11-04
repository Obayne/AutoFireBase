"""
Model Space Window - CAD workspace for device placement and design
"""

import os
import sys

# Allow running as `python app\main.py` by fixing sys.path for absolute `app.*` imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
)

# Drawing tools for wire routing
from app.tools.draw import (
    DrawController,
    DrawMode,
)
from backend import branding

# Backend services
from backend.catalog import load_catalog
from backend.logging_config import setup_logging

# CAD command system for undo/redo
from cad_core.commands import CADCommandStack
from frontend.assistant import AssistantDock
from frontend.labels_manager import (
    format_label_for_ui,
    get_hide_conduit_fill,
    set_hide_conduit_fill,
)
from frontend.panels.circuits_editor import CircuitsEditor

# Layers panel for advanced layer management
from frontend.panels.layer_manager import LayerManager

# System builder for direct professional CAD access
from frontend.panels.system_builder_guided import SystemBuilderWidget

# Status widgets
from frontend.widgets.canvas_status_summary import CanvasStatusSummary

# Grid scene and defaults used by the main window
from frontend.windows.scene import DEFAULT_GRID_SIZE, CanvasView, GridScene

# Ensure logging is configured early so module-level loggers emit during
# headless simulators and when the app starts from __main__.
setup_logging()

_logger = logging.getLogger(__name__)


class WireSegment(QtWidgets.QGraphicsLineItem):
    """Minimal wire segment with metadata for voltage drop calculations."""

    def __init__(self, x1, y1, x2, y2, ohms_per_1000ft=3.08, parent=None):
        super().__init__(parent)
        self.setLine(x1, y1, x2, y2)
        self.ohms_per_1000ft = float(ohms_per_1000ft)
        self.length_ft = 0.0  # will be computed on add
        pen = QtGui.QPen(QtGui.QColor(200, 0, 0))
        pen.setWidth(2)
        self.setPen(pen)
        self.setZValue(65)


class ModelSpaceWindow(QMainWindow):
    """
    Model Space Window - Dedicated CAD workspace for device placement and design.
    Contains the main design canvas with device placement, drawing tools, and CAD operations.
    """

    def __init__(self, app_controller, parent=None):
        import time

        logger = logging.getLogger(__name__)
        start_ts = time.time()
        logger.info("ModelSpaceWindow.__init__ start")
        super().__init__(parent)
        self.app_controller = app_controller
        self.setWindowTitle(f"{branding.PRODUCT_NAME} - Model Space")
        self.setObjectName("ModelSpaceWindow")

        # Initialize core attributes
        self.prefs = app_controller.prefs
        self.devices_all = app_controller.devices_all
        self.px_per_ft = float(self.prefs.get("px_per_ft", 12.0))
        self.snap_label = self.prefs.get("snap_label", "grid")
        self.snap_step_in = float(self.prefs.get("snap_step_in", 0.0))

        # Initialize layers
        self.layer_manager = LayerManager()
        self.layer_manager.layer_changed.connect(self.on_layer_changed)
        self.layer_manager.layer_selected.connect(self.on_layer_selected)

        # Create the main scene and view
        self._setup_scene_and_view()

        # Setup UI components
        self._setup_ui()

        # Initialize tools and state
        self._initialize_tools()

        # Connect to app controller signals
        self._connect_signals()

        self.resize(1200, 800)
        try:
            end_ts = time.time()
            logger.info("ModelSpaceWindow.__init__ complete (%.3fs)", end_ts - start_ts)
        except Exception:
            pass

    def _setup_scene_and_view(self):
        """Setup the main CAD scene and view."""

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

        # Initialize circuit manager for fire alarm system logic
        from frontend.circuit_manager import CircuitManager

        self.circuit_manager = CircuitManager(self.scene)

    def _setup_ui(self):
        """Setup UI components like docks and status bar."""
        self._setup_toolbar()
        self._setup_docks()
        self._setup_status_bar()
        self._setup_menus()

    def _setup_toolbar(self):
        """Setup the main toolbar."""
        toolbar = self.addToolBar("Main")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # Selection tool
        select_action = toolbar.addAction("Select")
        select_action.setCheckable(True)
        select_action.setChecked(True)

        toolbar.addSeparator()

        # Pan tool
        pan_action = toolbar.addAction("Pan")
        pan_action.setCheckable(True)

        # Place panel
        place_panel_action = toolbar.addAction("Panel")
        place_panel_action.setCheckable(True)

        # Place device
        place_device_action = toolbar.addAction("Device")
        place_device_action.setCheckable(True)

        # Wire routing
        wire_action = toolbar.addAction("Wire")
        wire_action.setCheckable(True)
        wire_action.triggered.connect(lambda: self.draw.set_mode(DrawMode.WIRE))

        # Quick Voltage Drop calculator
        vd_action = toolbar.addAction("Voltage Drop")
        vd_action.triggered.connect(self._calculate_voltage_drop)

        # Add a demo wire segment (scaffolding for overlay)
        add_wire_seg_action = toolbar.addAction("Add Wire Seg")
        add_wire_seg_action.triggered.connect(self._add_wire_segment)

        toolbar.addSeparator()

        # Quick: Export Submittal ZIP (one-click)
        export_zip_quick = toolbar.addAction("Export ZIP")
        export_zip_quick.setToolTip("Export Submittal Bundle (ZIP) using defaults")
        export_zip_quick.triggered.connect(self._export_report_bundle_zip)

        # CAD Drawing Tools (mutually exclusive)
        self.draw_action_group = QtGui.QActionGroup(self)
        self.draw_action_group.setExclusive(True)

        line_action = toolbar.addAction("Line")
        line_action.setCheckable(True)
        line_action.triggered.connect(lambda: self.draw.set_mode(DrawMode.LINE))
        self.draw_action_group.addAction(line_action)

        rect_action = toolbar.addAction("Rectangle")
        rect_action.setCheckable(True)
        rect_action.triggered.connect(lambda: self.draw.set_mode(DrawMode.RECT))
        self.draw_action_group.addAction(rect_action)

        circle_action = toolbar.addAction("Circle")
        circle_action.setCheckable(True)
        circle_action.triggered.connect(lambda: self.draw.set_mode(DrawMode.CIRCLE))
        self.draw_action_group.addAction(circle_action)

        polyline_action = toolbar.addAction("Polyline")
        polyline_action.setCheckable(True)
        polyline_action.triggered.connect(lambda: self.draw.set_mode(DrawMode.POLYLINE))
        self.draw_action_group.addAction(polyline_action)

        toolbar.addSeparator()

    def _calculate_voltage_drop(self):
        """Basic voltage drop calculation using wire segments.
        Sums total resistance from wire metadata (ohms/1000ft) and lengths, then shows a summary.
        """
        try:
            total_length_ft = 0.0
            total_resistance_ohms = 0.0

            for item in self.layer_wires.childItems():
                length_ft = getattr(item, "length_ft", 0.0)
                ohms_per_1000ft = getattr(item, "ohms_per_1000ft", 0.0)
                total_length_ft += float(length_ft)
                total_resistance_ohms += (float(ohms_per_1000ft) * float(length_ft)) / 1000.0

            current_a = 0.5
            v_drop = total_resistance_ohms * current_a

            msg = (
                f"Wire length: {total_length_ft:.1f} ft | "
                f"R_total: {total_resistance_ohms:.2f} Ω | "
                f"Vdrop@0.5A: {v_drop:.2f} V"
            )
            self.statusBar().showMessage(msg, 5000)
        except Exception as e:
            self.statusBar().showMessage(f"Voltage drop calc error: {e}", 5000)

    def _add_wire_segment(self):
        """Create a minimal wire segment and add to the wire layer."""
        try:
            # Create a short segment near the view center
            center = self.view.mapToScene(self.view.viewport().rect().center())
            x1 = center.x() - 100
            y1 = center.y()
            x2 = center.x() + 100
            y2 = center.y()

            seg = WireSegment(x1, y1, x2, y2, ohms_per_1000ft=3.08)
            # Compute length in feet based on px_per_ft (pixels per foot)
            px_len = QtCore.QLineF(x1, y1, x2, y2).length()
            feet_len = float(px_len) / float(self.px_per_ft)
            seg.length_ft = feet_len

            self.layer_wires.addToGroup(seg)
            self.statusBar().showMessage(
                f"Added wire segment: {feet_len:.1f} ft @ {seg.ohms_per_1000ft:.2f} Ω/1000ft",
                4000,
            )
            # Update labels after adding a segment
            self.update_wire_labels_overlay()
        except Exception as e:
            self.statusBar().showMessage(f"Failed to add wire segment: {e}", 5000)

    def _show_layer_manager(self):
        """Show the layer manager dialog."""
        if hasattr(self, "layer_manager"):
            # Create a dialog to show the layer manager
            from PySide6.QtWidgets import QDialog, QVBoxLayout

            dialog = QDialog(self)
            dialog.setWindowTitle("Layer Manager")
            dialog.resize(600, 400)

            layout = QVBoxLayout(dialog)
            layout.addWidget(self.layer_manager)

            dialog.exec()

    def _setup_docks(self):
        """Setup dockable panels."""
        # Left dock: Device Palette + Wire Spool
        self._setup_left_dock()

        # Right dock: Inspector tabs (Properties, Connections, AI Suggestions)
        self._setup_right_dock()

        # System Builder dock (initially hidden)
        self._setup_system_builder_panel()

        # Status Summary dock
        self._setup_status_summary_dock()

    def _setup_left_dock(self):
        """Setup left dock with Device Palette and Wire Spool tabs."""
        # Create tab widget for left dock
        self.left_tab_widget = QtWidgets.QTabWidget()

        # Device Palette tab
        self._setup_device_palette_tab()

        # Wire Spool tab
        self._setup_wire_spool_tab()

        # Create dock
        left_dock = QtWidgets.QDockWidget("Tools", self)
        left_dock.setWidget(self.left_tab_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)

    def _setup_device_palette_tab(self):
        """Setup device palette tab with professional-grade filtering."""
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # Search and Filter Controls
        search_frame = QtWidgets.QFrame()
        search_layout = QtWidgets.QVBoxLayout(search_frame)
        search_frame.setStyleSheet(
            "QFrame { background-color: #2d2d30; border: 1px solid #3c3c3c; border-radius: 4px; }"
        )

        # Search box with advanced features
        search_row = QtWidgets.QHBoxLayout()
        search_label = QtWidgets.QLabel("Search:")
        self.device_search = QtWidgets.QLineEdit()
        self.device_search.setPlaceholderText(
            "Search devices, manufacturers, part numbers... (supports AND/OR)"
        )
        self.device_search.textChanged.connect(self._filter_devices)
        search_row.addWidget(search_label)
        search_row.addWidget(self.device_search)
        search_layout.addLayout(search_row)

        # Advanced filter row
        filter_row1 = QtWidgets.QHBoxLayout()

        # Device type filter
        type_label = QtWidgets.QLabel("Type:")
        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems(
            [
                "All Types",
                "Smoke Detectors",
                "Heat Detectors",
                "Manual Pull Stations",
                "Horn/Strobes",
                "Speakers",
                "Control Modules",
                "Monitor Modules",
                "Panels",
                "Annunciators",
            ]
        )
        self.filter_combo.currentTextChanged.connect(self._filter_devices)

        # Manufacturer filter
        mfg_label = QtWidgets.QLabel("Manufacturer:")
        self.manufacturer_combo = QtWidgets.QComboBox()
        self.manufacturer_combo.addItem("All Manufacturers")
        self.manufacturer_combo.currentTextChanged.connect(self._filter_devices)

        filter_row1.addWidget(type_label)
        filter_row1.addWidget(self.filter_combo)
        filter_row1.addStretch()
        filter_row1.addWidget(mfg_label)
        filter_row1.addWidget(self.manufacturer_combo)
        search_layout.addLayout(filter_row1)

        # Control buttons row
        filter_row2 = QtWidgets.QHBoxLayout()

        # Clear button
        clear_btn = QtWidgets.QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_filters)
        clear_btn.setMaximumWidth(80)

        # Advanced search toggle
        advanced_btn = QtWidgets.QPushButton("Advanced")
        advanced_btn.setCheckable(True)
        advanced_btn.setMaximumWidth(80)
        advanced_btn.toggled.connect(self._toggle_advanced_search)

        filter_row2.addStretch()
        filter_row2.addWidget(advanced_btn)
        filter_row2.addWidget(clear_btn)
        search_layout.addLayout(filter_row2)

        lay.addWidget(search_frame)

        # Results count
        self.results_label = QtWidgets.QLabel("Loading devices...")
        self.results_label.setStyleSheet("color: #cccccc; font-size: 11px; margin: 5px;")
        lay.addWidget(self.results_label)

        # Device tree with improved structure
        self.device_tree = QtWidgets.QTreeWidget()
        self.device_tree.setColumnCount(3)
        self.device_tree.setHeaderLabels(["Device", "Manufacturer", "Part Number"])
        self.device_tree.setAlternatingRowColors(True)
        self.device_tree.setSortingEnabled(True)
        self.device_tree.setRootIsDecorated(True)
        self.device_tree.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.device_tree.customContextMenuRequested.connect(self._on_device_tree_context_menu)

        # Store all devices for filtering
        self.all_devices = []
        self.device_type_mapping = {
            "Smoke Detectors": ["smoke", "photo", "ionization"],
            "Heat Detectors": ["heat", "thermal", "fixed_temperature", "rate_of_rise"],
            "Manual Pull Stations": ["pull", "manual", "station"],
            "Horn/Strobes": ["horn", "strobe", "speaker_strobe", "notification"],
            "Speakers": ["speaker", "audio", "voice"],
            "Control Modules": ["control", "relay", "output"],
            "Monitor Modules": ["monitor", "input", "supervision"],
            "Panels": ["panel", "facp", "controller"],
            "Annunciators": ["annunciator", "display", "lcd", "led"],
        }

        # Populate device tree
        self._populate_device_tree()

        lay.addWidget(self.device_tree)
        self.left_tab_widget.addTab(w, "Devices")

    def _setup_wire_spool_tab(self):
        """Setup wire spool tab with professional-grade filtering."""
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # Wire Spool Header
        spool_label = QtWidgets.QLabel("Wire Spool")
        spool_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        lay.addWidget(spool_label)

        # Search and Filter Controls for Wire Spool
        wire_search_frame = QtWidgets.QFrame()
        wire_search_layout = QtWidgets.QVBoxLayout(wire_search_frame)
        wire_search_frame.setStyleSheet(
            "QFrame { background-color: #2d2d30; border: 1px solid #3c3c3c; border-radius: 4px; }"
        )

        # Wire search box
        wire_search_row = QtWidgets.QHBoxLayout()
        wire_search_label = QtWidgets.QLabel("Search:")
        self.wire_search = QtWidgets.QLineEdit()
        self.wire_search.setPlaceholderText("Search wire types, gauges, colors, manufacturers...")
        self.wire_search.textChanged.connect(self._filter_wires)
        wire_search_row.addWidget(wire_search_label)
        wire_search_row.addWidget(self.wire_search)
        wire_search_layout.addLayout(wire_search_row)

        # Wire filter controls
        wire_filter_row = QtWidgets.QHBoxLayout()

        # Wire type filter
        wire_type_label = QtWidgets.QLabel("Type:")
        self.wire_type_combo = QtWidgets.QComboBox()
        self.wire_type_combo.addItems(["All Types", "SLC/IDC", "NAC", "Power", "Riser", "Plenum"])
        self.wire_type_combo.currentTextChanged.connect(self._filter_wires)

        # Wire gauge filter
        gauge_label = QtWidgets.QLabel("Gauge:")
        self.wire_gauge_combo = QtWidgets.QComboBox()
        self.wire_gauge_combo.addItems(
            ["All Gauges", "12 AWG", "14 AWG", "16 AWG", "18 AWG", "20 AWG", "22 AWG"]
        )
        self.wire_gauge_combo.currentTextChanged.connect(self._filter_wires)

        wire_filter_row.addWidget(wire_type_label)
        wire_filter_row.addWidget(self.wire_type_combo)
        wire_filter_row.addStretch()
        wire_filter_row.addWidget(gauge_label)
        wire_filter_row.addWidget(self.wire_gauge_combo)
        wire_search_layout.addLayout(wire_filter_row)

        # Wire control buttons
        wire_control_row = QtWidgets.QHBoxLayout()

        # Clear wire filters
        wire_clear_btn = QtWidgets.QPushButton("Clear")
        wire_clear_btn.clicked.connect(self._clear_wire_filters)
        wire_clear_btn.setMaximumWidth(60)

        # Add custom wire
        add_wire_btn = QtWidgets.QPushButton("Add Custom")
        add_wire_btn.clicked.connect(self._add_custom_wire)
        add_wire_btn.setMaximumWidth(80)

        wire_control_row.addStretch()
        wire_control_row.addWidget(add_wire_btn)
        wire_control_row.addWidget(wire_clear_btn)
        wire_search_layout.addLayout(wire_control_row)

        lay.addWidget(wire_search_frame)

        # Wire results count
        self.wire_results_label = QtWidgets.QLabel("Loading wires...")
        self.wire_results_label.setStyleSheet("color: #cccccc; font-size: 11px; margin: 5px;")
        lay.addWidget(self.wire_results_label)

        # Wire list with enhanced styling
        self.wire_list = QtWidgets.QListWidget()
        self.wire_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.wire_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
        """
        )
        lay.addWidget(self.wire_list)

        # Active wire selection indicator
        self.active_wire_label = QtWidgets.QLabel("Active Wire: None selected")
        self.active_wire_label.setStyleSheet(
            "color: #888888; font-style: italic; margin-top: 10px;"
        )
        lay.addWidget(self.active_wire_label)

        # Connect selection changes
        self.wire_list.itemSelectionChanged.connect(self._on_wire_selection_changed)

        # Store all wires for filtering
        self.all_wires = []

        # Populate with available wires from database
        self._populate_wire_spool_from_database()

        lay.addStretch()
        self.left_tab_widget.addTab(w, "Wire Spool")

    def _on_wire_selection_changed(self):
        """Handle wire selection changes per spec."""
        current_item = self.wire_list.currentItem()
        if current_item:
            wire_data = current_item.data(Qt.ItemDataRole.UserRole)
            if wire_data:
                wire_sku = wire_data.get("sku", "Unknown")
                self.active_wire_label.setText(f"Active Wire: {wire_sku}")
                self.wire_label_status.setText(f"Wire: {wire_sku}")
            else:
                # Fallback for simple text items
                wire_text = current_item.text().split(" - ")[0]
                self.active_wire_label.setText(f"Active Wire: {wire_text}")
                self.wire_label_status.setText(f"Wire: {wire_text}")
        else:
            self.active_wire_label.setText("Active Wire: None selected")
            self.wire_label_status.setText("Wire: None")

    def _populate_wire_spool_from_database(self):
        """Load available wires from database and populate the wire spool."""
        try:
            import sqlite3

            _logger.info("Loading wires from database for wire spool...")

            con = sqlite3.connect("autofire.db")
            cur = con.cursor()

            # Get wires with their types
            cur.execute(
                """
                SELECT w.name, w.gauge, w.color, wt.code AS type,
                       w.ohms_per_1000ft, w.max_current_a, w.model
                FROM wires w
                LEFT JOIN wire_types wt ON w.type_id = wt.id
                ORDER BY w.gauge, w.name
            """
            )

            wire_rows = cur.fetchall()
            con.close()

            # Convert to wire data structures and store for filtering
            wires = []
            for wire_row in wire_rows:
                name, gauge, color, wire_type, ohms, max_current, model = wire_row

                wire_data = {
                    "name": name,
                    "gauge": gauge,
                    "color": color,
                    "type": wire_type or "",
                    "ohms_per_1000ft": ohms,
                    "max_current_a": max_current,
                    "model": model or "",
                }
                wires.append(wire_data)

            # Store all wires for filtering
            self.all_wires = wires

            # Update wire list with all wires initially
            self._update_wire_list(wires)

            # Update results count
            self.wire_results_label.setText(f"Showing {len(wires)} wires")

            _logger.info(f"✅ Populated wire spool with {len(wires)} wires from database")

        except Exception as e:
            _logger.error(f"Failed to load wires from database: {e}")
            # Add fallback message
            self.wire_list.clear()
            item = QtWidgets.QListWidgetItem("No wires available - check database")
            self.wire_list.addItem(item)
            self.wire_results_label.setText("Error loading wires")

    def _setup_right_dock(self):
        """Setup right dock with Inspector tabs."""
        # Create tab widget for right dock
        self.right_tab_widget = QtWidgets.QTabWidget()

        # Properties tab
        self._setup_properties_tab()

        # Connections tab
        self._setup_connections_tab()

        # AI Suggestions tab
        self._setup_ai_tab()

        # Create dock
        right_dock = QtWidgets.QDockWidget("Inspector", self)
        right_dock.setWidget(self.right_tab_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)

    def _setup_properties_tab(self):
        """Setup properties tab with device selection and editing."""
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setSpacing(15)
        lay.setContentsMargins(15, 15, 15, 15)

        # Device selection info - cleaner styling
        self.selected_device_label = QtWidgets.QLabel("No device selected")
        self.selected_device_label.setStyleSheet(
            """
            font-weight: bold;
            font-size: 12px;
            padding: 8px 12px;
            background-color: #2d2d30;
            color: #ffffff;
            border: 1px solid #0078d4;
            border-radius: 4px;
            margin-bottom: 10px;
        """
        )
        lay.addWidget(self.selected_device_label)

        # Properties form - cleaner group box
        self.properties_form = QtWidgets.QGroupBox("Device Properties")
        self.properties_form.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #ffffff;
                border: 2px solid #0078d4;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #0078d4;
                font-weight: bold;
            }
        """
        )
        form_layout = QtWidgets.QFormLayout(self.properties_form)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(15, 20, 15, 15)

        # Form fields with cleaner styling
        self.prop_name = QtWidgets.QLineEdit()
        self.prop_name.setPlaceholderText("Device name")
        self.prop_name.setStyleSheet(
            """
            QLineEdit {
                padding: 6px 8px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """
        )
        form_layout.addRow("Name:", self.prop_name)

        self.prop_address = QtWidgets.QSpinBox()
        self.prop_address.setRange(1, 255)
        self.prop_address.setStyleSheet(
            """
            QSpinBox {
                padding: 6px 8px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 12px;
            }
            QSpinBox:focus {
                border-color: #0078d4;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                width: 16px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #4c4c4c;
            }
        """
        )
        form_layout.addRow("Address:", self.prop_address)

        self.prop_circuit = QtWidgets.QComboBox()
        self.prop_circuit.addItems(["NAC", "SLC", "Power", "Control"])
        self.prop_circuit.setStyleSheet(
            """
            QComboBox {
                padding: 6px 8px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 12px;
                min-width: 100px;
            }
            QComboBox:focus {
                border-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ffffff;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
            }
        """
        )
        form_layout.addRow("Circuit:", self.prop_circuit)

        self.prop_location = QtWidgets.QLineEdit()
        self.prop_location.setPlaceholderText("Room/area location")
        self.prop_location.setStyleSheet(
            """
            QLineEdit {
                padding: 6px 8px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """
        )
        form_layout.addRow("Location:", self.prop_location)

        lay.addWidget(self.properties_form)

        # Apply button - cleaner styling
        self.apply_props_button = QtWidgets.QPushButton("Apply Changes")
        self.apply_props_button.clicked.connect(self._apply_device_properties)
        self.apply_props_button.setEnabled(False)
        self.apply_props_button.setStyleSheet(
            """
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;
            }
        """
        )
        lay.addWidget(self.apply_props_button)

        # Documentation buttons
        docs_btns = QtWidgets.QHBoxLayout()
        self.open_cutsheet_btn = QtWidgets.QPushButton("Open Cutsheet")
        self.open_cutsheet_btn.setEnabled(False)
        self.open_cutsheet_btn.clicked.connect(lambda: self._open_device_doc("cutsheet"))
        docs_btns.addWidget(self.open_cutsheet_btn)
        self.open_manual_btn = QtWidgets.QPushButton("Open Manual")
        self.open_manual_btn.setEnabled(False)
        self.open_manual_btn.clicked.connect(lambda: self._open_device_doc("manual"))
        docs_btns.addWidget(self.open_manual_btn)
        lay.addLayout(docs_btns)

        # Device info display - cleaner
        self.device_info_text = QtWidgets.QTextEdit()
        self.device_info_text.setMaximumHeight(120)
        self.device_info_text.setReadOnly(True)
        self.device_info_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """
        )
        lay.addWidget(self.device_info_text)

        self.right_tab_widget.addTab(w, "Properties")

    def _setup_connections_tab(self):
        """Setup enhanced connections tab with hierarchical circuit display."""
        try:
            from frontend.panels.enhanced_connections import create_enhanced_connections_tab

            # Create the enhanced connections panel
            self.connections_panel = create_enhanced_connections_tab(self)

            # Connect signals for integration
            self.connections_panel.circuit_selected.connect(self._on_circuit_selected)
            self.connections_panel.device_selected.connect(self._on_device_selected)
            self.connections_panel.calculations_updated.connect(self._on_calculations_updated)

            self.right_tab_widget.addTab(self.connections_panel, "Connections")

        except ImportError as e:
            # Fallback to basic connections tab if enhanced version fails
            _logger.warning("Enhanced connections not available, using basic version: %s", e)
            self._setup_basic_connections_tab()

    def _setup_basic_connections_tab(self):
        """Setup basic connections tab (fallback)."""
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # Circuit type selection
        circuit_group = QtWidgets.QGroupBox("Circuit Configuration")
        circuit_layout = QtWidgets.QVBoxLayout(circuit_group)

        circuit_type_layout = QtWidgets.QHBoxLayout()
        circuit_type_layout.addWidget(QtWidgets.QLabel("Circuit Type:"))
        self.conn_circuit_combo = QtWidgets.QComboBox()
        self.conn_circuit_combo.addItems(["NAC", "SLC", "Power", "Control"])
        circuit_type_layout.addWidget(self.conn_circuit_combo)
        circuit_type_layout.addStretch()
        circuit_layout.addLayout(circuit_type_layout)

        # Wire type selection
        wire_layout = QtWidgets.QHBoxLayout()
        wire_layout.addWidget(QtWidgets.QLabel("Wire Type:"))
        self.conn_wire_combo = QtWidgets.QComboBox()
        self.conn_wire_combo.addItems(["14 AWG Red THHN", "12 AWG Black THHN", "10 AWG White THHN"])
        wire_layout.addWidget(self.conn_wire_combo)
        wire_layout.addStretch()
        circuit_layout.addLayout(wire_layout)

        lay.addWidget(circuit_group)

        # Device selection for connections
        devices_group = QtWidgets.QGroupBox("Device Connections")
        devices_layout = QtWidgets.QVBoxLayout(devices_group)

        # Available devices list
        devices_layout.addWidget(QtWidgets.QLabel("Select devices to connect:"))
        self.conn_device_list = QtWidgets.QListWidget()
        self.conn_device_list.setMaximumHeight(120)
        self.conn_device_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.MultiSelection
        )
        devices_layout.addWidget(self.conn_device_list)

        # Connection buttons
        conn_buttons_layout = QtWidgets.QHBoxLayout()
        self.connect_devices_button = QtWidgets.QPushButton("Connect Selected")
        self.connect_devices_button.clicked.connect(self._connect_selected_devices)
        conn_buttons_layout.addWidget(self.connect_devices_button)

        self.clear_conn_button = QtWidgets.QPushButton("Clear All")
        self.clear_conn_button.clicked.connect(self._clear_all_connections)
        conn_buttons_layout.addWidget(self.clear_conn_button)

        devices_layout.addLayout(conn_buttons_layout)

        lay.addWidget(devices_group)

        # Current connections display
        connections_group = QtWidgets.QGroupBox("Current Connections")
        connections_layout = QtWidgets.QVBoxLayout(connections_group)

        self.current_connections_list = QtWidgets.QListWidget()
        self.current_connections_list.setMaximumHeight(120)
        connections_layout.addWidget(self.current_connections_list)

        # Connection management buttons
        conn_mgmt_layout = QtWidgets.QHBoxLayout()
        self.remove_conn_button = QtWidgets.QPushButton("Remove Selected")
        self.remove_conn_button.clicked.connect(self._remove_selected_connection)
        conn_mgmt_layout.addWidget(self.remove_conn_button)

        self.calc_voltage_button = QtWidgets.QPushButton("Calculate Voltage Drop")
        self.calc_voltage_button.clicked.connect(self._calculate_voltage_drop)
        conn_mgmt_layout.addWidget(self.calc_voltage_button)

        connections_layout.addLayout(conn_mgmt_layout)

        lay.addWidget(connections_group)

        self.right_tab_widget.addTab(w, "Connections")

    def _setup_ai_tab(self):
        """Setup AI suggestions tab."""
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        self.ai_label = QtWidgets.QLabel("AI suggestions will appear here")
        lay.addWidget(self.ai_label)

        self.right_tab_widget.addTab(w, "AI Suggestions")

    def _setup_layers_panel(self):
        """Setup the layers panel dock."""
        # Layer manager is now accessed from toolbar
        pass

    def _setup_system_builder_panel(self):
        """Setup the direct CAD launcher (system builder)."""
        self.system_builder_panel = SystemBuilderWidget(self)
        self.system_builder_panel.cad_ready.connect(self._on_cad_ready)

        # Create dock for system builder
        system_dock = QtWidgets.QDockWidget("🔥 Professional Setup", self)
        system_dock.setObjectName("SystemBuilderDock")
        system_dock.setWidget(self.system_builder_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, system_dock)

        # Initially show the system builder for first-time setup
        system_dock.show()

    def _on_cad_ready(self, settings):
        """Handle CAD workspace ready with AI context."""
        self.ai_context = settings.get("ai_context", {})

        # Apply AI context to workspace
        self._apply_ai_context(settings)

        # Hide the system builder and show CAD tools
        system_dock = self.findChild(QtWidgets.QDockWidget, "SystemBuilderDock")
        if system_dock:
            system_dock.hide()

        # Show main CAD panels
        self._show_device_palette()
        self._show_wire_spool()

        print(f"🎯 CAD Workspace Ready with AI Context: {len(self.ai_context)} items loaded")

    def _apply_ai_context(self, settings):
        """Apply AI context to enhance workspace functionality."""
        ai_context = settings.get("ai_context", {})

        # Apply compliance settings
        compliance_level = ai_context.get("compliance_level", "Manual")
        if compliance_level == "Automatic":
            # Enable automatic compliance checking
            self.auto_compliance = True

        # Apply manufacturer preferences to device filtering
        preferred_mfgs = ai_context.get("preferred_manufacturers", [])
        if hasattr(self, "device_palette_tree") and preferred_mfgs:
            # This would enhance device filtering with regional preferences
            pass

        # Apply local code context
        fire_code = ai_context.get("fire_code", "Standard")
        nfpa_edition = ai_context.get("nfpa_edition", "NFPA 72-2019")

        # Store context for use by other tools
        self.fire_code_context = {
            "fire_code": fire_code,
            "nfpa_edition": nfpa_edition,
            "voltage_standards": ai_context.get("voltage_standards", ["24VDC"]),
            "wire_types": ai_context.get("wire_types", ["FPLR"]),
            "preferred_manufacturers": preferred_mfgs,
        }

    def _on_system_assembled(self, assembly_data):
        """Handle system assembly - populate Device Palette and Wire Spool per spec."""
        # Per specification: "Assemble → populates Device Palette and Wire Spool, seeds Connections"

        # Update device palette with staged devices
        self._populate_device_palette_from_assembly(assembly_data.get("devices", []))

        # Update wire spool with staged wires
        self._populate_wire_spool_from_assembly(assembly_data.get("wires", []))

        # Store assembly data for project
        self.assembly_data = assembly_data

        # Update status
        device_count = sum(d.get("quantity_planned", 0) for d in assembly_data.get("devices", []))
        self.statusBar().showMessage(
            f"System assembled: {device_count} devices available for placement"
        )

        # Auto-switch to devices tab to start placement workflow
        if hasattr(self, "left_tab_widget"):
            self.left_tab_widget.setCurrentIndex(0)  # Switch to Devices tab

    def _populate_device_palette_from_assembly(self, devices_data):
        """Populate device palette from assembled staging data."""
        # Clear existing device tree
        self.device_tree.clear()

        # Group devices by type for palette organization
        device_groups = {}
        for device in devices_data:
            device_type = device.get("device_type", "Other")
            if device_type not in device_groups:
                device_groups[device_type] = []
            device_groups[device_type].append(device)

        # Create tree structure per specification format
        for device_type, devices in device_groups.items():
            type_item = QtWidgets.QTreeWidgetItem([device_type])

            for device in devices:
                # Format: "Name - Model (Planned/Placed/Connected)"
                planned = device.get("quantity_planned", 0)
                placed = device.get("quantity_placed", 0)
                connected = device.get("quantity_connected", 0)

                device_name = f"{device.get('model', 'Unknown')} - {device.get('manufacturer', '')}"
                counter_text = f" ({planned}/{placed}/{connected})"

                device_item = QtWidgets.QTreeWidgetItem([device_name + counter_text])
                device_item.setData(0, Qt.ItemDataRole.UserRole, device)
                type_item.addChild(device_item)

            self.device_tree.addTopLevelItem(type_item)

        self.device_tree.expandAll()

    def _populate_wire_spool_from_assembly(self, wires_data):
        """Populate wire spool from assembled staging data."""
        # Clear existing wire spool
        if hasattr(self, "wire_list"):
            self.wire_list.clear()

            # Add staged wires with Ω/1000ft, remaining length, cost per spec
            for wire in wires_data:
                wire_text = (
                    f"{wire.get('sku', 'Unknown')} - "
                    f"{wire.get('resistance_per_1000ft', 0):.1f}Ω/1000ft - "
                    f"{wire.get('remaining_length', 0)}ft remaining - "
                    f"${wire.get('cost_per_foot', 0):.2f}/ft"
                )

                wire_item = QtWidgets.QListWidgetItem(wire_text)
                wire_item.setData(Qt.ItemDataRole.UserRole, wire)
                self.wire_list.addItem(wire_item)

    def _apply_device_properties(self):
        """Apply property changes to selected device."""
        # TODO: Implement device property updates
        self.statusBar().showMessage("Device properties updated")

    def _connect_selected_devices(self):
        """Connect selected devices in the connections panel."""
        selected_items = self.conn_device_list.selectedItems()
        if len(selected_items) < 2:
            QtWidgets.QMessageBox.warning(
                self, "Connection Error", "Please select at least 2 devices to connect."
            )
            return

        circuit_type = self.conn_circuit_combo.currentText()
        wire_type = self.conn_wire_combo.currentText()

        # Create connections between selected devices
        device_names = [item.text().split(" (")[0] for item in selected_items]
        connection_text = f"{circuit_type}: {' ↔ '.join(device_names)} ({wire_type})"

        # Add to current connections list
        self.current_connections_list.addItem(connection_text)

        self.statusBar().showMessage(
            f"Connected {len(device_names)} devices on {circuit_type} circuit"
        )

    def _clear_all_connections(self):
        """Clear all connections."""
        self.current_connections_list.clear()
        self.statusBar().showMessage("All connections cleared")

    def _remove_selected_connection(self):
        """Remove selected connection."""
        current_item = self.current_connections_list.currentItem()
        if current_item:
            row = self.current_connections_list.row(current_item)
            self.current_connections_list.takeItem(row)
            self.statusBar().showMessage("Connection removed")

    def _zoom_to_selection(self):
        """Zoom to selected items."""
        selected_items = self.scene.selectedItems()
        if selected_items:
            # Get bounding rect of selected items
            bounding_rect = QtCore.QRectF()
            for item in selected_items:
                bounding_rect = bounding_rect.united(item.sceneBoundingRect())

            if not bounding_rect.isEmpty():
                # Add some padding
                padding = 20
                bounding_rect.adjust(-padding, -padding, padding, padding)
                self.view.zoom_to_rect(bounding_rect)

    def _toggle_grid(self):
        """Toggle grid visibility."""
        self.view.toggle_grid()

    def _toggle_snap(self):
        """Toggle snap to grid."""
        self.scene.snap_enabled = not self.scene.snap_enabled
        status = "on" if self.scene.snap_enabled else "off"
        self.statusBar().showMessage(f"Snap: {status}")

    def _toggle_measure_tool(self):
        """Toggle measurement tool."""
        if hasattr(self, "measure_tool"):
            if self.measure_tool.active:
                self.measure_tool.cancel()
                self.statusBar().showMessage("Measure: Off")
            else:
                self.measure_tool.start()

    def _on_hide_conduit_fill_toggled(self, checked: bool) -> None:
        """Persist the 'hide_conduit_fill' preference and trigger a lightweight repaint.

        Note: This does not yet walk existing text items to reformat labels; it simply
        updates the preference and nudges the viewport to repaint so future draws use
        the new setting.
        """
        try:
            set_hide_conduit_fill(bool(checked))
            # User feedback
            try:
                self.statusBar().showMessage(
                    f"Hide Conduit Fill: {'On' if checked else 'Off'}", 2000
                )
            except Exception:
                pass
        finally:
            # Best-effort repaint
            try:
                self.view.viewport().update()
            except Exception:
                pass

    # --- Wire label overlay helpers ---
    def _infer_wire_spec_for_item(self, item) -> dict:
        """Infer a minimal wire spec for labeling from an item.

        Returns a dict with keys: conduit_kind, trade_size, wires (AWG->count)
        This MVP uses conservative defaults when attributes are missing.
        """
        # Try to pick up attributes if present on the item (future wiring can set these)
        conduit = getattr(item, "conduit_kind", "EMT")
        trade = getattr(item, "trade_size", '3/4"')
        awg = getattr(item, "wire_gauge", getattr(item, "awg", 18))
        count = getattr(item, "conductor_count", 2)
        try:
            awg = int(awg)
            count = int(count)
        except Exception:
            awg, count = 18, 2
        return {"conduit_kind": str(conduit), "trade_size": str(trade), "wires": {awg: count}}

    def update_wire_labels_overlay(self) -> None:
        """Create or update simple text labels along wire segments based on preferences."""
        try:
            if not hasattr(self, "layer_wires") or self.layer_wires is None:
                return
            for item in list(self.layer_wires.childItems() or []):
                # Compute label text
                spec = self._infer_wire_spec_for_item(item)
                label_text = format_label_for_ui(
                    conduit_kind=spec["conduit_kind"],
                    trade_size=spec["trade_size"],
                    wires=spec["wires"],
                )

                # Find or create the text item attached to this segment
                label_item = getattr(item, "_label_item", None)
                if label_text:
                    if label_item is None:
                        label_item = QtWidgets.QGraphicsSimpleTextItem(label_text)
                        label_item.setBrush(QtGui.QBrush(QtGui.QColor("#DADADA")))
                        try:
                            # Prefer explicit GraphicsItemFlag enum for PySide6
                            flag = (
                                QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations
                            )
                        except Exception:
                            # Fallback for environments where enum exposure differs
                            flag = QtWidgets.QGraphicsItem.ItemIgnoresTransformations  # type: ignore[attr-defined]
                        label_item.setFlag(flag, True)
                        label_item.setZValue(70)
                        # Attach as child so it moves with the segment
                        if hasattr(item, "addToGroup"):
                            # item is likely a group; fall back to scene add
                            self.scene.addItem(label_item)
                        else:
                            label_item.setParentItem(item)
                        setattr(item, "_label_item", label_item)
                    else:
                        label_item.setText(label_text)

                    # Position near the segment midpoint if possible
                    try:
                        ln = item.line()  # QGraphicsLineItem
                        mid_x = (ln.x1() + ln.x2()) / 2.0
                        mid_y = (ln.y1() + ln.y2()) / 2.0
                        label_item.setPos(mid_x + 6, mid_y - 6)
                    except Exception:
                        # Best-effort placement
                        pass
                else:
                    # Remove label if present
                    if label_item is not None:
                        try:
                            self.scene.removeItem(label_item)
                        except Exception:
                            pass
                        setattr(item, "_label_item", None)
        except Exception as e:
            # Non-fatal; show status for visibility
            try:
                self.statusBar().showMessage(f"Label update error: {e}", 3000)
            except Exception:
                pass

    def _start_text_tool(self):
        """Start the text annotation tool."""
        if hasattr(self, "text_tool"):
            self.text_tool.start()
            self.statusBar().showMessage("Text: Click to place text")

    def _start_mtext_tool(self):
        """Start the multi-line text annotation tool."""
        if hasattr(self, "mtext_tool"):
            self.mtext_tool.start()
            self.statusBar().showMessage("MText: Click to place multi-line text")

    def _update_tool_status(self, tool_name):
        """Update the tool status indicator."""
        if hasattr(self, "tool_label"):
            self.tool_label.setText(f"Tool: {tool_name}")

    def _update_connections_device_list(self):
        """Update the device list in connections panel with placed devices."""
        if hasattr(self, "conn_device_list"):
            self.conn_device_list.clear()
            # Get all device items from the scene
            for item in self.devices_group.childItems():
                if hasattr(item, "name") and hasattr(item, "part_number"):
                    device_text = f"{item.name}"
                    if hasattr(item, "part_number") and item.part_number:
                        device_text += f" ({item.part_number})"
                    list_item = QtWidgets.QListWidgetItem(device_text)
                    list_item.setData(QtCore.Qt.ItemDataRole.UserRole, item)
                    self.conn_device_list.addItem(list_item)

    def on_layer_changed(self, layer_id: int, property_name: str, value):
        """Handle layer property changes."""
        # Update layer visibility/opacity in the scene
        if property_name == "visible":
            self._update_layer_visibility(layer_id, value)
        elif property_name == "opacity":
            self._update_layer_opacity(layer_id, value)
        elif property_name == "color":
            # Update color for layer items (would need item tagging)
            pass
        elif property_name == "locked":
            # Update locked state (would affect editing)
            pass

    def on_layer_selected(self, layer_id: int):
        """Handle layer selection changes."""
        self.active_layer_id = layer_id
        layer = self.layer_manager.get_layer(layer_id)
        if layer:
            self.statusBar().showMessage(f"Active layer: {layer.name}")
            self.layer_label.setText(f"Layer: {layer.name}")

    def _update_layer_visibility(self, layer_id: int, visible: bool):
        """Update visibility of items on a specific layer."""
        layer = self.layer_manager.get_layer(layer_id)
        if not layer:
            return

        # Map layer types to graphics groups
        if layer.type == "devices":
            self.devices_group.setVisible(visible)
        elif layer.type == "wiring":
            self.layer_wires.setVisible(visible)
        elif layer.type == "annotations":
            self.layer_sketch.setVisible(visible)
        elif layer.type == "coverage":
            self.layer_overlay.setVisible(visible)
        # Add more mappings as needed

    def _update_layer_opacity(self, layer_id: int, opacity: float):
        """Update opacity of items on a specific layer."""
        layer = self.layer_manager.get_layer(layer_id)
        if not layer:
            return

        # Map layer types to graphics groups
        if layer.type == "devices":
            self.devices_group.setOpacity(opacity)
        elif layer.type == "wiring":
            self.layer_wires.setOpacity(opacity)
        elif layer.type == "annotations":
            self.layer_sketch.setOpacity(opacity)
        elif layer.type == "coverage":
            self.layer_overlay.setOpacity(opacity)
        elif layer_id == 3:  # Annotations layer
            self.layer_sketch.setOpacity(opacity)

    def _populate_device_tree(self):
        """Populate the device tree with devices from the database."""
        _logger.info("Starting device tree population...")

        try:
            # Load devices from catalog
            _logger.info("Loading devices from catalog...")
            devices = load_catalog()
            _logger.info(f"Loaded {len(devices)} devices from catalog")

            # Store all devices for filtering
            self.all_devices = devices

            # Populate manufacturer dropdown
            self._populate_manufacturers()

            # Update the tree with all devices initially
            self._update_device_tree(devices)

            # Update results count
            self.results_label.setText(f"Showing {len(devices)} devices")

            _logger.info("✅ Successfully populated device tree with %d devices", len(devices))

        except Exception as e:
            _logger.error("Failed to populate device tree: %s", e)
            try:
                self.device_tree.clear()
                item = QtWidgets.QTreeWidgetItem([f"Error loading devices: {e}"])
                self.device_tree.addTopLevelItem(item)
                self.results_label.setText("Error loading devices")
            except Exception:
                pass

    def _update_device_tree(self, devices):
        """Update the device tree with the given device list."""
        self.device_tree.clear()

        if not devices:
            item = QtWidgets.QTreeWidgetItem(["No devices found"])
            self.device_tree.addTopLevelItem(item)
            return

        # Group devices by type for better organization
        grouped = {}
        for d in devices:
            cat = d.get("type", "Unknown") or "Unknown"
            grouped.setdefault(cat, []).append(d)

        # Add devices to tree
        for cat in sorted(grouped.keys()):
            cat_item = QtWidgets.QTreeWidgetItem([f"{cat} ({len(grouped[cat])})"])
            cat_item.setExpanded(True)  # Expand categories by default

            for dev in sorted(grouped[cat], key=lambda x: x.get("name", "")):
                name_txt = f"{dev.get('name','<unknown>')}"
                symbol = dev.get("symbol", "")
                if symbol:
                    name_txt += f" ({symbol})"

                mfg_txt = dev.get("manufacturer", "") or ""
                pn_txt = dev.get("part_number", "") or ""

                it = QtWidgets.QTreeWidgetItem([name_txt, mfg_txt, pn_txt])
                it.setData(0, Qt.ItemDataRole.UserRole, dev)
                cat_item.addChild(it)

            self.device_tree.addTopLevelItem(cat_item)

    def _filter_devices(self):
        """Filter devices based on search text, type, and manufacturer filters."""
        search_text = self.device_search.text().lower().strip()
        category_filter = self.filter_combo.currentText()
        manufacturer_filter = getattr(self, "manufacturer_combo", None)
        manufacturer_filter = (
            manufacturer_filter.currentText() if manufacturer_filter else "All Manufacturers"
        )

        if not hasattr(self, "all_devices"):
            return

        filtered_devices = []

        for device in self.all_devices:
            # Apply manufacturer filter first
            if manufacturer_filter != "All Manufacturers":
                device_mfg = device.get("manufacturer", "").strip()
                if device_mfg != manufacturer_filter:
                    continue

            # Apply category filter
            if category_filter != "All Types":
                device_type = device.get("type", "").lower()
                device_name = device.get("name", "").lower()

                # Check if device matches the category filter
                if category_filter in self.device_type_mapping:
                    keywords = self.device_type_mapping[category_filter]
                    if not any(
                        keyword in device_type or keyword in device_name for keyword in keywords
                    ):
                        continue

            # Apply search filter with enhanced logic
            if search_text:
                # Support AND/OR operators for advanced search
                if " AND " in search_text.upper():
                    search_terms = [
                        term.strip().lower() for term in search_text.upper().split(" AND ")
                    ]
                    searchable_text = " ".join(
                        [
                            device.get("name", ""),
                            device.get("manufacturer", ""),
                            device.get("part_number", ""),
                            device.get("type", ""),
                            device.get("symbol", ""),
                        ]
                    ).lower()

                    if not all(term in searchable_text for term in search_terms):
                        continue
                elif " OR " in search_text.upper():
                    search_terms = [
                        term.strip().lower() for term in search_text.upper().split(" OR ")
                    ]
                    searchable_text = " ".join(
                        [
                            device.get("name", ""),
                            device.get("manufacturer", ""),
                            device.get("part_number", ""),
                            device.get("type", ""),
                            device.get("symbol", ""),
                        ]
                    ).lower()

                    if not any(term in searchable_text for term in search_terms):
                        continue
                else:
                    # Simple search
                    searchable_text = " ".join(
                        [
                            device.get("name", ""),
                            device.get("manufacturer", ""),
                            device.get("part_number", ""),
                            device.get("type", ""),
                            device.get("symbol", ""),
                        ]
                    ).lower()

                    if search_text not in searchable_text:
                        continue

            filtered_devices.append(device)

        # Update tree with filtered results
        self._update_device_tree(filtered_devices)

        # Update results count
        total = len(self.all_devices) if hasattr(self, "all_devices") else 0
        self.results_label.setText(f"Showing {len(filtered_devices)} of {total} devices")

    def _clear_filters(self):
        """Clear all filters and show all devices."""
        self.device_search.clear()
        self.filter_combo.setCurrentIndex(0)  # "All Types"
        if hasattr(self, "manufacturer_combo"):
            self.manufacturer_combo.setCurrentIndex(0)  # "All Manufacturers"
        if hasattr(self, "all_devices"):
            self._update_device_tree(self.all_devices)
            self.results_label.setText(f"Showing {len(self.all_devices)} devices")

    def _toggle_advanced_search(self, enabled):
        """Toggle advanced search features."""
        # Placeholder for advanced search features
        if enabled:
            # Could add regex support, boolean operators, etc.
            self.device_search.setPlaceholderText(
                "Advanced search: use 'AND', 'OR', regex patterns..."
            )
        else:
            self.device_search.setPlaceholderText("Search devices, manufacturers, part numbers...")

    def _populate_manufacturers(self):
        """Populate manufacturer dropdown with unique manufacturers from devices."""
        if not hasattr(self, "all_devices") or not self.all_devices:
            return

        manufacturers = set()
        for device in self.all_devices:
            mfg = device.get("manufacturer", "").strip()
            if mfg:
                manufacturers.add(mfg)

        # Clear and repopulate manufacturer combo
        self.manufacturer_combo.clear()
        self.manufacturer_combo.addItem("All Manufacturers")
        for mfg in sorted(manufacturers):
            self.manufacturer_combo.addItem(mfg)

    # Wire filtering methods
    def _filter_wires(self):
        """Filter wires based on search text, type, and gauge filters."""
        search_text = self.wire_search.text().lower().strip()
        type_filter = self.wire_type_combo.currentText()
        gauge_filter = self.wire_gauge_combo.currentText()

        if not hasattr(self, "all_wires"):
            return

        filtered_wires = []

        for wire in self.all_wires:
            # Apply type filter
            if type_filter != "All Types":
                wire_type = wire.get("type", "").lower()
                wire_name = wire.get("name", "").lower()

                # Map filter to wire type keywords
                type_keywords = {
                    "SLC/IDC": ["slc", "idc", "signal", "initiating"],
                    "NAC": ["nac", "notification", "appliance"],
                    "Power": ["power", "supply", "battery"],
                    "Riser": ["riser", "cmr"],
                    "Plenum": ["plenum", "cmp"],
                }

                if type_filter in type_keywords:
                    keywords = type_keywords[type_filter]
                    if not any(
                        keyword in wire_type or keyword in wire_name for keyword in keywords
                    ):
                        continue

            # Apply gauge filter
            if gauge_filter != "All Gauges":
                wire_gauge = str(wire.get("gauge", ""))
                filter_gauge = gauge_filter.split()[0]  # Extract number from "14 AWG"
                if filter_gauge not in wire_gauge:
                    continue

            # Apply search filter
            if search_text:
                searchable_text = " ".join(
                    [
                        wire.get("name", ""),
                        wire.get("color", ""),
                        str(wire.get("gauge", "")),
                        wire.get("type", ""),
                        str(wire.get("ohms_per_1000ft", "")),
                        str(wire.get("max_current_a", "")),
                    ]
                ).lower()

                if search_text not in searchable_text:
                    continue

            filtered_wires.append(wire)

        # Update wire list with filtered results
        self._update_wire_list(filtered_wires)

        # Update results count
        total = len(self.all_wires) if hasattr(self, "all_wires") else 0
        self.wire_results_label.setText(f"Showing {len(filtered_wires)} of {total} wires")

    def _clear_wire_filters(self):
        """Clear all wire filters and show all wires."""
        self.wire_search.clear()
        self.wire_type_combo.setCurrentIndex(0)  # "All Types"
        self.wire_gauge_combo.setCurrentIndex(0)  # "All Gauges"
        if hasattr(self, "all_wires"):
            self._update_wire_list(self.all_wires)
            self.wire_results_label.setText(f"Showing {len(self.all_wires)} wires")

    def _add_custom_wire(self):
        """Add a custom wire to the spool."""
        # Placeholder for adding custom wire functionality
        from PySide6 import QtWidgets

        dialog = QtWidgets.QInputDialog()
        dialog.setWindowTitle("Add Custom Wire")
        dialog.setLabelText("Enter wire specification (e.g., '16 AWG Red SLC'):")
        dialog.setTextValue("")

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            wire_spec = dialog.textValue().strip()
            if wire_spec:
                # Create a simple custom wire entry
                custom_wire = {
                    "name": f"Custom: {wire_spec}",
                    "gauge": 16,  # Default
                    "color": "Unknown",
                    "type": "Custom",
                    "ohms_per_1000ft": 4.0,  # Default
                    "max_current_a": 10.0,  # Default
                    "model": "CUSTOM",
                    "sku": wire_spec,
                }

                # Add to wire list
                self.all_wires.append(custom_wire)
                self._filter_wires()  # Refresh display

    def _update_wire_list(self, wires):
        """Update the wire list widget with the given wires."""
        self.wire_list.clear()

        if not wires:
            item = QtWidgets.QListWidgetItem("No wires found")
            self.wire_list.addItem(item)
            return

        for wire in wires:
            gauge = wire.get("gauge", 0)
            color = wire.get("color", "Unknown")
            wire_type = wire.get("type", "")
            ohms = wire.get("ohms_per_1000ft", 0.0)
            max_current = wire.get("max_current_a", 0.0)

            # Create display text
            if wire_type:
                display_name = f"{gauge} AWG {wire_type} - {color}"
            else:
                display_name = f"{gauge} AWG - {color}"

            specs = f"({ohms:.1f} Ω/1000ft, {max_current:.0f}A)"
            full_display = f"{display_name} {specs}"

            # Create list item
            item = QtWidgets.QListWidgetItem(full_display)

            # Store wire data
            wire_data = dict(wire)
            wire_data["sku"] = display_name
            item.setData(Qt.ItemDataRole.UserRole, wire_data)

            self.wire_list.addItem(item)

    def _setup_properties_dock(self):
        """Setup the properties dock."""
        dock = QtWidgets.QDockWidget("Properties", self)
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # Properties will be populated when devices are selected
        self.properties_label = QtWidgets.QLabel("Select a device to view properties")
        lay.addWidget(self.properties_label)

        dock.setWidget(w)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def _setup_ai_dock(self):
        """Setup the AI Assistant dock."""
        dock = AssistantDock(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

    def _setup_status_summary_dock(self):
        """Setup the Canvas Status Summary dock."""
        self.status_summary = CanvasStatusSummary(self)

        dock = QtWidgets.QDockWidget("System Status", self)
        dock.setWidget(self.status_summary)
        dock.setObjectName("StatusSummaryDock")
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # Add to right side, below the right dock
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        # Initially show the status summary
        dock.show()

    def _setup_status_bar(self):
        """Setup the status bar with all required elements."""
        # Coordinates
        self.coord_label = QtWidgets.QLabel("0.00, 0.00 ft")
        self.statusBar().addWidget(self.coord_label)

        # Zoom level
        self.zoom_label = QtWidgets.QLabel("Zoom: 100%")
        self.statusBar().addWidget(self.zoom_label)

        # Selection count
        self.selection_label = QtWidgets.QLabel("Sel: 0")
        self.statusBar().addWidget(self.selection_label)

        # Active layer
        self.layer_label = QtWidgets.QLabel("Layer: Default")
        self.statusBar().addWidget(self.layer_label)

        # Snap toggle
        self.snap_label = QtWidgets.QLabel("Snap: On")
        self.statusBar().addWidget(self.snap_label)

        # Active tool
        self.tool_label = QtWidgets.QLabel("Tool: Select")
        self.statusBar().addWidget(self.tool_label)

        # Active wire
        self.wire_label_status = QtWidgets.QLabel("Wire: None")
        self.statusBar().addWidget(self.wire_label_status)

        # Warning banner (right side)
        self.warning_label = QtWidgets.QLabel("")
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.statusBar().addPermanentWidget(self.warning_label)

        self.statusBar().showMessage("Model Space - Ready")

    def _setup_menus(self):
        """Setup complete menu bar per spec."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = file_menu.addAction("&New Project")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_project)

        open_action = file_menu.addAction("&Open Project...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_project)

        save_action = file_menu.addAction("&Save Project")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_project)

        save_as_action = file_menu.addAction("Save Project &As...")
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_project_as)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("E&xit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        undo_action = edit_menu.addAction("&Undo")
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(lambda: self.undo())

        redo_action = edit_menu.addAction("&Redo")
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(lambda: self.redo())

        # Preferences
        edit_menu.addSeparator()
        prefs_action = edit_menu.addAction("&Preferences...")
        prefs_action.setShortcut("Ctrl+,")
        prefs_action.triggered.connect(self._open_preferences)

        # View menu
        view_menu = menubar.addMenu("&View")
        zoom_in_action = view_menu.addAction("Zoom &In")
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(lambda: self.view.zoom_in())

        zoom_out_action = view_menu.addAction("Zoom &Out")
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(lambda: self.view.zoom_out())

        zoom_fit_action = view_menu.addAction("&Fit to Screen")
        zoom_fit_action.setShortcut("Ctrl+0")
        zoom_fit_action.triggered.connect(lambda: self.view.zoom_fit())

        view_menu.addSeparator()

        # Simple grid toggle
        grid_action = view_menu.addAction("&Grid")
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.triggered.connect(lambda: self.view.toggle_grid())

        # Hide Conduit Fill toggle (affects wirepath label formatting)
        hide_fill_action = view_menu.addAction("Hide Conduit Fill")
        hide_fill_action.setCheckable(True)
        hide_fill_action.setChecked(get_hide_conduit_fill())
        hide_fill_action.toggled.connect(self._on_hide_conduit_fill_toggled)

        # Insert menu
        menubar.addMenu("&Insert")
        # Add insert options here

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        # Circuits Editor (v1)
        circuits_action = tools_menu.addAction("Open Circuits Editor")
        circuits_action.setShortcut("Ctrl+Shift+E")
        circuits_action.triggered.connect(self._open_circuits_editor)

        # System Builder menu
        system_menu = menubar.addMenu("&System Builder")

        # Add System Builder actions per specification
        show_system_builder_action = system_menu.addAction("Show &System Builder")
        show_system_builder_action.setShortcut("F3")
        show_system_builder_action.triggered.connect(self._show_system_builder)

        system_menu.addSeparator()

        stage_panels_action = system_menu.addAction("Stage &Panels...")
        stage_panels_action.triggered.connect(lambda: self._show_system_builder_tab(0))

        stage_devices_action = system_menu.addAction("Stage &Devices...")
        stage_devices_action.triggered.connect(lambda: self._show_system_builder_tab(1))

        stage_wires_action = system_menu.addAction("Stage &Wires...")
        stage_wires_action.triggered.connect(lambda: self._show_system_builder_tab(2))

        system_policies_action = system_menu.addAction("System &Policies...")
        system_policies_action.triggered.connect(lambda: self._show_system_builder_tab(3))

        system_menu.addSeparator()

        assemble_action = system_menu.addAction("&Assemble System")
        assemble_action.setShortcut("Ctrl+Shift+A")
        assemble_action.triggered.connect(self._assemble_system_from_menu)

        # Connections menu
        menubar.addMenu("&Connections")
        # Add connection options

        # Reports menu
        reports_menu = menubar.addMenu("&Reports")
        # BOM CSV export
        export_bom_action = reports_menu.addAction("Generate &BOM (CSV)...")
        export_bom_action.setShortcut("Ctrl+B")
        export_bom_action.triggered.connect(self._generate_bom_report)

        # Cable Schedule export
        export_cable_action = reports_menu.addAction("Generate &Cable Schedule (CSV)...")
        export_cable_action.setShortcut("Ctrl+Shift+C")
        export_cable_action.triggered.connect(self._generate_cable_schedule)

        # Report bundle export
        export_bundle_action = reports_menu.addAction("Export Report &Bundle...")
        export_bundle_action.setShortcut("Ctrl+Shift+R")
        export_bundle_action.triggered.connect(self._export_report_bundle)

        # HTML Submittal Pack
        export_html_action = reports_menu.addAction("Export &Submittal Pack (HTML)...")
        export_html_action.setShortcut("Ctrl+Alt+H")
        export_html_action.triggered.connect(self._export_submittal_html)

        # ZIP bundle export
        export_zip_action = reports_menu.addAction("Export Submittal &Bundle (ZIP)...")
        export_zip_action.setShortcut("Ctrl+Alt+Z")
        export_zip_action.triggered.connect(self._export_report_bundle_zip)

        # Compliance menu
        menubar.addMenu("&Compliance")
        # Add compliance options

        # Window menu
        window_menu = menubar.addMenu("&Window")
        try:
            wm = getattr(self.app_controller, "window_manager", None)
        except Exception:
            wm = None
        if wm:
            ensure_visible = window_menu.addAction("Ensure All Windows Visible")
            ensure_visible.triggered.connect(wm.ensure_windows_visible)

            window_menu.addSeparator()

            profiles_menu = window_menu.addMenu("Layout Profiles")
            try:
                from window_management_system import WindowProfile  # type: ignore

                profiles_menu.addAction(
                    "Designer",
                    lambda: wm.apply_layout_profile(WindowProfile.DESIGNER),
                )
                profiles_menu.addAction(
                    "Engineer",
                    lambda: wm.apply_layout_profile(WindowProfile.ENGINEER),
                )
                profiles_menu.addAction(
                    "Manager",
                    lambda: wm.apply_layout_profile(WindowProfile.MANAGER),
                )
                profiles_menu.addAction(
                    "Dual Monitor",
                    lambda: wm.apply_layout_profile(WindowProfile.DUAL_MONITOR),
                )
            except Exception:
                # Profiles unavailable; continue with basic actions only
                pass

            window_menu.addSeparator()

            # Save/Load layouts
            save_layout = window_menu.addAction("Save Current Layout…")

            def _save_layout():
                from PySide6.QtWidgets import QInputDialog

                name, ok = QInputDialog.getText(self, "Save Layout", "Layout name:")
                if ok and name.strip():
                    try:
                        wm.save_current_layout(name.strip())
                        self.statusBar().showMessage(f"Saved layout '{name.strip()}'", 4000)
                    except Exception:
                        pass

            save_layout.triggered.connect(_save_layout)

            load_layout = window_menu.addAction("Load Layout…")

            def _load_layout():
                from PySide6.QtWidgets import QInputDialog

                try:
                    names = wm.get_available_layouts()
                except Exception:
                    names = []
                if not names:
                    return
                name, ok = QInputDialog.getItem(
                    self, "Load Layout", "Choose a layout:", names, 0, False
                )
                if ok and name:
                    try:
                        wm.load_layout(name)
                        self.statusBar().showMessage(f"Loaded layout '{name}'", 4000)
                    except Exception:
                        pass

            load_layout.triggered.connect(_load_layout)
        else:
            disabled = window_menu.addAction("Window Manager unavailable")
            disabled.setEnabled(False)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about)

        # Export menu for sheets
        export_menu = menubar.addMenu("E&xport")
        export_sheet_action = export_menu.addAction("Export Sheet (SVG/PNG/PDF)...")
        export_sheet_action.setShortcut("Ctrl+P")
        export_sheet_action.triggered.connect(self._export_title_block_sheet)

    def _open_preferences(self):
        """Open Preferences dialog and persist updates."""
        try:
            from backend.preferences import load_preferences, update_preferences
            from frontend.dialogs.preferences import PreferencesDialog
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Preferences", f"Preferences unavailable: {e}")
            return

        # Start with current prefs merged with stored file (so unknown keys persist)
        current = {}
        try:
            current = load_preferences()
            # Include any runtime-only keys from controller.prefs if present
            if isinstance(self.app_controller.prefs, dict):
                current.update(
                    {k: v for k, v in self.app_controller.prefs.items() if k not in current}
                )
        except Exception:
            current = dict(getattr(self, "prefs", {}) or {})

        dlg = PreferencesDialog(self, initial=current)
        if not dlg.exec():
            return

        new_vals = dlg.values()
        try:
            merged = update_preferences(new_vals)
            # Update controller and window prefs in-memory
            if isinstance(self.app_controller.prefs, dict):
                self.app_controller.prefs.update(merged)
            self.prefs.update(merged)
            self.statusBar().showMessage("Preferences saved", 4000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Preferences", f"Failed to save preferences: {e}")

    def _show_system_builder(self):
        """Show the System Builder dock."""
        # Find and show the system builder dock
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if dock.windowTitle() == "System Builder":
                dock.show()
                dock.raise_()
                dock.activateWindow()
                break

    def _generate_bom_report(self):
        """Generate a simple BOM CSV by aggregating placed devices."""
        try:
            from backend.reports import generate_bom_csv
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Reports", f"Reports module unavailable: {e}")
            return

        # Choose destination path
        default_dir = str(
            self.prefs.get(
                "report_default_dir",
                os.path.join(os.getcwd(), "artifacts", "reports"),
            )
        )
        try:
            os.makedirs(default_dir, exist_ok=True)
        except Exception:
            pass
        default_path = os.path.join(default_dir, "bom.csv")

        dest_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save BOM As",
            default_path,
            "CSV Files (*.csv);;All Files (*)",
        )
        if not dest_path:
            return

        # Collect device-like items from devices group
        items = []
        try:
            if self.devices_group:
                items = list(self.devices_group.childItems())
        except Exception:
            items = []

        try:
            result = generate_bom_csv(items, dest_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "BOM Export Failed", str(e))
            return

        # Notify
        total_lines = result.get("unique_items", 0)
        total_qty = result.get("total_qty", 0)
        self.statusBar().showMessage(
            f"BOM saved: {dest_path} (items: {total_lines}, qty: {total_qty})"
        )
        QtWidgets.QMessageBox.information(
            self,
            "BOM Exported",
            f"Saved to:\n{dest_path}\n\nUnique items: {total_lines}\nTotal quantity: {total_qty}",
        )

    def _generate_cable_schedule(self):
        """Generate a cable schedule CSV from wire items."""
        try:
            from backend.reports import generate_cable_schedule_csv
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Reports", f"Reports module unavailable: {e}")
            return

        default_dir = str(
            self.prefs.get(
                "report_default_dir",
                os.path.join(os.getcwd(), "artifacts", "reports"),
            )
        )
        try:
            os.makedirs(default_dir, exist_ok=True)
        except Exception:
            pass
        default_path = os.path.join(default_dir, "cable_schedule.csv")

        dest_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Cable Schedule As",
            default_path,
            "CSV Files (*.csv);;All Files (*)",
        )
        if not dest_path:
            return

        wire_items = []
        try:
            if self.layer_wires:
                wire_items = list(self.layer_wires.childItems())
        except Exception:
            wire_items = []

        try:
            result = generate_cable_schedule_csv(wire_items, dest_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Cable Schedule Export Failed", str(e))
            return

        groups = result.get("groups", 0)
        total_len = result.get("total_length_ft", 0.0)
        self.statusBar().showMessage(
            f"Cable schedule saved: {dest_path} (groups: {groups}, total ft: {total_len:.2f})"
        )
        QtWidgets.QMessageBox.information(
            self,
            "Cable Schedule Exported",
            f"Saved to:\n{dest_path}\n\nGroups: {groups}\nTotal length (ft): {total_len:.2f}",
        )

    def _export_report_bundle(self):
        """Export a BOM + Cable Schedule into a folder."""
        try:
            from backend.reports import export_report_bundle
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Reports", f"Reports module unavailable: {e}")
            return

        default_dir = str(
            self.prefs.get(
                "report_default_dir",
                os.path.join(os.getcwd(), "artifacts", "reports", "bundle"),
            )
        )
        try:
            os.makedirs(default_dir, exist_ok=True)
        except Exception:
            pass

        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Choose Report Folder", default_dir
        )
        if not folder:
            return

        device_items = []
        wire_items = []
        try:
            if self.devices_group:
                device_items = list(self.devices_group.childItems())
        except Exception:
            pass
        try:
            if self.layer_wires:
                wire_items = list(self.layer_wires.childItems())
        except Exception:
            pass

        try:
            summary = export_report_bundle(device_items, wire_items, folder)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Report Bundle Failed", str(e))
            return

        msg = (
            f"BOM: {summary.get('bom_path')} (unique: {summary.get('bom_unique')}, "
            f"qty: {summary.get('bom_qty')})\n"
            f"Cable: {summary.get('cable_path')} (groups: {summary.get('cable_groups')}, "
            f"segments: {summary.get('cable_segments')}, "
            f"length ft: {summary.get('cable_length_ft')})\n"
            f"Riser: {summary.get('riser_path')} (rows: {summary.get('riser_rows')})\n"
            f"Compliance: {summary.get('compliance_path')} (rows: {summary.get('compliance_rows')})"
        )
        self.statusBar().showMessage("Report bundle exported")
        QtWidgets.QMessageBox.information(self, "Report Bundle Exported", msg)

    def _export_submittal_html(self):
        """Export HTML submittal (index.html) and open it for print/copy."""
        try:
            from backend.reports import export_html_submittal
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Reports", f"Reports module unavailable: {e}")
            return

        default_dir = str(
            self.prefs.get(
                "report_default_dir",
                os.path.join(os.getcwd(), "artifacts", "reports", "submittal"),
            )
        )
        try:
            os.makedirs(default_dir, exist_ok=True)
        except Exception:
            pass
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Choose Submittal Folder", default_dir
        )
        if not folder:
            return

        device_items = []
        wire_items = []
        try:
            if self.devices_group:
                device_items = list(self.devices_group.childItems())
        except Exception:
            pass
        try:
            if self.layer_wires:
                wire_items = list(self.layer_wires.childItems())
        except Exception:
            pass

        try:
            out = export_html_submittal(device_items, wire_items, folder)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "HTML Submittal Failed", str(e))
            return

        index_path = out.get("index_path")
        self.statusBar().showMessage(f"Submittal exported: {index_path}")
        try:
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices

            if index_path:
                QDesktopServices.openUrl(QUrl.fromLocalFile(index_path))
        except Exception:
            pass

    def _export_report_bundle_zip(self):
        """Export a full submittal bundle as a ZIP archive."""
        try:
            from backend.reports import export_report_bundle_zip
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Reports", f"Reports module unavailable: {e}")
            return

        default_dir = str(
            self.prefs.get(
                "report_default_dir",
                os.path.join(os.getcwd(), "artifacts", "reports"),
            )
        )
        try:
            os.makedirs(default_dir, exist_ok=True)
        except Exception:
            pass
        default_path = os.path.join(default_dir, "submittal_bundle.zip")

        dest_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Submittal Bundle As",
            default_path,
            "ZIP Files (*.zip);;All Files (*)",
        )
        if not dest_path:
            return

        device_items = []
        wire_items = []
        try:
            if self.devices_group:
                device_items = list(self.devices_group.childItems())
        except Exception:
            pass
        try:
            if self.layer_wires:
                wire_items = list(self.layer_wires.childItems())
        except Exception:
            pass

        try:
            summary = export_report_bundle_zip(device_items, wire_items, dest_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "ZIP Export Failed", str(e))
            return

        self.statusBar().showMessage(f"Submittal bundle saved: {summary.get('zip_path')}")
        QtWidgets.QMessageBox.information(
            self,
            "Submittal Bundle Exported",
            f"Saved to:\n{summary.get('zip_path')}\n\n"
            f"Includes: index.html, device_documents.html, BOM, Cable, Riser, Compliance",
        )

    def _generate_riser(self):
        """Generate riser CSV."""
        try:
            from backend.reports import generate_riser_csv
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Reports", f"Reports module unavailable: {e}")
            return

        default_dir = str(
            self.prefs.get(
                "report_default_dir",
                os.path.join(os.getcwd(), "artifacts", "reports"),
            )
        )
        try:
            os.makedirs(default_dir, exist_ok=True)
        except Exception:
            pass
        default_path = os.path.join(default_dir, "riser.csv")
        dest_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Riser As", default_path, "CSV Files (*.csv);;All Files (*)"
        )
        if not dest_path:
            return
        device_items = []
        try:
            if self.devices_group:
                device_items = list(self.devices_group.childItems())
        except Exception:
            pass
        try:
            result = generate_riser_csv(device_items, dest_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Riser Export Failed", str(e))
            return
        self.statusBar().showMessage(f"Riser saved: {dest_path} (rows: {result.get('rows', 0)})")
        QtWidgets.QMessageBox.information(
            self, "Riser Exported", f"Saved to:\n{dest_path}\nRows: {result.get('rows', 0)}"
        )

    def _generate_compliance_summary(self):
        """Generate compliance summary CSV."""
        try:
            from backend.reports import generate_compliance_summary_csv
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Reports", f"Reports module unavailable: {e}")
            return

        default_dir = str(
            self.prefs.get(
                "report_default_dir",
                os.path.join(os.getcwd(), "artifacts", "reports"),
            )
        )
        try:
            os.makedirs(default_dir, exist_ok=True)
        except Exception:
            pass
        default_path = os.path.join(default_dir, "compliance_summary.csv")
        dest_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Compliance Summary As", default_path, "CSV Files (*.csv);;All Files (*)"
        )
        if not dest_path:
            return
        device_items = []
        try:
            if self.devices_group:
                device_items = list(self.devices_group.childItems())
        except Exception:
            pass
        try:
            result = generate_compliance_summary_csv(device_items, dest_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Compliance Export Failed", str(e))
            return
        self.statusBar().showMessage(
            f"Compliance summary saved: {dest_path} (rows: {result.get('rows', 0)})"
        )
        QtWidgets.QMessageBox.information(
            self,
            "Compliance Summary Exported",
            f"Saved to:\n{dest_path}\nRows: {result.get('rows', 0)}",
        )

    def _show_system_builder_tab(self, tab_index: int):
        """Show System Builder and switch to specific tab."""
        self._show_system_builder()
        if hasattr(self, "system_builder_panel"):
            # New system builder uses content_stack instead of tab_widget
            if hasattr(self.system_builder_panel, "content_stack"):
                self.system_builder_panel.content_stack.setCurrentIndex(tab_index)
            # Fallback for backward compatibility
            elif hasattr(self.system_builder_panel, "tab_widget"):
                self.system_builder_panel.tab_widget.setCurrentIndex(tab_index)

    def _assemble_system_from_menu(self):
        """Trigger system assembly from menu."""
        if hasattr(self, "system_builder_panel"):
            self.system_builder_panel._assemble_system()
        else:
            QtWidgets.QMessageBox.information(
                self,
                "System Builder",
                "Please open the System Builder first to stage your system components.",
            )

    def undo(self):
        """Perform undo operation."""
        if hasattr(self, "command_stack") and self.command_stack:
            if self.command_stack.undo():
                description = self.command_stack.get_undo_description()
                self.statusBar().showMessage(f"Undid: {description}")
            else:
                self.statusBar().showMessage("Nothing to undo")

    def redo(self):
        """Perform redo operation."""
        if hasattr(self, "command_stack") and self.command_stack:
            if self.command_stack.redo():
                description = self.command_stack.get_redo_description()
                self.statusBar().showMessage(f"Redid: {description}")
            else:
                self.statusBar().showMessage("Nothing to redo")

    def show_about(self):
        """Show about dialog."""
        QtWidgets.QMessageBox.about(
            self,
            f"About {branding.PRODUCT_NAME}",
            f"{branding.PRODUCT_NAME} - Fire Alarm CAD System\nVersion {branding.get_version()}\n\n"
            "Professional fire alarm system design tool.",
        )

    def _open_circuits_editor(self):
        """Open the circuits editor dock with current device/wire items."""
        # Collect items similarly to report generators
        device_items = []
        wire_items = []
        try:
            if hasattr(self, "devices_group") and self.devices_group is not None:
                device_items = list(self.devices_group.childItems())
            if hasattr(self, "layer_wires") and self.layer_wires is not None:
                wire_items = list(self.layer_wires.childItems())
        except Exception:
            pass

        dock = QtWidgets.QDockWidget("Circuits Editor", self)
        widget = CircuitsEditor(self)
        widget.set_data(device_items, wire_items)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.show()

    def _export_title_block_sheet(self):
        try:
            from backend.title_block import (
                export_title_block_pdf_file,
                export_title_block_png_file,
                export_title_block_svg_file,
            )
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Export Error", f"Exporter unavailable: {e}")
            return

        # Build default metadata
        from datetime import datetime

        from backend import branding

        meta = {
            "sheet_title": "Fire Alarm Design Sheet",
            "project_name": getattr(self, "project_name", "Untitled Project"),
            "project_address": getattr(self, "project_address", ""),
            "designer": getattr(self, "designer_name", ""),
            "date": datetime.today().strftime("%Y-%m-%d"),
            "company": branding.PRODUCT_NAME,
            "company_contact": "",
        }

        dlg = QtWidgets.QFileDialog(self, "Export Sheet")
        dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)
        dlg.setNameFilters(["SVG Image (*.svg)", "PNG Image (*.png)", "PDF File (*.pdf)"])
        if not dlg.exec():
            return
        out_path = dlg.selectedFiles()[0]
        sel_filter = dlg.selectedNameFilter()
        try:
            if sel_filter.lower().startswith("svg") or out_path.lower().endswith(".svg"):
                if not out_path.lower().endswith(".svg"):
                    out_path += ".svg"
                export_title_block_svg_file(out_path, meta)
            elif sel_filter.lower().startswith("png") or out_path.lower().endswith(".png"):
                if not out_path.lower().endswith(".png"):
                    out_path += ".png"
                export_title_block_png_file(out_path, meta)
            else:
                if not out_path.lower().endswith(".pdf"):
                    out_path += ".pdf"
                export_title_block_pdf_file(out_path, meta)
            self.statusBar().showMessage(f"Exported sheet to {out_path}", 5000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Failed", str(e))

    def _new_project(self):
        """Create a new project and open System Builder for project setup."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "New Project",
            "Create a new project? Any unsaved changes will be lost.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # Clear current project
            self._clear_project()
            # Reset project data in controller
            if hasattr(self.app_controller, "current_project_path"):
                self.app_controller.current_project_path = None
            if hasattr(self.app_controller, "project_data"):
                self.app_controller.project_data = self.app_controller._get_default_project_data()

            # Show System Builder for new project setup
            self._show_system_builder()
            self.statusBar().showMessage(
                "New project - use System Builder to configure your design"
            )

    def _open_project(self):
        """Open an existing project."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Project", "", "AutoFire Projects (*.afp);;All Files (*)"
        )

        if file_path:
            if self.app_controller.load_project(file_path):
                self.statusBar().showMessage(f"Project opened: {file_path}")
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Open Failed", f"Failed to open project: {file_path}"
                )

    def _save_project(self):
        """Save the current project."""
        if (
            hasattr(self.app_controller, "current_project_path")
            and self.app_controller.current_project_path
        ):
            if self.app_controller.save_project(self.app_controller.current_project_path):
                self.statusBar().showMessage(
                    f"Project saved: {self.app_controller.current_project_path}"
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Save Failed",
                    f"Failed to save project: {self.app_controller.current_project_path}",
                )
        else:
            self._save_project_as()

    def _save_project_as(self):
        """Save the current project with a new name."""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Project As", "", "AutoFire Projects (*.afp);;All Files (*)"
        )

        if file_path:
            # Ensure .afp extension
            if not file_path.lower().endswith(".afp"):
                file_path += ".afp"

            if self.app_controller.save_project(file_path):
                self.statusBar().showMessage(f"Project saved: {file_path}")
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Save Failed", f"Failed to save project: {file_path}"
                )

    def _clear_project(self):
        """Clear all project data from the scene."""
        # Clear devices
        if self.devices_group:
            for item in self.devices_group.childItems():
                self.devices_group.removeFromGroup(item)

        # Clear wires
        if self.layer_wires:
            for item in self.layer_wires.childItems():
                self.layer_wires.removeFromGroup(item)

        # Clear drawings
        if self.layer_sketch:
            for item in self.layer_sketch.childItems():
                self.layer_sketch.removeFromGroup(item)

        # Clear overlays
        if self.layer_overlay:
            for item in self.layer_overlay.childItems():
                self.layer_overlay.removeFromGroup(item)

        # Reset view
        self.view.zoom_fit()

    def _initialize_tools(self):
        """Initialize CAD tools and state."""
        # Initialize tool state
        self.current_proto = None
        self.current_kind = "other"
        self.ghost = None
        self.show_coverage = bool(self.prefs.get("show_coverage", True))

        # Initialize drawing controller for wire routing
        self.draw = DrawController(self, self.layer_wires)

        # Initialize measurement tool (optional import)
        try:
            from cad_core.tools.measure_tool import MeasureTool  # type: ignore
        except Exception:

            class MeasureTool:  # type: ignore
                def __init__(self, *_, **__):
                    pass

        self.measure_tool = MeasureTool(self, self.layer_overlay)

        # Initialize text tools (optional import)
        try:
            from cad_core.tools.text_tool import (
                MTextTool,  # type: ignore
                TextTool,  # type: ignore
            )
        except Exception:

            class MTextTool:  # type: ignore
                def __init__(self, *_, **__):
                    pass

            class TextTool:  # type: ignore
                def __init__(self, *_, **__):
                    pass

        self.text_tool = TextTool(self, self.layer_sketch)
        self.mtext_tool = MTextTool(self, self.layer_sketch)

        # Initialize command stack for undo/redo
        self.command_stack = CADCommandStack()

        # Initialize history
        self.history = []
        self.history_index = -1

    def _connect_signals(self):
        """Connect to app controller signals."""
        # Connect device tree selection
        self.device_tree.itemClicked.connect(self.on_device_selected)

        # Connect scene selection changes
        self.scene.selectionChanged.connect(self.on_scene_selection_changed)

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

            # Extract name from the appropriate field
            # (support both direct catalog and assembly data)
            device_name = dev.get("name") or dev.get("model") or dev.get("device_type") or "Unknown"

            self.statusBar().showMessage(f"Selected: {device_name}")

            # Create ghost device for placement preview
            self._create_ghost_device(dev)

    def _create_ghost_device(self, device_proto):
        """Create ghost device for placement preview."""
        if self.ghost:
            self.scene.removeItem(self.ghost)
            self.ghost = None

        # Extract name and symbol from the appropriate fields
        # (support both direct catalog and assembly data)
        device_name = (
            device_proto.get("name")
            or device_proto.get("model")
            or device_proto.get("device_type")
            or "Unknown"
        )

        device_symbol = device_proto.get("symbol") or device_proto.get("uid") or "?"

        # Create ghost device (semi-transparent preview)
        device_type = device_proto.get("type", "other").lower()

        # Check if this should be a fire alarm panel ghost
        if device_type in ["panel", "fire_alarm_panel", "main_panel"]:
            from frontend.fire_alarm_panel import FireAlarmPanel

            self.ghost = FireAlarmPanel(
                0,
                0,
                device_symbol,
                device_name,
                device_proto.get("manufacturer", ""),
                device_proto.get("part_number", ""),
            )
        else:
            from frontend.device import DeviceItem

            self.ghost = DeviceItem(
                0,
                0,
                device_symbol,
                device_name,
                device_proto.get("manufacturer", ""),
                device_proto.get("part_number", ""),
            )

        # Make it semi-transparent and non-interactive
        self.ghost.setOpacity(0.5)
        self.ghost.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.ghost.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.ghost.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

        # Add to overlay layer so it appears on top
        self.layer_overlay.addToGroup(self.ghost)

    def on_scene_selection_changed(self):
        """Handle selection changes in the scene."""
        selected_items = self.scene.selectedItems()

        # Update selection count
        if hasattr(self, "selection_label"):
            self.selection_label.setText(f"Sel: {len(selected_items)}")

        # Update status summary with current canvas stats
        self._update_status_summary()

        # Update properties panel
        if selected_items:
            # Get the first selected item (for now, handle single selection)
            selected_item = selected_items[0]
            if hasattr(selected_item, "name"):  # It's a DeviceItem
                self._update_properties_panel(selected_item)
            else:
                self._clear_properties_panel()
        else:
            self._clear_properties_panel()

        # Update connections device list
        self._update_connections_device_list()

    def _update_properties_panel(self, device_item):
        """Update the properties panel with selected device info."""
        if hasattr(self, "selected_device_label"):
            self.selected_device_label.setText(f"Selected: {device_item.name}")

        if hasattr(self, "prop_name"):
            self.prop_name.setText(device_item.name)

        if hasattr(self, "prop_address"):
            # TODO: Get address from device data
            self.prop_address.setValue(1)

        if hasattr(self, "device_info_text"):
            info = f"Device: {device_item.name}\n"
            info += f"Symbol: {getattr(device_item, 'symbol', 'N/A')}\n"
            info += f"Manufacturer: {getattr(device_item, 'manufacturer', 'N/A')}\n"
            info += f"Part Number: {getattr(device_item, 'part_number', 'N/A')}\n"
            info += f"Position: ({device_item.x():.1f}, {device_item.y():.1f})"
            self.device_info_text.setPlainText(info)

        if hasattr(self, "apply_props_button"):
            self.apply_props_button.setEnabled(True)

        # Enable docs buttons when links exist
        try:
            from backend.device_docs import lookup_docs_for_item

            docs = lookup_docs_for_item(device_item)
            has_c = bool(docs.get("cutsheet"))
            has_m = bool(docs.get("manual"))
            if hasattr(self, "open_cutsheet_btn"):
                self.open_cutsheet_btn.setEnabled(has_c)
            if hasattr(self, "open_manual_btn"):
                self.open_manual_btn.setEnabled(has_m)
        except Exception:
            if hasattr(self, "open_cutsheet_btn"):
                self.open_cutsheet_btn.setEnabled(False)
            if hasattr(self, "open_manual_btn"):
                self.open_manual_btn.setEnabled(False)

    def _clear_properties_panel(self):
        """Clear the properties panel when no device is selected."""
        if hasattr(self, "selected_device_label"):
            self.selected_device_label.setText("No device selected")

        if hasattr(self, "prop_name"):
            self.prop_name.clear()

        if hasattr(self, "prop_address"):
            self.prop_address.setValue(1)

        if hasattr(self, "device_info_text"):
            self.device_info_text.clear()

        if hasattr(self, "apply_props_button"):
            self.apply_props_button.setEnabled(False)

        if hasattr(self, "open_cutsheet_btn"):
            self.open_cutsheet_btn.setEnabled(False)
        if hasattr(self, "open_manual_btn"):
            self.open_manual_btn.setEnabled(False)

    def _open_device_doc(self, kind: str):
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return
        device_item = selected_items[0]
        try:
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices

            from backend.device_docs import lookup_docs_for_item

            docs = lookup_docs_for_item(device_item)
            url = docs.get(kind)
            if url:
                QDesktopServices.openUrl(QUrl(url))
        except Exception:
            pass

    def _on_device_tree_context_menu(self, pos: QtCore.QPoint) -> None:
        item = self.device_tree.itemAt(pos)
        if not item:
            return
        dev = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(dev, dict):
            return
        menu = QtWidgets.QMenu(self)
        act_c = menu.addAction("Open Cutsheet")
        menu.addAction("Open Manual")
        chosen = menu.exec(self.device_tree.viewport().mapToGlobal(pos))
        if not chosen:
            return
        try:
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices

            from backend.device_docs import lookup_docs_for_spec

            docs = lookup_docs_for_spec(
                manufacturer=dev.get("manufacturer"),
                model=dev.get("model") or dev.get("symbol"),
                name=dev.get("name"),
                part_number=dev.get("part_number"),
            )
            url = docs.get("cutsheet") if chosen == act_c else docs.get("manual")
            if url:
                QDesktopServices.openUrl(QUrl(url))
        except Exception:
            pass

    def _update_status_summary(self):
        """Update the status summary with current canvas statistics."""
        if not hasattr(self, "status_summary"):
            return

        try:
            # Count devices by connection status
            device_items = [
                item for item in self.scene.items() if hasattr(item, "connection_status")
            ]

            placed = len(device_items)
            connected = len(
                [d for d in device_items if getattr(d, "connection_status", "") == "connected"]
            )
            unconnected = len(
                [d for d in device_items if getattr(d, "connection_status", "") == "unconnected"]
            )
            partial = len(
                [d for d in device_items if getattr(d, "connection_status", "") == "partial"]
            )

            # Count wire segments (simplified for now)
            wire_items = [item for item in self.scene.items() if hasattr(item, "length")]
            total_length = sum(getattr(item, "length", 0.0) for item in wire_items)
            circuits = len(
                set(
                    getattr(item, "circuit_id", 0)
                    for item in wire_items
                    if hasattr(item, "circuit_id")
                )
            )
            segments = len(wire_items)

            # System stats (basic for now)
            panel_items = [item for item in self.scene.items() if hasattr(item, "panel_type")]
            panels = len(panel_items)
            zones = 0  # Will be calculated when zone system is implemented
            voltage_drop = 0.0  # Will be calculated when electrical system is implemented
            battery_hours = 24.0  # Default assumption

            # Update the status summary
            self.status_summary.update_device_stats(placed, connected, unconnected, partial)
            self.status_summary.update_wire_stats(total_length, circuits, segments)
            self.status_summary.update_system_stats(panels, zones, voltage_drop, battery_hours)

        except Exception as e:
            _logger.warning(f"Failed to update status summary: {e}")

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

    def toggle_system_builder(self, on):
        """Toggle system builder panel visibility."""
        # System builder is now in right dock tabs
        if hasattr(self, "right_tab_widget"):
            # Find system builder tab and show it
            for i in range(self.right_tab_widget.count()):
                if self.right_tab_widget.tabText(i) == "Connections":
                    # Assuming connections tab has system builder
                    self.right_tab_widget.setCurrentIndex(i)
                    break

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
        # Check if project has unsaved changes
        if hasattr(self.app_controller, "is_modified") and self.app_controller.is_modified:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QtWidgets.QMessageBox.StandardButton.Save
                | QtWidgets.QMessageBox.StandardButton.Discard
                | QtWidgets.QMessageBox.StandardButton.Cancel,
                QtWidgets.QMessageBox.StandardButton.Save,
            )

            if reply == QtWidgets.QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QtWidgets.QMessageBox.StandardButton.Save:
                # Try to save
                try:
                    self._save_project()
                    # If save was cancelled (user hit cancel in file dialog), don't close
                    if (
                        hasattr(self.app_controller, "is_modified")
                        and self.app_controller.is_modified
                    ):
                        event.ignore()
                        return
                except Exception as e:
                    QtWidgets.QMessageBox.warning(
                        self, "Save Error", f"Could not save project: {e}"
                    )
                    event.ignore()
                    return

        # Notify controller about window closing - this will close all other windows too
        if hasattr(self.app_controller, "on_model_space_closed"):
            self.app_controller.on_model_space_closed()
        else:
            # Fallback: close application directly
            QtWidgets.QApplication.quit()

        event.accept()

    def _on_circuit_selected(self, circuit_id: str):
        """Handle circuit selection from enhanced connections panel."""
        _logger.info("Circuit selected: %s", circuit_id)
        self.statusBar().showMessage(f"Selected circuit: {circuit_id}")

        # Could highlight circuit items in the scene here
        # TODO: Integrate with scene highlighting

    def _on_device_selected(self, device_name: str):
        """Handle device selection from enhanced connections panel."""
        _logger.info("Device selected: %s", device_name)
        self.statusBar().showMessage(f"Selected device: {device_name}")

        # Could highlight device in the scene here
        # TODO: Integrate with scene highlighting

    def _on_calculations_updated(self):
        """Handle calculation updates from enhanced connections panel."""
        _logger.debug("Live calculations updated")

        # Could update other UI elements that depend on calculations
        # TODO: Integrate with other panels that need calculation results
