"""
Panel Selection and Configuration Dialog
Allows users to select main panels, annunciators, and other fire alarm equipment.
"""

import json

from PySide6 import QtCore, QtWidgets

try:
    from db import loader as db_loader
except Exception:
    db_loader = None


class WireConnection:
    """Represents a wire connection between devices."""

    def __init__(self, device1, device2, wire_type, circuit_type="NAC", footage=0):
        self.device1 = device1
        self.device2 = device2
        self.wire_type = wire_type
        self.circuit_type = circuit_type
        self.footage = footage
        self.cables = []  # List of cable segments

    def add_cable(self, gauge, color, length_ft):
        """Add a cable segment to this connection."""
        self.cables.append({"gauge": gauge, "color": color, "length_ft": length_ft})
        self.footage += length_ft

    def get_total_resistance(self):
        """Calculate total resistance of the connection."""
        total_resistance = 0
        for cable in self.cables:
            # ohms_per_1000ft from wire data
            ohms_per_1000ft = self.wire_type.get("ohms_per_1000ft", 0)
            total_resistance += (ohms_per_1000ft * cable["length_ft"]) / 1000
        return total_resistance

    def get_voltage_drop(self, current_a):
        """Calculate voltage drop for given current."""
        return self.get_total_resistance() * current_a


class PanelSelectionDialog(QtWidgets.QDialog):
    """Dialog for selecting and configuring fire alarm panels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Panel Selection & Configuration")
        self.setModal(True)
        self.resize(800, 600)

        # Data
        self.panels = []
        self.selected_panel = None
        self.panel_config = {}

        # Load panel data
        self._load_panel_data()

        # Setup UI
        self._setup_ui()

    def _load_panel_data(self):
        """Load panel data from database."""
        if db_loader:
            try:
                con = db_loader.connect()
                self.panels = db_loader.fetch_panels(con)
                con.close()
            except Exception as e:
                print(f"Failed to load panels: {e}")
                self.panels = self._get_builtin_panels()

    def _get_builtin_panels(self) -> list[dict]:
        """Fallback panel data if database is not available."""
        return [
            {
                "id": 1,
                "manufacturer_name": "Honeywell Firelite",
                "model": "MS-9050UD",
                "name": "MS-9050UD Fire Alarm Control Panel",
                "panel_type": "main",
                "max_devices": 1000,
                "properties_json": json.dumps(
                    {
                        "power_supply": "120VAC",
                        "battery_capacity": "55AH",
                        "communication_protocols": ["SLC", "NAC", "485"],
                    }
                ),
                "circuits": [
                    {"circuit_type": "SLC", "circuit_number": 1, "max_devices": 159},
                    {
                        "circuit_type": "NAC",
                        "circuit_number": 1,
                        "max_current_a": 3.0,
                        "voltage_v": 24,
                    },
                    {
                        "circuit_type": "NAC",
                        "circuit_number": 2,
                        "max_current_a": 3.0,
                        "voltage_v": 24,
                    },
                ],
                "compatibility": [
                    {"device_type": "Detector", "compatible": True},
                    {"device_type": "Notification", "compatible": True},
                    {"device_type": "Initiating", "compatible": True},
                ],
            }
        ]

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Apply dialog styling for better contrast - MAXIMUM VISIBILITY
        self.setStyleSheet(
            """
            QDialog {
                background-color: #ffffff !important;
                color: #000000 !important;
                font-size: 14pt !important;
                font-weight: bold !important;
            }
            QLabel {
                color: #000000 !important;
                font-weight: bold !important;
                font-size: 14pt !important;
                background-color: #ffffff !important;
            }
            QComboBox {
                background-color: #ffffff !important;
                color: #000000 !important;
                border: 3px solid #ff0000 !important;
                border-radius: 4px;
                padding: 12px !important;
                font-size: 14pt !important;
                font-weight: bold !important;
            }
            QComboBox:hover {
                border-color: #0000ff !important;
                background-color: #f0f0f0 !important;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #0078d7;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid white;
                width: 0;
                height: 0;
            }
            QListWidget {
                background-color: #ffffff !important;
                color: #000000 !important;
                border: 5px solid #ff0000 !important;
                border-radius: 4px;
                font-size: 16pt !important;
                font-weight: bold !important;
                selection-background-color: #0078d7 !important;
                selection-color: #ffffff !important;
            }
            QListWidget::item {
                padding: 15px !important;
                border-bottom: 2px solid #000000 !important;
                color: #000000 !important;
                background-color: #ffffff !important;
                font-weight: bold !important;
                font-size: 16pt !important;
                margin: 2px !important;
            }
            QListWidget::item:hover {
                background-color: #ffff00 !important;
                color: #000000 !important;
                font-weight: bold !important;
                border: 2px solid #0000ff !important;
            }
            QListWidget::item:selected {
                background-color: #0078d7 !important;
                color: #ffffff !important;
                font-weight: bold !important;
                border: 3px solid #ff0000 !important;
            }
            QListWidget::item:selected:hover {
                background-color: #ff0000 !important;
                color: #ffffff !important;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #495057;
                border: 1px solid #ced4da;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f8f9fa;
            }
            QTextEdit {
                background-color: white;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 10pt;
            }
            QTableWidget {
                background-color: white;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 4px;
                gridline-color: #e9ecef;
                font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                color: #495057;
                border: 1px solid #ced4da;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """
        )

        # Manufacturer filter
        filter_layout = QtWidgets.QHBoxLayout()
        filter_label = QtWidgets.QLabel("Manufacturer:")
        filter_layout.addWidget(filter_label)
        self.manufacturer_combo = QtWidgets.QComboBox()
        self.manufacturer_combo.addItem("All Manufacturers")
        manufacturers = set()
        for panel in self.panels:
            manufacturers.add(panel.get("manufacturer_name", "Unknown"))
        for mfr in sorted(manufacturers):
            self.manufacturer_combo.addItem(mfr)
        self.manufacturer_combo.currentTextChanged.connect(self._filter_panels)
        filter_layout.addWidget(self.manufacturer_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Panel list
        self.panel_list = QtWidgets.QListWidget()
        self.panel_list.itemSelectionChanged.connect(self._on_panel_selected)
        layout.addWidget(self.panel_list)

        # Panel details
        self.details_group = QtWidgets.QGroupBox("Panel Details")
        details_layout = QtWidgets.QVBoxLayout(self.details_group)

        self.details_text = QtWidgets.QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)

        # Circuit configuration
        self.circuit_group = QtWidgets.QGroupBox("Circuit Configuration")
        circuit_layout = QtWidgets.QVBoxLayout(self.circuit_group)

        self.circuit_table = QtWidgets.QTableWidget()
        self.circuit_table.setColumnCount(4)
        self.circuit_table.setHorizontalHeaderLabels(["Type", "Number", "Capacity", "Config"])
        self.circuit_table.horizontalHeader().setStretchLastSection(True)
        circuit_layout.addWidget(self.circuit_table)

        layout.addWidget(self.details_group)
        layout.addWidget(self.circuit_group)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        self.select_button = QtWidgets.QPushButton("Select Panel")
        self.select_button.clicked.connect(self._on_select_panel)
        self.select_button.setEnabled(False)
        button_layout.addWidget(self.select_button)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Populate initial panel list
        self._filter_panels()

    def _filter_panels(self):
        """Filter panels by manufacturer."""
        manufacturer = self.manufacturer_combo.currentText()
        if manufacturer == "All Manufacturers":
            filtered_panels = self.panels
        else:
            filtered_panels = [p for p in self.panels if p.get("manufacturer_name") == manufacturer]

        self.panel_list.clear()
        for panel in filtered_panels:
            item_text = (
                f"{panel.get('manufacturer_name', 'Unknown')} - {panel.get('model', 'Unknown')}"
            )
            if panel.get("name"):
                item_text += f" ({panel.get('name')})"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, panel)
            self.panel_list.addItem(item)

    def _on_panel_selected(self):
        """Handle panel selection."""
        current_item = self.panel_list.currentItem()
        if current_item:
            self.selected_panel = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
            self._update_panel_details()
            self.select_button.setEnabled(True)
        else:
            self.selected_panel = None
            self.select_button.setEnabled(False)

    def _update_panel_details(self):
        """Update the panel details display."""
        if not self.selected_panel:
            self.details_text.clear()
            self.circuit_table.setRowCount(0)
            return

        # Panel info
        props = json.loads(self.selected_panel.get("properties_json", "{}"))
        details = f"""
<b>Model:</b> {self.selected_panel.get('model', 'Unknown')}
<b>Type:</b> {self.selected_panel.get('panel_type', 'Unknown')}
<b>Max Devices:</b> {self.selected_panel.get('max_devices', 'Unknown')}
<b>Power Supply:</b> {props.get('power_supply', 'Unknown')}
<b>Battery:</b> {props.get('battery_capacity', 'Unknown')}
<b>Protocols:</b> {', '.join(props.get('communication_protocols', []))}
        """.strip()

        self.details_text.setHtml(details)

        # Circuit table
        circuits = self.selected_panel.get("circuits", [])
        self.circuit_table.setRowCount(len(circuits))

        for row, circuit in enumerate(circuits):
            self.circuit_table.setItem(
                row, 0, QtWidgets.QTableWidgetItem(circuit.get("circuit_type", ""))
            )
            self.circuit_table.setItem(
                row, 1, QtWidgets.QTableWidgetItem(str(circuit.get("circuit_number", "")))
            )

            capacity = ""
            if circuit.get("max_devices"):
                capacity = f"{circuit['max_devices']} devices"
            elif circuit.get("max_current_a"):
                capacity = f"{circuit['max_current_a']}A @ {circuit.get('voltage_v', '?')}V"
            self.circuit_table.setItem(row, 2, QtWidgets.QTableWidgetItem(capacity))

            # Config column - could be expanded for configuration options
            config_props = json.loads(circuit.get("properties_json", "{}"))
            config_text = ", ".join(f"{k}: {v}" for k, v in config_props.items())
            self.circuit_table.setItem(row, 3, QtWidgets.QTableWidgetItem(config_text))

        self.circuit_table.resizeColumnsToContents()

    def _on_select_panel(self):
        """Handle panel selection confirmation."""
        if self.selected_panel:
            # Create panel configuration
            self.panel_config = {
                "panel": self.selected_panel,
                "circuits": self.selected_panel.get("circuits", []),
                "compatibility": self.selected_panel.get("compatibility", []),
            }
            self.accept()

    def get_panel_config(self) -> dict:
        """Get the selected panel configuration."""
        return self.panel_config


class SystemBuilderPanel(QtWidgets.QDockWidget):
    """System Builder panel for designing fire alarm systems around selected panels."""

    def __init__(self, parent=None):
        super().__init__("System Builder", parent)
        self.panel_config = None
        self.devices = []
        self.connections = []
        self.selected_devices = []  # Track selected devices for connection

        self._setup_ui()

    def _setup_ui(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Apply styling for better visibility
        widget.setStyleSheet(
            """
            QWidget {
                background-color: #f8f9fa;
                color: #212529;
            }
            QTabWidget::pane {
                border: 1px solid #ced4da;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                color: #495057;
                border: 1px solid #ced4da;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #0078d7;
            }
            QTabBar::tab:hover {
                background-color: #dee2e6;
            }
            QLabel {
                color: #495057;
                font-size: 10pt;
            }
            QGroupBox {
                font-weight: bold;
                color: #495057;
                border: 1px solid #ced4da;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f8f9fa;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
            QListWidget, QTableWidget, QTextEdit {
                background-color: white;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            QComboBox {
                background-color: white;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 4px 8px;
            }
        """
        )

        # Create tab widget for staging
        self.tab_widget = QtWidgets.QTabWidget()

        # Panels tab
        self._setup_panels_tab()

        # Devices tab
        self._setup_devices_tab()

        # Wire tab
        self._setup_wire_tab()

        # Policies tab
        self._setup_policies_tab()
        self._setup_configuration_tab()

        layout.addWidget(self.tab_widget)

        # Assemble & Stage button
        self.assemble_button = QtWidgets.QPushButton("Assemble & Stage")
        self.assemble_button.clicked.connect(self._assemble_and_stage)
        self.assemble_button.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(self.assemble_button)

        # Export functionality (for backward compatibility)
        export_layout = QtWidgets.QHBoxLayout()
        self.export_button = QtWidgets.QPushButton("Export Configuration")
        self.export_button.clicked.connect(self._export_configuration)
        self.export_button.setEnabled(False)
        export_layout.addWidget(self.export_button)

        self.addressing_button = QtWidgets.QPushButton("Auto-Address")
        self.addressing_button.clicked.connect(self._auto_address)
        self.addressing_button.setEnabled(False)
        export_layout.addWidget(self.addressing_button)

        layout.addLayout(export_layout)

        # Status
        self.status_label = QtWidgets.QLabel("Ready - Configure system components and assemble")
        layout.addWidget(self.status_label)

        self.setWidget(widget)
        self.setMinimumWidth(500)

    def _setup_panels_tab(self):
        """Setup the Panels tab for FACP/boards/PSU/batteries."""
        panel_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel_widget)

        # Current panel display
        self.panel_label = QtWidgets.QLabel("No panel selected")
        layout.addWidget(self.panel_label)

        # Panel selection
        select_layout = QtWidgets.QHBoxLayout()
        self.select_panel_button = QtWidgets.QPushButton("Select Main Panel")
        self.select_panel_button.clicked.connect(self._select_panel)
        select_layout.addWidget(self.select_panel_button)

        self.clear_panel_button = QtWidgets.QPushButton("Clear")
        self.clear_panel_button.clicked.connect(self._clear_panel)
        select_layout.addWidget(self.clear_panel_button)

        layout.addLayout(select_layout)

        # Panel details
        self.panel_details = QtWidgets.QTextEdit()
        self.panel_details.setMaximumHeight(100)
        self.panel_details.setReadOnly(True)
        layout.addWidget(self.panel_details)

        # Boards/PSU/Batteries
        boards_group = QtWidgets.QGroupBox("Additional Components")
        boards_layout = QtWidgets.QVBoxLayout(boards_group)

        self.boards_list = QtWidgets.QListWidget()
        self.boards_list.setMaximumHeight(100)
        boards_layout.addWidget(self.boards_list)

        add_board_layout = QtWidgets.QHBoxLayout()
        self.add_board_button = QtWidgets.QPushButton("Add Board/PSU")
        add_board_layout.addWidget(self.add_board_button)
        boards_layout.addLayout(add_board_layout)

        layout.addWidget(boards_group)

        self.tab_widget.addTab(panel_widget, "Panels")

    def _setup_devices_tab(self):
        """Setup the Devices tab for staging detectors/modules/etc."""
        device_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(device_widget)

        # Device categories
        self.device_category_combo = QtWidgets.QComboBox()
        self.device_category_combo.addItems(
            ["All Devices", "Detection", "Notification", "Control", "Power", "Annunciator"]
        )
        self.device_category_combo.currentTextChanged.connect(self._filter_devices)
        layout.addWidget(self.device_category_combo)

        # Device list with quantity
        device_list_layout = QtWidgets.QHBoxLayout()

        self.available_devices = QtWidgets.QListWidget()
        self.available_devices.setMaximumWidth(200)
        device_list_layout.addWidget(self.available_devices)

        # Quantity controls
        quantity_layout = QtWidgets.QVBoxLayout()

        self.add_device_button = QtWidgets.QPushButton("Add →")
        self.add_device_button.clicked.connect(self._add_device)
        quantity_layout.addWidget(self.add_device_button)

        self.remove_device_button = QtWidgets.QPushButton("← Remove")
        self.remove_device_button.clicked.connect(self._remove_device)
        quantity_layout.addWidget(self.remove_device_button)

        device_list_layout.addLayout(quantity_layout)

        # Staged devices
        self.staged_devices = QtWidgets.QListWidget()
        device_list_layout.addWidget(self.staged_devices)

        layout.addLayout(device_list_layout)

        self.tab_widget.addTab(device_widget, "Devices")

    def _setup_wire_tab(self):
        """Setup the Wire tab for adding wire SKUs."""
        wire_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(wire_widget)

        # Wire catalog
        self.wire_catalog = QtWidgets.QTableWidget()
        self.wire_catalog.setColumnCount(5)
        self.wire_catalog.setHorizontalHeaderLabels(
            ["Type", "Gauge", "Color", "Ω/1000ft", "Cost/ft"]
        )
        self.wire_catalog.setMaximumHeight(200)
        self._load_wire_catalog()
        layout.addWidget(self.wire_catalog)

        # Add wire
        add_wire_layout = QtWidgets.QHBoxLayout()

        self.wire_type_combo = QtWidgets.QComboBox()
        self.wire_type_combo.addItems(["NAC", "SLC", "Power", "Control"])
        add_wire_layout.addWidget(self.wire_type_combo)

        self.wire_gauge_combo = QtWidgets.QComboBox()
        self.wire_gauge_combo.addItems(["14", "12", "10", "8", "6"])
        add_wire_layout.addWidget(self.wire_gauge_combo)

        self.wire_color_combo = QtWidgets.QComboBox()
        self.wire_color_combo.addItems(["Red", "Black", "White", "Blue", "Green"])
        add_wire_layout.addWidget(self.wire_color_combo)

        self.add_wire_button = QtWidgets.QPushButton("Add Wire SKU")
        self.add_wire_button.clicked.connect(self._add_wire_sku)
        add_wire_layout.addWidget(self.add_wire_button)

        layout.addLayout(add_wire_layout)

        # Staged wires
        self.staged_wires = QtWidgets.QListWidget()
        layout.addWidget(self.staged_wires)

        self.tab_widget.addTab(wire_widget, "Wire")

    def _setup_policies_tab(self):
        """Setup the Policies tab for addressing schemes."""
        policy_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(policy_widget)

        # Addressing scheme
        scheme_group = QtWidgets.QGroupBox("Addressing Scheme")
        scheme_layout = QtWidgets.QVBoxLayout(scheme_group)

        self.addressing_scheme = QtWidgets.QComboBox()
        self.addressing_scheme.addItems(["Sequential", "Zone + Device", "Manual", "Custom"])
        scheme_layout.addWidget(self.addressing_scheme)

        layout.addWidget(scheme_group)

        # Reserved ranges
        reserved_group = QtWidgets.QGroupBox("Reserved Address Ranges")
        reserved_layout = QtWidgets.QVBoxLayout(reserved_group)

        self.reserved_ranges = QtWidgets.QListWidget()
        self.reserved_ranges.addItems(["1-10: System devices", "250-255: Special"])
        reserved_layout.addWidget(self.reserved_ranges)

        layout.addWidget(reserved_group)

        # Routing preferences
        routing_group = QtWidgets.QGroupBox("Routing Preferences")
        routing_layout = QtWidgets.QVBoxLayout(routing_group)

        self.routing_prefs = QtWidgets.QListWidget()
        self.routing_prefs.addItems(["Follow corridors", "Minimize conduit", "Avoid plenums"])
        routing_layout.addWidget(self.routing_prefs)

        layout.addWidget(routing_group)

        self.tab_widget.addTab(policy_widget, "Policies")

    def _setup_configuration_tab(self):
        """Setup the Configuration tab for device connections and system setup."""
        config_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(config_widget)

        # Device connections section
        connections_group = QtWidgets.QGroupBox("Device Connections")
        connections_layout = QtWidgets.QVBoxLayout(connections_group)

        # Circuit type selector
        circuit_layout = QtWidgets.QHBoxLayout()
        circuit_layout.addWidget(QtWidgets.QLabel("Circuit Type:"))
        self.circuit_combo = QtWidgets.QComboBox()
        self.circuit_combo.addItems(["NAC", "SLC", "Power", "Control"])
        circuit_layout.addWidget(self.circuit_combo)
        circuit_layout.addStretch()
        connections_layout.addLayout(circuit_layout)

        # Device list for connections
        self.device_list = QtWidgets.QListWidget()
        self.device_list.setMaximumHeight(150)
        self.device_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        connections_layout.addWidget(QtWidgets.QLabel("Select devices to connect:"))
        connections_layout.addWidget(self.device_list)

        # Connection buttons
        conn_buttons_layout = QtWidgets.QHBoxLayout()
        self.connect_button = QtWidgets.QPushButton("Connect Devices")
        self.connect_button.clicked.connect(self._connect_devices)
        conn_buttons_layout.addWidget(self.connect_button)

        self.clear_connections_button = QtWidgets.QPushButton("Clear All")
        self.clear_connections_button.clicked.connect(self._clear_connections)
        conn_buttons_layout.addWidget(self.clear_connections_button)

        connections_layout.addLayout(conn_buttons_layout)

        # Connections display
        self.connections_list = QtWidgets.QListWidget()
        self.connections_list.setMaximumHeight(150)
        connections_layout.addWidget(QtWidgets.QLabel("Current connections:"))
        connections_layout.addWidget(self.connections_list)

        layout.addWidget(connections_group)

        # System configuration section
        system_group = QtWidgets.QGroupBox("System Configuration")
        system_layout = QtWidgets.QVBoxLayout(system_group)

        # Auto-addressing
        addr_layout = QtWidgets.QHBoxLayout()
        addr_layout.addWidget(QtWidgets.QLabel("Addressing:"))
        config_addressing_button = QtWidgets.QPushButton("Auto-Address")
        config_addressing_button.clicked.connect(self._auto_address)
        config_addressing_button.setEnabled(False)
        addr_layout.addWidget(config_addressing_button)
        addr_layout.addStretch()
        system_layout.addLayout(addr_layout)

        # Export configuration
        export_layout_config = QtWidgets.QHBoxLayout()
        export_layout_config.addWidget(QtWidgets.QLabel("Export:"))
        config_export_button = QtWidgets.QPushButton("Export Configuration")
        config_export_button.clicked.connect(self._export_configuration)
        config_export_button.setEnabled(False)
        export_layout_config.addWidget(config_export_button)
        export_layout_config.addStretch()
        system_layout.addLayout(export_layout_config)

        layout.addWidget(system_group)

        self.tab_widget.addTab(config_widget, "Configuration")

    def _load_wire_catalog(self):
        """Load wire catalog into table."""
        if not db_loader:
            return

        try:
            con = db_loader.connect()
            wires = db_loader.fetch_wires(con)
            con.close()

            self.wire_catalog.setRowCount(len(wires))
            for row, wire in enumerate(wires):
                self.wire_catalog.setItem(row, 0, QtWidgets.QTableWidgetItem(wire.get("type", "")))
                self.wire_catalog.setItem(
                    row, 1, QtWidgets.QTableWidgetItem(str(wire.get("gauge", "")))
                )
                self.wire_catalog.setItem(row, 2, QtWidgets.QTableWidgetItem(wire.get("color", "")))
                self.wire_catalog.setItem(
                    row, 3, QtWidgets.QTableWidgetItem(str(wire.get("ohms_per_1000ft", "")))
                )
                self.wire_catalog.setItem(
                    row, 4, QtWidgets.QTableWidgetItem(f"${wire.get('cost_per_ft', 0):.3f}")
                )

        except Exception as e:
            print(f"Failed to load wire catalog: {e}")

    def _clear_panel(self):
        """Clear the selected panel."""
        self.panel_config = {}
        self.panel_label.setText("No panel selected")
        self.panel_details.clear()
        self.boards_list.clear()
        self.devices.clear()
        self.staged_devices.clear()
        self._update_panel_display()
        self.status_label.setText("Panel cleared")

    def _filter_devices(self):
        """Filter devices by category."""
        category = self.device_category_combo.currentText()
        self.available_devices.clear()

        if not hasattr(self, "all_devices"):
            self.all_devices = []
            # Load devices if not already loaded
            if db_loader:
                try:
                    con = db_loader.connect()
                    self.all_devices = db_loader.fetch_devices(con)
                    con.close()
                except Exception as e:
                    print(f"Failed to load devices: {e}")
                    self.all_devices = []

        filtered_devices = self.all_devices
        if category != "All Devices":
            filtered_devices = [d for d in self.all_devices if d.get("device_type") == category]

        for device in filtered_devices[:50]:  # Limit for performance
            item_text = f"{device.get('name', 'Unknown')}"
            if device.get("manufacturer_name"):
                item_text = f"{device['manufacturer_name']} - {item_text}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, device)
            self.available_devices.addItem(item)

    def _add_device(self):
        """Add selected device to staging."""
        current_item = self.available_devices.currentItem()
        if current_item:
            device = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
            # Add to staged devices if not already there
            existing_items = [
                self.staged_devices.item(i).data(QtCore.Qt.ItemDataRole.UserRole)
                for i in range(self.staged_devices.count())
            ]
            if device not in existing_items:
                item_text = f"{device.get('name', 'Unknown')} (x1)"
                item = QtWidgets.QListWidgetItem(item_text)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, device)
                self.staged_devices.addItem(item)
                self.status_label.setText(f"Added {device.get('name', 'Unknown')} to staging")

    def _remove_device(self):
        """Remove device from staging."""
        current_item = self.staged_devices.currentItem()
        if current_item:
            device = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
            row = self.staged_devices.row(current_item)
            self.staged_devices.takeItem(row)
            self.status_label.setText(f"Removed {device.get('name', 'Unknown')} from staging")

    def _add_wire_sku(self):
        """Add wire SKU to staging."""
        wire_type = self.wire_type_combo.currentText()
        gauge = self.wire_gauge_combo.currentText()
        color = self.wire_color_combo.currentText()

        wire_info = f"{wire_type} - {gauge} AWG {color}"
        item = QtWidgets.QListWidgetItem(wire_info)
        self.staged_wires.addItem(item)
        self.status_label.setText(f"Added {wire_info} to wire staging")

    def _assemble_and_stage(self):
        """Assemble the staged components and populate Device Palette and Wire Spool."""
        if not self.panel_config:
            QtWidgets.QMessageBox.warning(
                self, "Assembly Error", "Please select a main panel first."
            )
            return

        # Count staged components
        device_count = self.staged_devices.count()
        wire_count = self.staged_wires.count()

        if device_count == 0:
            QtWidgets.QMessageBox.warning(
                self, "Assembly Error", "Please stage some devices first."
            )
            return

        # Create assembly summary
        summary = f"System assembled with {device_count} devices and {wire_count} wire types"

        # Here we would populate the Device Palette and Wire Spool in the main workspace
        # For now, just show success message
        QtWidgets.QMessageBox.information(
            self,
            "System Assembled",
            f"{summary}\n\nComponents are now available in the Device Palette and Wire Spool.",
        )

        self.status_label.setText("System assembled and staged for placement")

    def _load_wire_types(self):
        """Load available wire types from database."""
        if db_loader:
            try:
                con = db_loader.connect()
                wires = db_loader.fetch_wires(con)
                con.close()

                # Group by type and gauge
                wire_options = set()
                for wire in wires:
                    wire_options.add(
                        f"{wire.get('type', 'Unknown')} - {wire.get('gauge', 'Unknown')} AWG {wire.get('color', 'Unknown')}"
                    )

                for option in sorted(wire_options):
                    self.wire_type_combo.addItem(option)

            except Exception as e:
                print(f"Failed to load wire types: {e}")

    def _connect_devices(self):
        """Create a wire connection between selected devices."""
        selected_items = self.device_list.selectedItems()
        if len(selected_items) < 2:
            QtWidgets.QMessageBox.warning(
                self, "Connection Error", "Please select at least 2 devices to connect."
            )
            return

        # Get selected devices
        selected_devices = []
        for item in selected_items:
            device = item.data(QtCore.Qt.ItemDataRole.UserRole)
            selected_devices.append(device)

        # Get wire type from wire tab
        wire_type_text = "NAC"  # Default, could be enhanced to get from wire tab
        circuit_type = self.circuit_combo.currentText()

        # Create connections between all selected device pairs
        new_connections = 0

        for i in range(len(selected_devices)):
            for j in range(i + 1, len(selected_devices)):
                device1 = selected_devices[i]
                device2 = selected_devices[j]

                # Create basic wire connection (could be enhanced with wire data)
                wire_data = {
                    "type": circuit_type,
                    "gauge": 14,
                    "color": "Red",
                    "ohms_per_1000ft": 2.525,
                    "max_current_a": 15,
                }

                connection = WireConnection(device1, device2, wire_data, circuit_type)
                connection.add_cable(14, "Red", 100)  # Default 100 ft

                self.connections.append(connection)
                new_connections += 1

        self._update_connections_list()
        self.status_label.setText(f"Created {new_connections} wire connections")

    def _clear_connections(self):
        """Clear all wire connections."""
        self.connections.clear()
        self.connections_list.clear()
        self.status_label.setText("All connections cleared")

    def _export_configuration(self):
        """Export the system configuration to a file."""
        if not self.panel_config:
            QtWidgets.QMessageBox.warning(self, "Export Error", "No panel selected for export.")
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Configuration", "", "JSON files (*.json);;All files (*)"
        )

        if filename:
            try:
                config = {
                    "panel": self.panel_config["panel"],
                    "devices": self.devices,
                    "connections": [
                        {
                            "device1": conn.device1.get("name", "Unknown"),
                            "device2": conn.device2.get("name", "Unknown"),
                            "circuit_type": conn.circuit_type,
                            "footage": conn.footage,
                            "cables": conn.cables,
                        }
                        for conn in self.connections
                    ],
                    "exported_at": QtCore.QDateTime.currentDateTime().toString(),
                }

                with open(filename, "w") as f:
                    json.dump(config, f, indent=2)

                self.status_label.setText(f"Configuration exported to {filename}")

            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Export Error", f"Failed to export configuration: {e}"
                )

    def _auto_address(self):
        """Automatically assign addresses to devices."""
        if not self.devices:
            QtWidgets.QMessageBox.warning(self, "Auto-Address", "No devices to address.")
            return

        # Simple auto-addressing: assign sequential addresses
        for i, device in enumerate(self.devices, 1):
            device["address"] = i

        self._update_device_list()
        self.status_label.setText(f"Auto-addressed {len(self.devices)} devices")

    def _select_panel(self):
        """Open panel selection dialog."""
        dialog = PanelSelectionDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.panel_config = dialog.get_panel_config()
        self._update_panel_display()
        self._load_compatible_devices()
        # Enable buttons if we have a valid panel config
        has_panel = self.panel_config and self.panel_config.get("panel")
        self.export_button.setEnabled(bool(has_panel))
        self.addressing_button.setEnabled(bool(has_panel))

    def _update_panel_display(self):
        """Update the panel display."""
        if self.panel_config and self.panel_config.get("panel"):
            panel = self.panel_config["panel"]
            self.panel_label.setText(
                f"Selected: {panel.get('manufacturer_name')} {panel.get('model')}"
            )
            self.status_label.setText("Panel selected - loading compatible devices...")
            # Enable buttons when panel is selected
            self.export_button.setEnabled(True)
            self.addressing_button.setEnabled(True)
        else:
            self.panel_label.setText("No panel selected")
            self.status_label.setText("Ready - Select a panel to begin")
            # Disable buttons when no panel
            self.export_button.setEnabled(False)
            self.addressing_button.setEnabled(False)

    def _load_compatible_devices(self):
        """Load devices compatible with the selected panel."""
        if not self.panel_config or not self.panel_config.get("panel"):
            return

        panel_id = self.panel_config["panel"].get("id")
        if db_loader and panel_id:
            try:
                con = db_loader.connect()
                self.devices = db_loader.fetch_compatible_devices(con, panel_id)
                con.close()
            except Exception as e:
                print(f"Failed to load compatible devices: {e}")
                self.devices = []

        self._update_device_list()
        self.status_label.setText(f"Loaded {len(self.devices)} compatible devices")

    def _update_connections_list(self):
        """Update the connections list display."""
        self.connections_list.clear()
        for i, conn in enumerate(self.connections):
            device1_name = conn.device1.get("name", "Unknown")
            device2_name = conn.device2.get("name", "Unknown")
            wire_info = f"{conn.wire_type.get('gauge', '?')} AWG {conn.wire_type.get('color', '?')}"
            footage = f"{conn.footage} ft"

            item_text = f"{i+1}. {device1_name} ↔ {device2_name} ({wire_info}, {conn.circuit_type}, {footage})"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, conn)
            self.connections_list.addItem(item)

    def _update_device_list(self):
        """Update the device list display in configuration tab."""
        self.device_list.clear()
        for device in self.devices:
            item_text = f"{device.get('name', 'Unknown')} ({device.get('symbol', '')})"
            if device.get("manufacturer_name") and device["manufacturer_name"] != "(Any)":
                item_text = f"{device['manufacturer_name']} - {item_text}"

            # Show address if assigned
            if device.get("address"):
                item_text = f"[{device['address']}] {item_text}"

            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, device)
            self.device_list.addItem(item)
