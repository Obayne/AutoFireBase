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

# Backend services
from backend.catalog import load_catalog
from backend.logging_config import setup_logging

# CAD command system for undo/redo
from cad_core.commands import CADCommandStack

# Drawing tools for wire routing
from cad_core.tools.draw import (
    DrawController,
    DrawMode,
)
from frontend.assistant import AssistantDock

# System builder for panel-based system design
from frontend.panels.improved_system_builder import (
    ImprovedGuidedSystemBuilder as SystemBuilderWidget,
)

# Layers panel for advanced layer management
from frontend.panels.layer_manager import LayerManager

# Status widgets
from frontend.widgets.canvas_status_summary import CanvasStatusSummary

# Grid scene and defaults used by the main window
from frontend.windows.scene import DEFAULT_GRID_SIZE, CanvasView, GridScene

# Ensure logging is configured early so module-level loggers emit during
# headless simulators and when the app starts from __main__.
setup_logging()

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

        toolbar.addSeparator()

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

        # Text annotation tools
        text_action = toolbar.addAction("Text")
        text_action.triggered.connect(self._start_text_tool)

        mtext_action = toolbar.addAction("MText")
        mtext_action.triggered.connect(self._start_mtext_tool)

        toolbar.addSeparator()

        # Navigation tools
        zoom_extents_action = toolbar.addAction("Zoom Extents")
        zoom_extents_action.triggered.connect(self.view.zoom_fit)

        zoom_selection_action = toolbar.addAction("Zoom Selection")
        zoom_selection_action.triggered.connect(self._zoom_to_selection)

        toolbar.addSeparator()

        # Grid and snap
        grid_action = toolbar.addAction("Grid")
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        grid_action.triggered.connect(self._toggle_grid)

        snap_action = toolbar.addAction("Snap")
        snap_action.setCheckable(True)
        snap_action.setChecked(bool(self.prefs.get("snap", True)))
        snap_action.triggered.connect(self._toggle_snap)

        toolbar.addSeparator()

        # Coverage overlays
        coverage_action = toolbar.addAction("Coverage")
        coverage_action.setCheckable(True)

        # Array fill
        array_action = toolbar.addAction("Array")
        array_action.setCheckable(True)

        # Measure
        measure_action = toolbar.addAction("Measure")
        measure_action.setCheckable(True)
        measure_action.triggered.connect(self._toggle_measure_tool)

        toolbar.addSeparator()

        # Layers
        self.layers_action = toolbar.addAction("Layers")
        self.layers_action.triggered.connect(self._show_layer_manager)

        # Undo/Redo
        toolbar.addSeparator()
        undo_action = toolbar.addAction("Undo")
        undo_action.triggered.connect(self.undo)

        redo_action = toolbar.addAction("Redo")
        redo_action.triggered.connect(self.redo)

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
        """Setup device palette tab."""
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
        self.left_tab_widget.addTab(w, "Devices")

    def _setup_wire_spool_tab(self):
        """Setup wire spool tab per specification."""
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)

        # Header per spec: "Wire Spool shows active reels with Ω/1000ft, remaining length, cost"
        spool_label = QtWidgets.QLabel("Wire Spool")
        spool_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        lay.addWidget(spool_label)

        # Wire list with radio button selection per spec
        self.wire_list = QtWidgets.QListWidget()
        self.wire_list.setStyleSheet(
            """
            QListWidget {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
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
        """Setup connections tab with device interconnection management."""
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
        """Setup the system builder panel dock."""
        self.system_builder_panel = SystemBuilderWidget(self)
        self.system_builder_panel.assembled.connect(self._on_system_assembled)

        # Create dock for system builder
        system_dock = QtWidgets.QDockWidget("System Builder", self)
        system_dock.setWidget(self.system_builder_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, system_dock)

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

    def _calculate_voltage_drop(self):
        """Calculate voltage drop for selected connection."""
        current_item = self.current_connections_list.currentItem()
        if current_item:
            # TODO: Implement actual voltage drop calculation
            QtWidgets.QMessageBox.information(
                self,
                "Voltage Drop",
                "Voltage drop calculation: 0.5V (2.1%)\n\n"
                "This is a placeholder - full calculation engine needed.",
            )
        else:
            QtWidgets.QMessageBox.warning(
                self, "Selection Error", "Please select a connection to calculate voltage drop."
            )

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
        """Populate the device tree with available devices from database."""
        try:
            # Load devices from database using the same source as System Builder
            devices = load_catalog()

            # Group devices by type for hierarchy
            grouped = {}
            for d in devices:
                cat = d.get("type", "Unknown") or "Unknown"
                grouped.setdefault(cat, []).append(d)

            # Clear existing tree
            self.device_tree.clear()

            for cat in sorted(grouped.keys()):
                cat_item = QtWidgets.QTreeWidgetItem([cat])
                for dev in sorted(grouped[cat], key=lambda x: x.get("name", "")):
                    txt = f"{dev.get('name','<unknown>')} ({dev.get('symbol','')})"
                    if dev.get("part_number"):
                        txt += f" - {dev.get('part_number')}"
                    it = QtWidgets.QTreeWidgetItem([txt])
                    it.setData(0, Qt.ItemDataRole.UserRole, dev)
                    cat_item.addChild(it)
                self.device_tree.addTopLevelItem(cat_item)
            self.device_tree.expandAll()

            _logger.info(f"Populated device tree with {len(devices)} devices from database")
        except Exception as e:
            _logger.error(f"Failed to populate device tree: {e}")
            # Fallback to empty tree instead of crashing
            self.device_tree.clear()

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

        # Insert menu
        menubar.addMenu("&Insert")
        # Add insert options here

        # Tools menu
        menubar.addMenu("&Tools")
        # Add basic tools here

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
        menubar.addMenu("&Reports")
        # Add report options

        # Compliance menu
        menubar.addMenu("&Compliance")
        # Add compliance options

        # Window menu
        menubar.addMenu("&Window")
        # Add window management options

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about)

    def _show_system_builder(self):
        """Show the System Builder dock."""
        # Find and show the system builder dock
        for dock in self.findChildren(QtWidgets.QDockWidget):
            if dock.windowTitle() == "System Builder":
                dock.show()
                dock.raise_()
                dock.activateWindow()
                break

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
            "About AutoFire",
            "AutoFire - Fire Alarm CAD System\nVersion 0.8.0\n\n"
            "Professional fire alarm system design tool.",
        )

    def _new_project(self):
        """Create a new project."""
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
            self.statusBar().showMessage("New project created")

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

        # Initialize measurement tool
        from cad_core.tools.measure_tool import MeasureTool

        self.measure_tool = MeasureTool(self, self.layer_overlay)

        # Initialize text tools
        from cad_core.tools.text_tool import (
            MTextTool,
            TextTool,
        )

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

            # Extract name from the appropriate field (support both direct catalog and assembly data)
            device_name = dev.get("name") or dev.get("model") or dev.get("device_type") or "Unknown"

            self.statusBar().showMessage(f"Selected: {device_name}")

            # Create ghost device for placement preview
            self._create_ghost_device(dev)

    def _create_ghost_device(self, device_proto):
        """Create ghost device for placement preview."""
        if self.ghost:
            self.scene.removeItem(self.ghost)
            self.ghost = None

        # Extract name and symbol from the appropriate fields (support both direct catalog and assembly data)
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
        # Notify controller about window closing
        if hasattr(self.app_controller, "on_model_space_closed"):
            self.app_controller.on_model_space_closed()
        event.accept()
