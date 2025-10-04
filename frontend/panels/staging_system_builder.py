"""
System Builder - Staging Warehouse for AutoFire
Implements the specification's "System Builder (Staging Warehouse)" workflow
"""

from dataclasses import asdict, dataclass

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


@dataclass
class StagedPanel:
    """Represents a staged FACP panel."""

    uid: str
    model: str
    manufacturer: str
    slots: int = 0
    psu_capacity: float = 0.0
    battery_ah: float = 0.0
    outputs: int = 0
    quantity: int = 1


@dataclass
class StagedDevice:
    """Represents a staged device."""

    uid: str
    device_type: str  # detector, module, pull, NA, etc.
    model: str
    manufacturer: str
    symbol: str
    voltage: float = 24.0
    current_standby: float = 0.0
    current_alarm: float = 0.0
    quantity_planned: int = 0
    quantity_placed: int = 0
    quantity_connected: int = 0


@dataclass
class StagedWire:
    """Represents a staged wire type."""

    sku: str
    description: str
    gauge: int
    conductor_count: int
    resistance_per_1000ft: float  # ohms/1000ft
    capacitance_per_1000ft: float  # pF/1000ft
    reel_length: int = 1000
    cost_per_foot: float = 0.0
    remaining_length: int = 0


@dataclass
class StagingPolicies:
    """System staging policies."""

    addressing_scheme: str = "sequential"  # sequential, zone_based, custom
    reserved_ranges: list[tuple] | None = None
    routing_preference: str = "manual"  # manual, follow_path, auto_route
    auto_sizing: bool = True
    wire_derating: float = 1.25

    def __post_init__(self):
        if self.reserved_ranges is None:
            self.reserved_ranges = []


class SystemBuilderWidget(QWidget):
    """
    System Builder - Staging Warehouse Implementation

    Per specification section 3:
    - Panels tab: add FACP, boards, PSU, batteries
    - Devices tab: stage detectors, modules, pulls, NAs, annunciators, etc.
    - Wire tab: add wire SKUs, Ω/1000ft, capacitance, reel length, cost
    - Policies tab: addressing schemes, reserved ranges, routing preferences
    - Assemble → populates Device Palette and Wire Spool, seeds Connections
    """

    # Signals
    staging_changed = Signal()
    assembled = Signal(dict)  # Emitted when "Assemble" is clicked

    def __init__(self, parent=None):
        super().__init__(parent)

        # Staging data
        self.staged_panels: list[StagedPanel] = []
        self.staged_devices: list[StagedDevice] = []
        self.staged_wires: list[StagedWire] = []
        self.policies = StagingPolicies()

        self._setup_ui()
        self._load_defaults()

    def _setup_ui(self):
        """Setup the System Builder UI."""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("System Builder - Staging Warehouse")
        header_label.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                background-color: #0078d4;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 10px;
            }
        """
        )
        layout.addWidget(header_label)

        # Tab widget for the four main sections
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QTabBar::tab:hover {
                background-color: #404040;
            }
        """
        )

        # Create tabs
        self._setup_panels_tab()
        self._setup_devices_tab()
        self._setup_wires_tab()
        self._setup_policies_tab()

        layout.addWidget(self.tab_widget)

        # Assemble button
        assemble_layout = QHBoxLayout()
        assemble_layout.addStretch()

        self.assemble_btn = QPushButton("🔧 Assemble System")
        self.assemble_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #238636;
                color: #ffffff;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QPushButton:pressed {
                background-color: #1f6b32;
            }
        """
        )
        self.assemble_btn.clicked.connect(self._assemble_system)
        assemble_layout.addWidget(self.assemble_btn)

        layout.addLayout(assemble_layout)

        # Status label
        self.status_label = QLabel("System not assembled")
        self.status_label.setStyleSheet("color: #888888; font-style: italic; margin-top: 10px;")
        layout.addWidget(self.status_label)

    def _setup_panels_tab(self):
        """Setup the Panels tab for staging FACP, boards, PSU, batteries."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Add panel form
        form_group = QGroupBox("Add Panel/FACP")
        form_layout = QFormLayout(form_group)

        self.panel_uid = QLineEdit()
        self.panel_uid.setPlaceholderText("e.g., FACP-1")
        form_layout.addRow("UID:", self.panel_uid)

        self.panel_manufacturer = QComboBox()
        self.panel_manufacturer.addItems(
            [
                "Fire-Lite",
                "Notifier",
                "EST",
                "Honeywell",
                "Siemens",
                "Edwards",
                "System Sensor",
                "Other",
            ]
        )
        form_layout.addRow("Manufacturer:", self.panel_manufacturer)

        self.panel_model = QLineEdit()
        self.panel_model.setPlaceholderText("e.g., MS-9600LS")
        form_layout.addRow("Model:", self.panel_model)

        self.panel_slots = QSpinBox()
        self.panel_slots.setRange(0, 64)
        self.panel_slots.setValue(8)
        form_layout.addRow("Slots:", self.panel_slots)

        self.panel_psu = QSpinBox()
        self.panel_psu.setRange(0, 10)
        self.panel_psu.setValue(3)
        self.panel_psu.setSuffix(" A")
        form_layout.addRow("PSU Capacity:", self.panel_psu)

        self.panel_battery = QSpinBox()
        self.panel_battery.setRange(0, 200)
        self.panel_battery.setValue(18)
        self.panel_battery.setSuffix(" AH")
        form_layout.addRow("Battery:", self.panel_battery)

        add_panel_btn = QPushButton("Add Panel")
        add_panel_btn.clicked.connect(self._add_panel)
        form_layout.addWidget(add_panel_btn)

        layout.addWidget(form_group)

        # Staged panels table
        self.panels_table = QTableWidget()
        self.panels_table.setColumnCount(7)
        self.panels_table.setHorizontalHeaderLabels(
            ["UID", "Manufacturer", "Model", "Slots", "PSU (A)", "Battery (AH)", "Actions"]
        )
        self.panels_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.panels_table)

        self.tab_widget.addTab(widget, "Panels")

    def _setup_devices_tab(self):
        """Setup the Devices tab for staging detectors, modules, pulls, NAs, etc."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Add device form with database integration
        form_group = QGroupBox("Add Device Type from Catalog")
        form_layout = QFormLayout(form_group)

        # Load from database
        self.device_catalog = self._load_device_catalog()

        # Filtering controls
        filter_layout = QHBoxLayout()

        self.device_type_filter = QComboBox()
        self.device_type_filter.addItem("All Types")
        types = set()
        for device in self.device_catalog:
            if device.get("type"):
                types.add(device["type"])
        self.device_type_filter.addItems(sorted(types))
        self.device_type_filter.currentTextChanged.connect(self._filter_devices)

        self.device_mfr_filter = QComboBox()
        self.device_mfr_filter.addItem("All Manufacturers")
        manufacturers = set()
        for device in self.device_catalog:
            if device.get("manufacturer"):
                manufacturers.add(device["manufacturer"])
        self.device_mfr_filter.addItems(sorted(manufacturers))
        self.device_mfr_filter.currentTextChanged.connect(self._filter_devices)

        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.device_type_filter)
        filter_layout.addWidget(QLabel("Manufacturer:"))
        filter_layout.addWidget(self.device_mfr_filter)
        filter_layout.addStretch()

        form_layout.addRow(filter_layout)

        # Search field for model/name filtering
        search_layout = QHBoxLayout()
        self.device_search = QLineEdit()
        self.device_search.setPlaceholderText(
            "Search by model, name, or symbol (e.g., 'NFS2-3030', 'GEN-SD', 'Smoke')"
        )
        self.device_search.textChanged.connect(self._filter_devices)

        clear_search_btn = QPushButton("Clear")
        clear_search_btn.setStyleSheet(
            "padding: 4px 8px; border-radius: 3px; background-color: #6c757d; color: white;"
        )
        clear_search_btn.clicked.connect(lambda: self.device_search.clear())

        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.device_search)
        search_layout.addWidget(clear_search_btn)

        form_layout.addRow(search_layout)

        # Device selection from catalog
        self.device_catalog_list = QtWidgets.QListWidget()
        self.device_catalog_list.setMaximumHeight(120)
        self._populate_device_list()
        form_layout.addRow("Available Devices:", self.device_catalog_list)

        # Add button
        add_device_btn = QPushButton("🔹 Stage Selected Device")
        add_device_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """
        )
        add_device_btn.clicked.connect(self._add_device_from_catalog)
        form_layout.addWidget(add_device_btn)

        layout.addWidget(form_group)

        # Staged devices table
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(7)
        self.devices_table.setHorizontalHeaderLabels(
            ["Type", "Manufacturer", "Model", "Symbol", "Planned", "Placed", "Actions"]
        )
        self.devices_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.devices_table)

        self.tab_widget.addTab(widget, "Devices")

    def _load_device_catalog(self):
        """Load device catalog from database."""
        try:
            import sqlite3

            conn = sqlite3.connect("autofire.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT d.id, m.name as manufacturer, dt.code as type, d.model, d.name, d.symbol
                FROM devices d
                LEFT JOIN manufacturers m ON m.id = d.manufacturer_id
                LEFT JOIN device_types dt ON dt.id = d.type_id
                WHERE d.name IS NOT NULL AND d.name != ''
                ORDER BY m.name, dt.code, d.name
            """
            )

            devices = []
            for row in cursor.fetchall():
                devices.append(
                    {
                        "id": row[0],
                        "manufacturer": row[1] or "Unknown",
                        "type": row[2] or "Unknown",
                        "model": row[3] or "",
                        "name": row[4] or "Unnamed Device",
                        "symbol": row[5] or "?",
                    }
                )

            conn.close()
            return devices
        except Exception as e:
            print(f"Error loading device catalog: {e}")
            return self._get_fallback_devices()

    def _get_fallback_devices(self):
        """Fallback device list if database fails."""
        return [
            {
                "id": 1,
                "manufacturer": "System Sensor",
                "type": "Detector",
                "model": "2WT-B",
                "name": "Smoke Detector",
                "symbol": "SD",
            },
            {
                "id": 2,
                "manufacturer": "System Sensor",
                "type": "Detector",
                "model": "5602",
                "name": "Heat Detector",
                "symbol": "HD",
            },
            {
                "id": 3,
                "manufacturer": "Fire-Lite",
                "type": "Panel",
                "model": "MS-9600LS",
                "name": "Fire Alarm Control Panel",
                "symbol": "FACP",
            },
            {
                "id": 4,
                "manufacturer": "System Sensor",
                "type": "Notification",
                "model": "HS24-15/75W",
                "name": "Horn Strobe",
                "symbol": "HS",
            },
            {
                "id": 5,
                "manufacturer": "Fire-Lite",
                "type": "Initiating",
                "model": "BG-12",
                "name": "Pull Station",
                "symbol": "PS",
            },
        ]

    def _populate_device_list(self):
        """Populate the device list based on current filters and search."""
        self.device_catalog_list.clear()

        selected_type = self.device_type_filter.currentText()
        selected_mfr = self.device_mfr_filter.currentText()
        search_text = (
            self.device_search.text().lower().strip() if hasattr(self, "device_search") else ""
        )

        for device in self.device_catalog:
            # Apply dropdown filters
            if selected_type != "All Types" and device.get("type") != selected_type:
                continue
            if selected_mfr != "All Manufacturers" and device.get("manufacturer") != selected_mfr:
                continue

            # Apply search filter (search across name, model, symbol)
            if search_text:
                searchable_text = " ".join(
                    [
                        device.get("name", "").lower(),
                        device.get("model", "").lower(),
                        device.get("symbol", "").lower(),
                        device.get("manufacturer", "").lower(),
                    ]
                )
                if search_text not in searchable_text:
                    continue

            # Create list item
            display_text = f"{device['name']} ({device['symbol']}) - {device['manufacturer']} {device['model']}"
            item = QtWidgets.QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.device_catalog_list.addItem(item)

    def _filter_devices(self):
        """Handle device filtering when dropdowns change."""
        self._populate_device_list()

    def _add_device_from_catalog(self):
        """Add selected device from catalog to staging."""
        current_item = self.device_catalog_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "No Selection", "Please select a device from the catalog first."
            )
            return

        device_data = current_item.data(Qt.ItemDataRole.UserRole)

        # Create staged device (quantity will be determined by canvas placement)
        staged_device = StagedDevice(
            uid=f"{device_data['type']}_{len(self.staged_devices) + 1}",
            device_type=device_data["type"],
            model=device_data["model"],
            manufacturer=device_data["manufacturer"],
            symbol=device_data["symbol"],
            quantity_planned=1,  # Default to 1, real quantity comes from canvas placement
        )

        self.staged_devices.append(staged_device)
        self._refresh_devices_table()
        self.staging_changed.emit()

        # Show success message
        self.status_label.setText(
            f"✅ Added {device_data['name']} to staging (quantity determined by canvas placement)"
        )
        self.status_label.setStyleSheet("color: #28a745; font-style: normal; font-weight: bold;")

    def _refresh_devices_table(self):
        """Refresh the staged devices table."""
        self.devices_table.setRowCount(len(self.staged_devices))

        for row, device in enumerate(self.staged_devices):
            self.devices_table.setItem(row, 0, QTableWidgetItem(device.device_type))
            self.devices_table.setItem(row, 1, QTableWidgetItem(device.manufacturer))
            self.devices_table.setItem(row, 2, QTableWidgetItem(device.model))
            self.devices_table.setItem(row, 3, QTableWidgetItem(device.symbol))
            self.devices_table.setItem(row, 4, QTableWidgetItem(str(device.quantity_planned)))
            self.devices_table.setItem(row, 5, QTableWidgetItem(str(device.quantity_placed)))

            # Actions column
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet(
                "background-color: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 3px;"
            )
            remove_btn.clicked.connect(lambda checked, r=row: self._remove_staged_device(r))
            self.devices_table.setCellWidget(row, 6, remove_btn)

    def _remove_staged_device(self, row):
        """Remove a staged device."""
        if 0 <= row < len(self.staged_devices):
            removed_device = self.staged_devices.pop(row)
            self._refresh_devices_table()
            self.staging_changed.emit()
            self.status_label.setText(f"🗑️ Removed {removed_device.device_type} from staging")
            self.status_label.setStyleSheet("color: #ffc107; font-style: normal;")

    def _setup_wires_tab(self):
        """Setup the Wire tab with intelligent wire selection for fire alarm circuits."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Intelligent wire recommendation section
        recommend_group = QGroupBox("🔧 Intelligent Wire Recommendations")
        recommend_layout = QVBoxLayout(recommend_group)

        # Circuit type selector
        circuit_layout = QHBoxLayout()
        circuit_layout.addWidget(QLabel("Circuit Type:"))

        self.circuit_type_selector = QComboBox()
        self.circuit_type_selector.addItems(
            [
                "SLC (Signaling Line Circuit) - 18-22 AWG",
                "NAC (Notification Appliance Circuit) - 14-16 AWG",
                "Power Supply - 12-14 AWG",
                "IDC (Initiating Device Circuit) - 18 AWG",
                "Telephone/Data - 22-24 AWG",
            ]
        )
        self.circuit_type_selector.currentTextChanged.connect(self._recommend_wire)
        circuit_layout.addWidget(self.circuit_type_selector)

        circuit_layout.addStretch()
        recommend_layout.addLayout(circuit_layout)

        # Recommendation display
        self.wire_recommendation = QLabel("Select a circuit type for wire recommendations")
        self.wire_recommendation.setStyleSheet(
            """
            QLabel {
                background-color: #f8f9fa;
                border: 2px solid #007bff;
                border-radius: 6px;
                padding: 12px;
                margin: 8px 0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                font-weight: 500;
                color: #212529;
                line-height: 1.4;
            }
        """
        )
        recommend_layout.addWidget(self.wire_recommendation)

        # Quick add recommended wire button
        self.quick_add_wire_btn = QPushButton("📦 Add Recommended Wire to Spool")
        self.quick_add_wire_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """
        )
        self.quick_add_wire_btn.clicked.connect(self._add_recommended_wire)
        recommend_layout.addWidget(self.quick_add_wire_btn)

        layout.addWidget(recommend_group)

        # Manual wire entry form
        form_group = QGroupBox("Manual Wire Entry")
        form_layout = QFormLayout(form_group)

        self.wire_sku = QLineEdit()
        self.wire_sku.setPlaceholderText("e.g., THHN-14-2C-RED")
        form_layout.addRow("SKU:", self.wire_sku)

        self.wire_description = QLineEdit()
        self.wire_description.setPlaceholderText("e.g., 14 AWG 2-Conductor Red THHN")
        form_layout.addRow("Description:", self.wire_description)

        self.wire_gauge = QComboBox()
        self.wire_gauge.addItems(["24", "22", "20", "18", "16", "14", "12", "10"])
        self.wire_gauge.setCurrentText("14")
        form_layout.addRow("Gauge (AWG):", self.wire_gauge)

        self.wire_conductors = QSpinBox()
        self.wire_conductors.setRange(2, 8)
        self.wire_conductors.setValue(2)
        form_layout.addRow("Conductors:", self.wire_conductors)

        self.wire_resistance = QtWidgets.QDoubleSpinBox()
        self.wire_resistance.setRange(0.1, 100.0)
        self.wire_resistance.setValue(2.5)
        self.wire_resistance.setDecimals(2)
        self.wire_resistance.setSuffix(" Ω/1000ft")
        form_layout.addRow("Resistance:", self.wire_resistance)

        self.wire_capacitance = QtWidgets.QDoubleSpinBox()
        self.wire_capacitance.setRange(10.0, 200.0)
        self.wire_capacitance.setValue(58.0)
        self.wire_capacitance.setDecimals(1)
        self.wire_capacitance.setSuffix(" pF/1000ft")
        form_layout.addRow("Capacitance:", self.wire_capacitance)

        self.wire_reel = QSpinBox()
        self.wire_reel.setRange(100, 10000)
        self.wire_reel.setValue(1000)
        self.wire_reel.setSuffix(" ft")
        form_layout.addRow("Reel Length:", self.wire_reel)

        add_wire_btn = QPushButton("Add Custom Wire Type")
        add_wire_btn.clicked.connect(self._add_custom_wire)
        form_layout.addWidget(add_wire_btn)

        layout.addWidget(form_group)

        # Staged wires table
        self.wires_table = QTableWidget()
        self.wires_table.setColumnCount(7)
        self.wires_table.setHorizontalHeaderLabels(
            [
                "SKU",
                "Description",
                "Gauge",
                "Conductors",
                "Resistance (Ω/1000ft)",
                "Reel (ft)",
                "Actions",
            ]
        )
        self.wires_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.wires_table)

        self.tab_widget.addTab(widget, "Wire Spool")

        # Initialize with default recommendation
        self._recommend_wire()

    def _recommend_wire(self):
        """Provide intelligent wire recommendations based on circuit type."""
        circuit_type = self.circuit_type_selector.currentText()

        recommendations = {
            "SLC (Signaling Line Circuit) - 18-22 AWG": {
                "description": "🔍 SLC Circuit: 18 AWG 2-conductor shielded cable for reliable data communication",
                "sku": "SLC-18-2C-SHIELD",
                "gauge": "18",
                "conductors": 2,
                "resistance": 6.4,
                "capacitance": 42.0,
                "reel": 1000,
                "details": "Recommended for smoke detectors, heat detectors, and other addressable devices",
            },
            "NAC (Notification Appliance Circuit) - 14-16 AWG": {
                "description": "🔊 NAC Circuit: 14 AWG 2-conductor for notification appliances (horns, strobes)",
                "sku": "NAC-14-2C-RED",
                "gauge": "14",
                "conductors": 2,
                "resistance": 2.5,
                "capacitance": 58.0,
                "reel": 1000,
                "details": "Higher current capacity for horns, strobes, and speakers",
            },
            "Power Supply - 12-14 AWG": {
                "description": "⚡ Power: 12 AWG 2-conductor for main power distribution",
                "sku": "PWR-12-2C-BLACK",
                "gauge": "12",
                "conductors": 2,
                "resistance": 1.6,
                "capacitance": 65.0,
                "reel": 500,
                "details": "High current capacity for power panels and main distribution",
            },
            "IDC (Initiating Device Circuit) - 18 AWG": {
                "description": "🚨 IDC Circuit: 18 AWG 2-conductor for conventional pull stations",
                "sku": "IDC-18-2C-BLUE",
                "gauge": "18",
                "conductors": 2,
                "resistance": 6.4,
                "capacitance": 42.0,
                "reel": 1000,
                "details": "For conventional fire alarm initiating devices",
            },
            "Telephone/Data - 22-24 AWG": {
                "description": "📞 Comm: 22 AWG 4-conductor for telephone and data circuits",
                "sku": "TEL-22-4C-GRAY",
                "gauge": "22",
                "conductors": 4,
                "resistance": 16.2,
                "capacitance": 38.0,
                "reel": 1000,
                "details": "For telephone circuits and low-power data communication",
            },
        }

        if circuit_type in recommendations:
            rec = recommendations[circuit_type]
            self.wire_recommendation.setText(f"{rec['description']}\n\n{rec['details']}")
            self.current_recommendation = rec
        else:
            self.wire_recommendation.setText("Select a circuit type for wire recommendations")
            self.current_recommendation = None

    def _add_recommended_wire(self):
        """Add the currently recommended wire to the spool."""
        if not hasattr(self, "current_recommendation") or not self.current_recommendation:
            return

        rec = self.current_recommendation

        wire = StagedWire(
            sku=rec["sku"],
            description=rec["description"].split("\n")[0],  # First line only
            gauge=int(rec["gauge"]),
            conductor_count=rec["conductors"],
            resistance_per_1000ft=rec["resistance"],
            capacitance_per_1000ft=rec["capacitance"],
            reel_length=rec["reel"],
        )

        self.staged_wires.append(wire)
        self._refresh_wires_table()
        self.staging_changed.emit()

        # Show success message
        self.status_label.setText(f"📦 Added recommended {rec['gauge']} AWG wire to spool")
        self.status_label.setStyleSheet("color: #28a745; font-style: normal; font-weight: bold;")

    def _add_custom_wire(self):
        """Add a custom wire type to staging."""
        if not self.wire_sku.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter a wire SKU.")
            return

        wire = StagedWire(
            sku=self.wire_sku.text(),
            description=self.wire_description.text()
            or f"{self.wire_gauge.currentText()} AWG {self.wire_conductors.value()}-Conductor",
            gauge=int(self.wire_gauge.currentText()),
            conductor_count=self.wire_conductors.value(),
            resistance_per_1000ft=self.wire_resistance.value(),
            capacitance_per_1000ft=self.wire_capacitance.value(),
            reel_length=self.wire_reel.value(),
        )

        self.staged_wires.append(wire)
        self._refresh_wires_table()
        self.staging_changed.emit()

        # Clear form
        self.wire_sku.clear()
        self.wire_description.clear()

        # Show success message
        self.status_label.setText(f"📦 Added custom wire {wire.sku} to spool")
        self.status_label.setStyleSheet("color: #28a745; font-style: normal; font-weight: bold;")

    def _refresh_wires_table(self):
        """Refresh the staged wires table."""
        self.wires_table.setRowCount(len(self.staged_wires))

        for row, wire in enumerate(self.staged_wires):
            self.wires_table.setItem(row, 0, QTableWidgetItem(wire.sku))
            self.wires_table.setItem(row, 1, QTableWidgetItem(wire.description))
            self.wires_table.setItem(row, 2, QTableWidgetItem(str(wire.gauge)))
            self.wires_table.setItem(row, 3, QTableWidgetItem(str(wire.conductor_count)))
            self.wires_table.setItem(row, 4, QTableWidgetItem(f"{wire.resistance_per_1000ft:.2f}"))
            self.wires_table.setItem(row, 5, QTableWidgetItem(f"{wire.reel_length}"))

            # Actions column
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet(
                "background-color: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 3px;"
            )
            remove_btn.clicked.connect(lambda checked, r=row: self._remove_staged_wire(r))
            self.wires_table.setCellWidget(row, 6, remove_btn)

    def _remove_staged_wire(self, row):
        """Remove a staged wire."""
        if 0 <= row < len(self.staged_wires):
            removed_wire = self.staged_wires.pop(row)
            self._refresh_wires_table()
            self.staging_changed.emit()
            self.status_label.setText(f"🗑️ Removed wire {removed_wire.sku} from spool")
            self.status_label.setStyleSheet("color: #ffc107; font-style: normal;")

    def _setup_policies_tab(self):
        """Setup the Policies tab for addressing schemes, routing preferences."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Addressing policies
        addr_group = QGroupBox("Addressing Policies")
        addr_layout = QFormLayout(addr_group)

        self.addr_scheme = QComboBox()
        self.addr_scheme.addItems(["Sequential", "Zone-Based", "Custom"])
        addr_layout.addRow("Scheme:", self.addr_scheme)

        self.addr_start = QSpinBox()
        self.addr_start.setRange(1, 999)
        self.addr_start.setValue(1)
        addr_layout.addRow("Start Address:", self.addr_start)

        layout.addWidget(addr_group)

        # Routing policies
        route_group = QGroupBox("Routing Policies")
        route_layout = QFormLayout(route_group)

        self.route_preference = QComboBox()
        self.route_preference.addItems(["Manual", "Follow Path", "Auto Route"])
        route_layout.addRow("Default Mode:", self.route_preference)

        self.auto_sizing = QtWidgets.QCheckBox("Auto-size wire gauge")
        self.auto_sizing.setChecked(True)
        route_layout.addWidget(self.auto_sizing)

        self.wire_derating = QtWidgets.QDoubleSpinBox()
        self.wire_derating.setRange(1.0, 2.0)
        self.wire_derating.setValue(1.25)
        self.wire_derating.setDecimals(2)
        self.wire_derating.setSuffix("x")
        route_layout.addRow("Derating Factor:", self.wire_derating)

        layout.addWidget(route_group)

        layout.addStretch()

        self.tab_widget.addTab(widget, "Policies")

    def _load_defaults(self):
        """Load default staging items and refresh tables."""
        # Load initial data but don't populate with defaults
        # The user will use the System Builder to stage what they need

        self._refresh_tables()

    def _refresh_tables(self):
        """Refresh all staging tables."""
        self._refresh_panels_table()
        self._refresh_devices_table()
        self._refresh_wires_table()

    def _refresh_panels_table(self):
        """Refresh the staged panels table."""
        self.panels_table.setRowCount(len(self.staged_panels))

        for row, panel in enumerate(self.staged_panels):
            self.panels_table.setItem(row, 0, QTableWidgetItem(panel.uid))
            self.panels_table.setItem(row, 1, QTableWidgetItem(panel.manufacturer))
            self.panels_table.setItem(row, 2, QTableWidgetItem(panel.model))
            self.panels_table.setItem(row, 3, QTableWidgetItem(str(panel.slots)))
            self.panels_table.setItem(row, 4, QTableWidgetItem(f"{panel.psu_capacity:.1f}"))
            self.panels_table.setItem(row, 5, QTableWidgetItem(f"{panel.battery_ah:.1f}"))

            # Actions column
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet(
                "background-color: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 3px;"
            )
            remove_btn.clicked.connect(lambda checked, r=row: self._remove_staged_panel(r))
            self.panels_table.setCellWidget(row, 6, remove_btn)

    def _remove_staged_panel(self, row):
        """Remove a staged panel."""
        if 0 <= row < len(self.staged_panels):
            removed_panel = self.staged_panels.pop(row)
            self._refresh_panels_table()
            self.staging_changed.emit()
            self.status_label.setText(f"🗑️ Removed panel {removed_panel.uid} from staging")
            self.status_label.setStyleSheet("color: #ffc107; font-style: normal;")

    def _add_panel(self):
        """Add a panel to staging."""
        if not self.panel_uid.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter a Panel UID.")
            return

        panel = StagedPanel(
            uid=self.panel_uid.text(),
            model=self.panel_model.text() or "Unknown Model",
            manufacturer=self.panel_manufacturer.currentText(),
            slots=self.panel_slots.value(),
            psu_capacity=float(self.panel_psu.value()),
            battery_ah=float(self.panel_battery.value()),
            outputs=4,  # Default
        )

        self.staged_panels.append(panel)
        self._refresh_panels_table()
        self.staging_changed.emit()

        # Clear form
        self.panel_uid.clear()
        self.panel_model.clear()

        # Show success message
        self.status_label.setText(f"✅ Added panel {panel.uid} to staging")
        self.status_label.setStyleSheet("color: #28a745; font-style: normal; font-weight: bold;")

    def _assemble_system(self):
        """Assemble the staged system into a working fire alarm system."""
        if not self.staged_panels:
            QMessageBox.warning(
                self, "No Panels", "Please add at least one fire alarm panel before assembling."
            )
            return

        if not self.staged_devices:
            QMessageBox.warning(
                self, "No Devices", "Please add at least one device type before assembling."
            )
            return

        # Create assembled system data
        assembled_data = {
            "panels": [asdict(panel) for panel in self.staged_panels],
            "devices": [asdict(device) for device in self.staged_devices],
            "wires": [asdict(wire) for wire in self.staged_wires],
            "policies": asdict(self.policies),
        }

        # Emit assembled signal
        self.assembled.emit(assembled_data)

        # Update status
        total_devices = sum(device.quantity_planned for device in self.staged_devices)
        self.status_label.setText(
            f"🎉 System Assembled! {len(self.staged_panels)} panels, "
            f"{total_devices} devices, {len(self.staged_wires)} wire types"
        )
        self.status_label.setStyleSheet("color: #28a745; font-style: normal; font-weight: bold;")

        # Show assembly summary
        summary_msg = f"""
        System Assembly Complete!

        Panels: {len(self.staged_panels)}
        Device Types: {len(self.staged_devices)}
        Total Devices: {total_devices}
        Wire Types: {len(self.staged_wires)}

        The system is now ready for device placement and circuit design.
        """

        QMessageBox.information(self, "System Assembled", summary_msg)
        self.staging_changed.emit()

        # Clear form
        self.panel_uid.clear()
        self.panel_model.clear()

    def _add_wire(self):
        """Add a new wire type to staging."""
        sku = self.wire_sku.text() or f"WIRE-{self.wire_gauge.currentText()}AWG"

        wire = StagedWire(
            sku=sku,
            description=f"{self.wire_gauge.currentText()} AWG {self.wire_conductors.value()}C",
            gauge=int(self.wire_gauge.currentText()),
            conductor_count=self.wire_conductors.value(),
            resistance_per_1000ft=self.wire_resistance.value(),
            capacitance_per_1000ft=25.0,  # Default
            reel_length=self.wire_reel.value(),
            remaining_length=self.wire_reel.value(),
        )
        self.staged_wires.append(wire)
        self._refresh_tables()
        self.staging_changed.emit()

        # Clear form
        self.wire_sku.clear()

    def get_assembly_data(self) -> dict:
        """Get the current assembly data."""
        return {
            "panels": [asdict(panel) for panel in self.staged_panels],
            "devices": [asdict(device) for device in self.staged_devices],
            "wires": [asdict(wire) for wire in self.staged_wires],
            "policies": asdict(self.policies),
        }

    def load_assembly_data(self, data: dict):
        """Load assembly data from project file."""
        try:
            # Load panels
            self.staged_panels = [StagedPanel(**panel) for panel in data.get("panels", [])]

            # Load devices
            self.staged_devices = [StagedDevice(**device) for device in data.get("devices", [])]

            # Load wires
            self.staged_wires = [StagedWire(**wire) for wire in data.get("wires", [])]

            # Load policies
            if "policies" in data:
                self.policies = StagingPolicies(**data["policies"])

            self._refresh_tables()

        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Failed to load assembly data: {e}")
