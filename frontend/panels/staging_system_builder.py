"""
System Builder - Staging Warehouse for AutoFire
Implements the specification's "System Builder (Staging Warehouse)" workflow
"""

from dataclasses import asdict, dataclass

from PySide6 import QtCore, QtWidgets
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

from backend.catalog import load_catalog


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
    reserved_ranges: list[tuple] = None
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

        # Add device form
        form_group = QGroupBox("Add Device Type")
        form_layout = QFormLayout(form_group)

        self.device_type = QComboBox()
        self.device_type.addItems(
            [
                "Smoke Detector",
                "Heat Detector",
                "Pull Station",
                "Notification Appliance",
                "Monitor Module",
                "Control Module",
                "Input Module",
                "Output Module",
                "Annunciator",
            ]
        )
        form_layout.addRow("Type:", self.device_type)

        self.device_manufacturer = QComboBox()
        self.device_manufacturer.addItems(
            [
                "System Sensor",
                "EST",
                "Fire-Lite",
                "Notifier",
                "Honeywell",
                "Edwards",
                "Siemens",
                "Other",
            ]
        )
        form_layout.addRow("Manufacturer:", self.device_manufacturer)

        self.device_model = QLineEdit()
        self.device_model.setPlaceholderText("e.g., 2WT-B")
        form_layout.addRow("Model:", self.device_model)

        self.device_quantity = QSpinBox()
        self.device_quantity.setRange(1, 9999)
        self.device_quantity.setValue(10)
        form_layout.addRow("Quantity:", self.device_quantity)

        add_device_btn = QPushButton("Add Device Type")
        add_device_btn.clicked.connect(self._add_device)
        form_layout.addWidget(add_device_btn)

        layout.addWidget(form_group)

        # Staged devices table
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(6)
        self.devices_table.setHorizontalHeaderLabels(
            ["Type", "Manufacturer", "Model", "Planned", "Placed", "Connected"]
        )
        self.devices_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.devices_table)

        self.tab_widget.addTab(widget, "Devices")

    def _setup_wires_tab(self):
        """Setup the Wire tab for adding wire SKUs, resistance, capacitance, etc."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Add wire form
        form_group = QGroupBox("Add Wire Type")
        form_layout = QFormLayout(form_group)

        self.wire_sku = QLineEdit()
        self.wire_sku.setPlaceholderText("e.g., THHN-14-2C-RED")
        form_layout.addRow("SKU:", self.wire_sku)

        self.wire_gauge = QComboBox()
        self.wire_gauge.addItems(["22", "20", "18", "16", "14", "12", "10"])
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

        self.wire_reel = QSpinBox()
        self.wire_reel.setRange(100, 10000)
        self.wire_reel.setValue(1000)
        self.wire_reel.setSuffix(" ft")
        form_layout.addRow("Reel Length:", self.wire_reel)

        add_wire_btn = QPushButton("Add Wire Type")
        add_wire_btn.clicked.connect(self._add_wire)
        form_layout.addWidget(add_wire_btn)

        layout.addWidget(form_group)

        # Staged wires table
        self.wires_table = QTableWidget()
        self.wires_table.setColumnCount(6)
        self.wires_table.setHorizontalHeaderLabels(
            ["SKU", "Gauge", "Conductors", "Resistance (Ω/1000ft)", "Reel (ft)", "Remaining"]
        )
        self.wires_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.wires_table)

        self.tab_widget.addTab(widget, "Wire")

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
        """Load default staging items from database."""
        # Add default panel (still hardcoded for now - panels will come from database later)
        default_panel = StagedPanel(
            uid="FACP-1",
            model="MS-9600LS",
            manufacturer="Fire-Lite",
            slots=8,
            psu_capacity=3.0,
            battery_ah=18.0,
            outputs=4,
        )
        self.staged_panels.append(default_panel)

        # Load devices from database
        try:
            db_devices = load_catalog()
            for device in db_devices:
                staged_device = StagedDevice(
                    symbol=device.get("symbol", "DEV"),
                    name=device.get("name", "Unknown Device"),
                    model=device.get("model", "Unknown"),
                    manufacturer=device.get("manufacturer", "Unknown"),
                    device_type=device.get("type", "Device"),
                    voltage=24.0,  # Default voltage
                    current_sleep=0.05,  # Default sleep current
                    current_alarm=0.1,  # Default alarm current
                    quantity=1,  # Default quantity
                )
                self.staged_devices.append(staged_device)
        except Exception as e:
            print(f"Warning: Could not load devices from database: {e}")
            # Fallback to hardcoded devices if database fails
            default_devices = [
                StagedDevice(
                    "SD",
                    "Smoke Detector",
                    "2WT-B",
                    "System Sensor",
                    "Detector",
                    24.0,
                    0.05,
                    0.1,
                    20,
                ),
                StagedDevice(
                    "HD", "Heat Detector", "5601P", "System Sensor", "Detector", 24.0, 0.05, 0.1, 5
                ),
                StagedDevice(
                    "PS", "Pull Station", "270A", "Fire-Lite", "Initiating", 24.0, 0.0, 0.0, 8
                ),
                StagedDevice(
                    "HS", "Horn/Strobe", "HSR", "System Sensor", "Notification", 24.0, 0.02, 0.1, 15
                ),
            ]
            self.staged_devices.extend(default_devices)

        # Load wires from database
        try:
            from db import loader as db_loader

            con = db_loader.connect()
            db_wires = db_loader.fetch_wires(con)
            con.close()

            for wire in db_wires:
                staged_wire = StagedWire(
                    sku=wire.get("part_number", "UNKNOWN"),
                    name=wire.get("name", "Unknown Wire"),
                    gauge=wire.get("gauge", 14),
                    conductors=2,  # Default to 2 conductors
                    ohms_per_1000ft=wire.get("ohms_per_1000ft", 2.5),
                    ampacity=wire.get("max_current_a", 15.0),
                    reel_length=1000,  # Default reel length
                    cost_per_ft=0.12,  # Default cost
                )
                self.staged_wires.append(staged_wire)
        except Exception as e:
            print(f"Warning: Could not load wires from database: {e}")
            # Fallback to hardcoded wires if database fails
            default_wires = [
                StagedWire("THHN-14-2C-RED", "14 AWG 2C THHN Red", 14, 2, 2.5, 25.0, 1000, 0.12),
                StagedWire("THHN-12-2C-RED", "12 AWG 2C THHN Red", 12, 2, 1.6, 25.0, 1000, 0.18),
                StagedWire("FPLR-16-2C", "16 AWG 2C FPLR", 16, 2, 4.0, 30.0, 1000, 0.08),
            ]
            self.staged_wires.extend(default_wires)

        self._refresh_tables()

    def _add_panel(self):
        """Add a new panel to staging."""
        panel = StagedPanel(
            uid=self.panel_uid.text() or f"FACP-{len(self.staged_panels)+1}",
            model=self.panel_model.text(),
            manufacturer=self.panel_manufacturer.currentText(),
            slots=self.panel_slots.value(),
            psu_capacity=float(self.panel_psu.value()),
            battery_ah=float(self.panel_battery.value()),
            outputs=4,  # Default
        )
        self.staged_panels.append(panel)
        self._refresh_tables()
        self.staging_changed.emit()

        # Clear form
        self.panel_uid.clear()
        self.panel_model.clear()

    def _add_device(self):
        """Add a new device type to staging."""
        device_type = self.device_type.currentText()
        symbol_map = {
            "Smoke Detector": "SD",
            "Heat Detector": "HD",
            "Pull Station": "PS",
            "Notification Appliance": "NA",
            "Monitor Module": "MM",
            "Control Module": "CM",
            "Input Module": "IM",
            "Output Module": "OM",
            "Annunciator": "AN",
        }

        device = StagedDevice(
            uid=symbol_map.get(device_type, "DV"),
            device_type=device_type,
            model=self.device_model.text(),
            manufacturer=self.device_manufacturer.currentText(),
            symbol=symbol_map.get(device_type, "DV"),
            quantity_planned=self.device_quantity.value(),
        )
        self.staged_devices.append(device)
        self._refresh_tables()
        self.staging_changed.emit()

        # Clear form
        self.device_model.clear()

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

    def _refresh_tables(self):
        """Refresh all staging tables."""
        # Refresh panels table
        self.panels_table.setRowCount(len(self.staged_panels))
        for i, panel in enumerate(self.staged_panels):
            self.panels_table.setItem(i, 0, QTableWidgetItem(panel.uid))
            self.panels_table.setItem(i, 1, QTableWidgetItem(panel.manufacturer))
            self.panels_table.setItem(i, 2, QTableWidgetItem(panel.model))
            self.panels_table.setItem(i, 3, QTableWidgetItem(str(panel.slots)))
            self.panels_table.setItem(i, 4, QTableWidgetItem(f"{panel.psu_capacity:.1f}"))
            self.panels_table.setItem(i, 5, QTableWidgetItem(f"{panel.battery_ah:.1f}"))

            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda checked, idx=i: self._remove_panel(idx))
            self.panels_table.setCellWidget(i, 6, remove_btn)

        # Refresh devices table
        self.devices_table.setRowCount(len(self.staged_devices))
        for i, device in enumerate(self.staged_devices):
            self.devices_table.setItem(i, 0, QTableWidgetItem(device.device_type))
            self.devices_table.setItem(i, 1, QTableWidgetItem(device.manufacturer))
            self.devices_table.setItem(i, 2, QTableWidgetItem(device.model))
            self.devices_table.setItem(i, 3, QTableWidgetItem(str(device.quantity_planned)))
            self.devices_table.setItem(i, 4, QTableWidgetItem(str(device.quantity_placed)))
            self.devices_table.setItem(i, 5, QTableWidgetItem(str(device.quantity_connected)))

        # Refresh wires table
        self.wires_table.setRowCount(len(self.staged_wires))
        for i, wire in enumerate(self.staged_wires):
            self.wires_table.setItem(i, 0, QTableWidgetItem(wire.sku))
            self.wires_table.setItem(i, 1, QTableWidgetItem(str(wire.gauge)))
            self.wires_table.setItem(i, 2, QTableWidgetItem(str(wire.conductor_count)))
            self.wires_table.setItem(i, 3, QTableWidgetItem(f"{wire.resistance_per_1000ft:.2f}"))
            self.wires_table.setItem(i, 4, QTableWidgetItem(str(wire.reel_length)))
            self.wires_table.setItem(i, 5, QTableWidgetItem(str(wire.remaining_length)))

    def _remove_panel(self, index: int):
        """Remove a panel from staging."""
        if 0 <= index < len(self.staged_panels):
            del self.staged_panels[index]
            self._refresh_tables()
            self.staging_changed.emit()

    def _assemble_system(self):
        """Assemble the staged system - populates Device Palette and Wire Spool."""
        if not self.staged_panels:
            QMessageBox.warning(
                self, "Assembly Error", "Please add at least one panel before assembling."
            )
            return

        if not self.staged_devices:
            QMessageBox.warning(
                self, "Assembly Error", "Please add at least one device type before assembling."
            )
            return

        # Update policies
        self.policies.addressing_scheme = self.addr_scheme.currentText().lower().replace("-", "_")
        self.policies.routing_preference = (
            self.route_preference.currentText().lower().replace(" ", "_")
        )
        self.policies.auto_sizing = self.auto_sizing.isChecked()
        self.policies.wire_derating = self.wire_derating.value()

        # Create assembly data
        assembly_data = {
            "panels": [asdict(panel) for panel in self.staged_panels],
            "devices": [asdict(device) for device in self.staged_devices],
            "wires": [asdict(wire) for wire in self.staged_wires],
            "policies": asdict(self.policies),
            "timestamp": QtCore.QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate),
        }

        # Update status
        device_count = sum(d.quantity_planned for d in self.staged_devices)
        wire_count = len(self.staged_wires)
        self.status_label.setText(
            f"✅ System assembled: {len(self.staged_panels)} panels, "
            f"{device_count} devices, {wire_count} wire types"
        )
        self.status_label.setStyleSheet("color: #238636; font-weight: bold;")

        # Emit assembled signal
        self.assembled.emit(assembly_data)

        QMessageBox.information(
            self,
            "System Assembled",
            f"System successfully assembled!\n\n"
            f"• {len(self.staged_panels)} panels staged\n"
            f"• {device_count} devices planned\n"
            f"• {wire_count} wire types available\n\n"
            f"Device Palette and Wire Spool have been populated.",
        )

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
