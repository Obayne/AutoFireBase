"""
System Builder - Configure fire alarm systems
"""

import json
import math
from typing import Any

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt

# Import coverage and calculation services


class SystemConfiguration:
    """Represents a fire alarm system configuration."""

    def __init__(self, name: str = ""):
        self.name = (
            name or f"System {QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd_hh-mm-ss')}"
        )
        self.facp_type = "Conventional"
        self.zones: list[dict[str, Any]] = []
        self.devices: dict[str, list[dict[str, Any]]] = {
            "smoke_detectors": [],
            "heat_detectors": [],
            "pull_stations": [],
            "horn_strobes": [],
            "speakers": [],
            "other": [],
        }
        self.power_requirements = {
            "primary_voltage": 120,
            "secondary_voltage": 24,
            "battery_backup_hours": 24,
            "calculated_load": 0.0,
        }
        self.coverage_areas: list[dict[str, Any]] = []
        self.created_date = QtCore.QDateTime.currentDateTime().toString()
        self.modified_date = self.created_date

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "facp_type": self.facp_type,
            "zones": self.zones,
            "devices": self.devices,
            "power_requirements": self.power_requirements,
            "coverage_areas": self.coverage_areas,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SystemConfiguration":
        """Create from dictionary."""
        system = cls(data.get("name", ""))
        system.facp_type = data.get("facp_type", "Conventional")
        system.zones = data.get("zones", [])
        system.devices = data.get("devices", system.devices)
        system.power_requirements = data.get("power_requirements", system.power_requirements)
        system.coverage_areas = data.get("coverage_areas", [])
        system.created_date = data.get("created_date", system.created_date)
        system.modified_date = data.get(
            "modified_date", QtCore.QDateTime.currentDateTime().toString()
        )
        return system

    def calculate_power_load(self) -> float:
        """Calculate total power load in amps."""
        total_amps = 0.0

        # Device power requirements (example values - should be configurable)
        device_loads = {
            "smoke_detectors": 0.02,  # amps per device
            "heat_detectors": 0.02,
            "pull_stations": 0.01,
            "horn_strobes": 0.15,
            "speakers": 0.20,
            "other": 0.05,
        }

        for device_type, devices in self.devices.items():
            load_per_device = device_loads.get(device_type, 0.05)
            total_amps += len(devices) * load_per_device

        # FACP base load
        facp_loads = {"Conventional": 0.5, "Addressable": 1.0, "Hybrid": 0.8}
        total_amps += facp_loads.get(self.facp_type, 0.5)

        self.power_requirements["calculated_load"] = total_amps
        return total_amps


class SystemBuilderDialog(QtWidgets.QDialog):
    """System Builder Configuration Dialog."""

    def __init__(self, parent=None, existing_system: SystemConfiguration | None = None):
        super().__init__(parent)
        self.setWindowTitle("System Builder")
        self.setModal(False)
        self.resize(1000, 700)

        self.system = existing_system or SystemConfiguration()
        self._setup_ui()
        self._load_system_data()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()

        self.btn_new_system = QtWidgets.QPushButton("New System")
        self.btn_new_system.clicked.connect(self._new_system)
        toolbar.addWidget(self.btn_new_system)

        self.btn_load_system = QtWidgets.QPushButton("Load System")
        self.btn_load_system.clicked.connect(self._load_system)
        toolbar.addWidget(self.btn_load_system)

        self.btn_save_system = QtWidgets.QPushButton("Save System")
        self.btn_save_system.clicked.connect(self._save_system)
        toolbar.addWidget(self.btn_save_system)

        self.btn_generate_report = QtWidgets.QPushButton("Generate Report")
        self.btn_generate_report.clicked.connect(self._generate_report)
        toolbar.addWidget(self.btn_generate_report)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Main content
        content = QtWidgets.QSplitter(Qt.Horizontal)

        # Left panel - System overview
        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_panel)

        # System info
        info_group = QtWidgets.QGroupBox("System Information")
        info_layout = QtWidgets.QFormLayout(info_group)

        self.system_name_edit = QtWidgets.QLineEdit()
        self.facp_type_combo = QtWidgets.QComboBox()
        self.facp_type_combo.addItems(["Conventional", "Addressable", "Hybrid"])
        self.facp_type_combo.currentTextChanged.connect(self._on_facp_type_changed)

        info_layout.addRow("System Name:", self.system_name_edit)
        info_layout.addRow("FACP Type:", self.facp_type_combo)

        left_layout.addWidget(info_group)

        # Device summary
        summary_group = QtWidgets.QGroupBox("Device Summary")
        summary_layout = QtWidgets.QVBoxLayout(summary_group)

        self.device_summary_text = QtWidgets.QTextEdit()
        self.device_summary_text.setReadOnly(True)
        self.device_summary_text.setMaximumHeight(150)
        summary_layout.addWidget(self.device_summary_text)

        left_layout.addWidget(summary_group)

        # Power requirements
        power_group = QtWidgets.QGroupBox("Power Requirements")
        power_layout = QtWidgets.QFormLayout(power_group)

        self.primary_voltage_spin = QtWidgets.QSpinBox()
        self.primary_voltage_spin.setRange(100, 480)
        self.primary_voltage_spin.setValue(120)
        self.primary_voltage_spin.setSuffix(" V")

        self.secondary_voltage_spin = QtWidgets.QSpinBox()
        self.secondary_voltage_spin.setRange(12, 48)
        self.secondary_voltage_spin.setValue(24)
        self.secondary_voltage_spin.setSuffix(" V")

        self.battery_hours_spin = QtWidgets.QSpinBox()
        self.battery_hours_spin.setRange(4, 120)
        self.battery_hours_spin.setValue(24)
        self.battery_hours_spin.setSuffix(" hours")

        self.calculated_load_label = QtWidgets.QLabel("0.0 A")

        power_layout.addRow("Primary Voltage:", self.primary_voltage_spin)
        power_layout.addRow("Secondary Voltage:", self.secondary_voltage_spin)
        power_layout.addRow("Battery Backup:", self.battery_hours_spin)
        power_layout.addRow("Calculated Load:", self.calculated_load_label)

        self.btn_calculate_power = QtWidgets.QPushButton("Calculate Power")
        self.btn_calculate_power.clicked.connect(self._calculate_power)
        power_layout.addRow(self.btn_calculate_power)

        left_layout.addWidget(power_group)

        # Right panel - Device configuration
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)

        # Device type tabs
        self.device_tabs = QtWidgets.QTabWidget()

        device_types = [
            ("Smoke Detectors", "smoke_detectors"),
            ("Heat Detectors", "heat_detectors"),
            ("Pull Stations", "pull_stations"),
            ("Horn/Strobes", "horn_strobes"),
            ("Speakers", "speakers"),
            ("Other Devices", "other"),
        ]

        self.device_lists = {}
        for display_name, device_type in device_types:
            tab = QtWidgets.QWidget()
            tab_layout = QtWidgets.QVBoxLayout(tab)

            # Device list
            device_list = QtWidgets.QListWidget()
            self.device_lists[device_type] = device_list
            tab_layout.addWidget(device_list)

            # Controls
            controls_layout = QtWidgets.QHBoxLayout()

            btn_add = QtWidgets.QPushButton(f"Add {display_name[:-1]}")
            btn_add.clicked.connect(lambda checked, dt=device_type: self._add_device(dt))
            controls_layout.addWidget(btn_add)

            btn_remove = QtWidgets.QPushButton("Remove")
            btn_remove.clicked.connect(lambda checked, dt=device_type: self._remove_device(dt))
            controls_layout.addWidget(btn_remove)

            controls_layout.addStretch()
            tab_layout.addLayout(controls_layout)

            self.device_tabs.addTab(tab, display_name)

        # Coverage Analysis Tab
        coverage_tab = QtWidgets.QWidget()
        coverage_layout = QtWidgets.QVBoxLayout(coverage_tab)

        # Coverage settings
        coverage_settings_group = QtWidgets.QGroupBox("Coverage Settings")
        coverage_settings_layout = QtWidgets.QFormLayout(coverage_settings_group)

        self.room_length_spin = QtWidgets.QSpinBox()
        self.room_length_spin.setRange(5, 500)
        self.room_length_spin.setValue(30)
        self.room_length_spin.setSuffix(" ft")
        self.room_length_spin.valueChanged.connect(self._update_coverage_analysis)

        self.room_width_spin = QtWidgets.QSpinBox()
        self.room_width_spin.setRange(5, 500)
        self.room_width_spin.setValue(20)
        self.room_width_spin.setSuffix(" ft")
        self.room_width_spin.valueChanged.connect(self._update_coverage_analysis)

        self.ceiling_height_spin = QtWidgets.QSpinBox()
        self.ceiling_height_spin.setRange(8, 50)
        self.ceiling_height_spin.setValue(10)
        self.ceiling_height_spin.setSuffix(" ft")
        self.ceiling_height_spin.valueChanged.connect(self._update_coverage_analysis)

        coverage_settings_layout.addRow("Room Length:", self.room_length_spin)
        coverage_settings_layout.addRow("Room Width:", self.room_width_spin)
        coverage_settings_layout.addRow("Ceiling Height:", self.ceiling_height_spin)

        coverage_layout.addWidget(coverage_settings_group)

        # Coverage analysis results
        coverage_results_group = QtWidgets.QGroupBox("Coverage Analysis")
        coverage_results_layout = QtWidgets.QVBoxLayout(coverage_results_group)

        self.coverage_text = QtWidgets.QTextEdit()
        self.coverage_text.setReadOnly(True)
        self.coverage_text.setMinimumHeight(200)
        coverage_results_layout.addWidget(self.coverage_text)

        self.btn_analyze_coverage = QtWidgets.QPushButton("Analyze Coverage")
        self.btn_analyze_coverage.clicked.connect(self._analyze_coverage)
        coverage_results_layout.addWidget(self.btn_analyze_coverage)

        coverage_layout.addWidget(coverage_results_group)

        # NFPA Compliance
        compliance_group = QtWidgets.QGroupBox("NFPA Compliance Check")
        compliance_layout = QtWidgets.QVBoxLayout(compliance_group)

        self.compliance_text = QtWidgets.QTextEdit()
        self.compliance_text.setReadOnly(True)
        self.compliance_text.setMinimumHeight(150)
        compliance_layout.addWidget(self.compliance_text)

        self.btn_check_compliance = QtWidgets.QPushButton("Check NFPA Compliance")
        self.btn_check_compliance.clicked.connect(self._check_nfpa_compliance)
        compliance_layout.addWidget(self.btn_check_compliance)

        coverage_layout.addWidget(compliance_group)

        self.device_tabs.addTab(coverage_tab, "Coverage & NFPA")

        # Layout & Optimization Tab
        layout_tab = QtWidgets.QWidget()
        layout_layout = QtWidgets.QVBoxLayout(layout_tab)

        # Zone management
        zones_group = QtWidgets.QGroupBox("Zone Management")
        zones_layout = QtWidgets.QVBoxLayout(zones_group)

        # Zone list
        self.zones_list = QtWidgets.QListWidget()
        zones_layout.addWidget(self.zones_list)

        zone_controls = QtWidgets.QHBoxLayout()
        self.btn_add_zone = QtWidgets.QPushButton("Add Zone")
        self.btn_add_zone.clicked.connect(self._add_zone)
        zone_controls.addWidget(self.btn_add_zone)

        self.btn_remove_zone = QtWidgets.QPushButton("Remove Zone")
        self.btn_remove_zone.clicked.connect(self._remove_zone)
        zone_controls.addWidget(self.btn_remove_zone)

        zone_controls.addStretch()
        zones_layout.addLayout(zone_controls)

        layout_layout.addWidget(zones_group)

        # Automatic placement
        placement_group = QtWidgets.QGroupBox("Automatic Device Placement")
        placement_layout = QtWidgets.QVBoxLayout(placement_group)

        self.btn_auto_place = QtWidgets.QPushButton("Auto-Place Devices")
        self.btn_auto_place.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """
        )
        self.btn_auto_place.clicked.connect(self._auto_place_devices)
        placement_layout.addWidget(self.btn_auto_place)

        self.auto_place_status = QtWidgets.QLabel("Ready for automatic placement")
        placement_layout.addWidget(self.auto_place_status)

        layout_layout.addWidget(placement_group)

        # Optimization suggestions
        optimization_group = QtWidgets.QGroupBox("Optimization Suggestions")
        optimization_layout = QtWidgets.QVBoxLayout(optimization_group)

        self.optimization_text = QtWidgets.QTextEdit()
        self.optimization_text.setReadOnly(True)
        self.optimization_text.setMaximumHeight(150)
        optimization_layout.addWidget(self.optimization_text)

        self.btn_optimize = QtWidgets.QPushButton("Analyze & Optimize")
        self.btn_optimize.clicked.connect(self._analyze_optimization)
        optimization_layout.addWidget(self.btn_optimize)

        layout_layout.addWidget(optimization_group)

        self.device_tabs.addTab(layout_tab, "Layout & Optimization")

        right_layout.addWidget(self.device_tabs)

        content.addWidget(left_panel)
        content.addWidget(right_panel)
        content.setSizes([400, 600])

        layout.addWidget(content)

        # Status bar
        self.status_label = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status_label)

    def _load_system_data(self):
        """Load system data into UI."""
        self.system_name_edit.setText(self.system.name)
        self.facp_type_combo.setCurrentText(self.system.facp_type)

        # Load power requirements
        power = self.system.power_requirements
        self.primary_voltage_spin.setValue(power["primary_voltage"])
        self.secondary_voltage_spin.setValue(power["secondary_voltage"])
        self.battery_hours_spin.setValue(power["battery_backup_hours"])
        self.calculated_load_label.setText(f"{power['calculated_load']:.2f} A")

        # Load devices
        for device_type, devices in self.system.devices.items():
            device_list = self.device_lists.get(device_type)
            if device_list:
                device_list.clear()
                for device in devices:
                    item_text = (
                        f"{device.get('name', 'Unknown')} - {device.get('location', 'No location')}"
                    )
                    item = QtWidgets.QListWidgetItem(item_text)
                    item.setData(QtCore.Qt.UserRole, device)
                    device_list.addItem(item)

        self._update_device_summary()

    def _update_device_summary(self):
        """Update the device summary text."""
        summary = "Device Counts:\n"
        total_devices = 0

        for device_type, devices in self.system.devices.items():
            count = len(devices)
            total_devices += count
            display_name = device_type.replace("_", " ").title()
            summary += f"{display_name}: {count}\n"

        summary += f"\nTotal Devices: {total_devices}"
        self.device_summary_text.setPlainText(summary)

    def _on_facp_type_changed(self):
        """Handle FACP type change."""
        self.system.facp_type = self.facp_type_combo.currentText()
        self._calculate_power()

    def _add_device(self, device_type: str):
        """Add a device to the system."""
        dialog = AddDeviceDialog(device_type, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            device = dialog.get_device_data()
            self.system.devices[device_type].append(device)
            self._load_system_data()
            self._calculate_power()
            self.status_label.setText(f"Added {device['name']} to {device_type}")

    def _remove_device(self, device_type: str):
        """Remove selected device."""
        device_list = self.device_lists[device_type]
        current_item = device_list.currentItem()
        if current_item:
            row = device_list.row(current_item)
            if row >= 0:
                del self.system.devices[device_type][row]
                self._load_system_data()
                self._calculate_power()
                self.status_label.setText(f"Removed device from {device_type}")

    def _calculate_power(self):
        """Calculate and display power requirements."""
        load = self.system.calculate_power_load()
        self.calculated_load_label.setText(f"{load:.2f} A")

        # Update power requirements
        self.system.power_requirements.update(
            {
                "primary_voltage": self.primary_voltage_spin.value(),
                "secondary_voltage": self.secondary_voltage_spin.value(),
                "battery_backup_hours": self.battery_hours_spin.value(),
                "calculated_load": load,
            }
        )

    def _check_nfpa_compliance(self):
        """Check NFPA compliance for the current system."""
        compliance_report = "NFPA 72 Compliance Analysis\n"
        compliance_report += "=" * 40 + "\n\n"

        # NFPA 72 requirements analysis
        smoke_count = len(self.system.devices.get("smoke_detectors", []))
        heat_count = len(self.system.devices.get("heat_detectors", []))
        pull_count = len(self.system.devices.get("pull_stations", []))
        strobe_count = len(self.system.devices.get("horn_strobes", []))
        speaker_count = len(self.system.devices.get("speakers", []))

        # Basic NFPA requirements
        issues = []

        # Check for minimum devices
        if smoke_count == 0 and heat_count == 0:
            issues.append(
                "WARNING: No smoke or heat detectors found - violates NFPA 72 requirement for detection devices"
            )

        if pull_count == 0:
            issues.append(
                "WARNING: No manual pull stations found - violates NFPA 72 requirement for manual activation"
            )

        if strobe_count == 0:
            issues.append(
                "WARNING: No notification appliances found - violates NFPA 72 requirement for occupant notification"
            )

        # Check spacing and coverage (simplified)
        room_area = self.room_length_spin.value() * self.room_width_spin.value()
        max_devices_per_room = max(1, room_area // 900)  # Rough estimate: 900 sq ft per detector

        total_detectors = smoke_count + heat_count
        if total_detectors > max_devices_per_room * 2:
            issues.append(
                f"WARNING: Too many detectors for room size ({total_detectors} detectors, recommended max {max_devices_per_room * 2})"
            )

        # Power requirements check
        calculated_load = self.system.power_requirements.get("calculated_load", 0)
        if calculated_load > 10:  # Rough threshold
            issues.append(
                f"WARNING: High power load ({calculated_load:.2f}A) - verify power supply capacity"
            )

        # Report results
        if issues:
            compliance_report += "COMPLIANCE ISSUES FOUND:\n\n"
            for issue in issues:
                compliance_report += f"• {issue}\n"
            compliance_report += "\n"
        else:
            compliance_report += "✓ System appears to meet basic NFPA 72 requirements\n\n"

        # Recommendations
        compliance_report += "RECOMMENDATIONS:\n"
        compliance_report += "• Verify detector spacing per NFPA 72 Chapter 17\n"
        compliance_report += "• Ensure proper zoning and supervision\n"
        compliance_report += "• Verify notification appliance coverage per NFPA 72 Chapter 18\n"
        compliance_report += "• Confirm power supply calculations and battery backup\n"
        compliance_report += "• Review installation requirements and documentation\n"

        self.compliance_text.setPlainText(compliance_report)

    def _add_zone(self):
        """Add a new zone to the system."""
        zone_name, ok = QtWidgets.QInputDialog.getText(self, "Add Zone", "Enter zone name:")
        if ok and zone_name.strip():
            zone_name = zone_name.strip()
            # Check if zone already exists
            existing_zones = [
                self.zones_list.item(i).text() for i in range(self.zones_list.count())
            ]
            if zone_name in existing_zones:
                QtWidgets.QMessageBox.warning(
                    self, "Duplicate Zone", f"Zone '{zone_name}' already exists."
                )
                return

            # Add zone to list
            self.zones_list.addItem(zone_name)

            # Add zone to system data
            if not hasattr(self.system, "zones") or self.system.zones is None:
                self.system.zones = []
            self.system.zones.append(
                {
                    "name": zone_name,
                    "devices": [],
                    "area_sqft": 0,
                    "created_date": QtCore.QDateTime.currentDateTime().toString(),
                }
            )

            self.status_label.setText(f"Added zone: {zone_name}")

    def _remove_zone(self):
        """Remove selected zone."""
        current_item = self.zones_list.currentItem()
        if current_item:
            zone_name = current_item.text()
            # Confirm deletion
            reply = QtWidgets.QMessageBox.question(
                self,
                "Remove Zone",
                f"Are you sure you want to remove zone '{zone_name}'?\n\n"
                "This will not remove devices, but they will no longer be assigned to this zone.",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            )

            if reply == QtWidgets.QMessageBox.Yes:
                # Remove from list
                row = self.zones_list.row(current_item)
                self.zones_list.takeItem(row)

                # Remove from system data
                self.system.zones = [z for z in self.system.zones if z["name"] != zone_name]

                self.status_label.setText(f"Removed zone: {zone_name}")
        else:
            QtWidgets.QMessageBox.information(
                self, "No Selection", "Please select a zone to remove."
            )

    def _auto_place_devices(self):
        """Automatically place devices based on coverage requirements."""
        try:
            # Get room dimensions
            room_length = self.room_length_spin.value()
            room_width = self.room_width_spin.value()
            room_area = room_length * room_width

            if room_area == 0:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Dimensions",
                    "Please set room dimensions in the Coverage & NFPA tab before auto-placing devices.",
                )
                return

            # Calculate required devices
            smoke_spacing = 900  # sq ft per smoke detector
            heat_spacing = 2500  # sq ft per heat detector
            strobe_spacing = 20  # feet between strobes

            required_smoke = max(1, int(room_area // smoke_spacing))
            required_heat = max(1, int(room_area // heat_spacing))
            required_strobes = max(
                1, int((room_length // strobe_spacing) * (room_width // strobe_spacing))
            )

            # Clear existing devices
            reply = QtWidgets.QMessageBox.question(
                self,
                "Clear Existing Devices",
                "Auto-placement will replace all existing devices. Continue?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            )

            if reply != QtWidgets.QMessageBox.Yes:
                return

            # Clear devices
            for device_type in self.system.devices:
                self.system.devices[device_type] = []

            # Add smoke detectors
            for i in range(required_smoke):
                self.system.devices["smoke_detectors"].append(
                    {
                        "name": f"Smoke Detector {i+1}",
                        "location": f"Auto-placed (Room area: {room_area} sq ft)",
                        "quantity": 1,
                        "auto_placed": True,
                        "added_date": QtCore.QDateTime.currentDateTime().toString(),
                    }
                )

            # Add heat detectors (fewer than smoke)
            for i in range(min(required_heat, required_smoke // 2)):
                self.system.devices["heat_detectors"].append(
                    {
                        "name": f"Heat Detector {i+1}",
                        "location": f"Auto-placed (Room area: {room_area} sq ft)",
                        "quantity": 1,
                        "auto_placed": True,
                        "added_date": QtCore.QDateTime.currentDateTime().toString(),
                    }
                )

            # Add pull stations (typically 1-2 per building/area)
            self.system.devices["pull_stations"].append(
                {
                    "name": "Manual Pull Station",
                    "location": "Main exit area",
                    "quantity": 1,
                    "auto_placed": True,
                    "added_date": QtCore.QDateTime.currentDateTime().toString(),
                }
            )

            # Add horn/strobes
            for i in range(required_strobes):
                self.system.devices["horn_strobes"].append(
                    {
                        "name": f"Horn/Strobe {i+1}",
                        "location": f"Auto-placed (Grid position {i+1})",
                        "quantity": 1,
                        "auto_placed": True,
                        "added_date": QtCore.QDateTime.currentDateTime().toString(),
                    }
                )

            # Update UI
            self._load_system_data()
            self._calculate_power()

            self.auto_place_status.setText(
                f"Auto-placed: {required_smoke} smoke, {len(self.system.devices['heat_detectors'])} heat, "
                f"{required_strobes} horn/strobes, 1 pull station"
            )
            self.status_label.setText("Devices auto-placed successfully")

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Auto-Placement Error", f"Failed to auto-place devices: {str(e)}"
            )

    def _analyze_optimization(self):
        """Analyze system and provide optimization suggestions."""
        optimization_report = "SYSTEM OPTIMIZATION ANALYSIS\n"
        optimization_report += "=" * 35 + "\n\n"

        devices = self.system.devices
        total_devices = sum(len(devices.get(cat, [])) for cat in devices)

        if total_devices == 0:
            optimization_report += "No devices to analyze. Add devices first.\n"
            self.optimization_text.setPlainText(optimization_report)
            return

        suggestions = []

        # Analyze detector coverage
        smoke_count = len(devices.get("smoke_detectors", []))
        heat_count = len(devices.get("heat_detectors", []))
        total_detectors = smoke_count + heat_count

        room_area = self.room_length_spin.value() * self.room_width_spin.value()

        if room_area > 0:
            detector_density = total_detectors / room_area * 1000  # per 1000 sq ft

            if detector_density < 0.5:
                suggestions.append(
                    f"⚠️ LOW COVERAGE: Only {detector_density:.1f} detectors per 1000 sq ft. "
                    "Consider adding more detectors for better coverage."
                )
            elif detector_density > 4.0:
                suggestions.append(
                    f"⚠️ OVER-COVERAGE: {detector_density:.1f} detectors per 1000 sq ft. "
                    "Consider removing some detectors to reduce costs."
                )
            else:
                suggestions.append(
                    f"✓ Detector density ({detector_density:.1f} per 1000 sq ft) appears optimal."
                )

        # Analyze notification coverage
        notification_count = len(devices.get("horn_strobes", [])) + len(devices.get("speakers", []))
        room_size = max(self.room_length_spin.value(), self.room_width_spin.value())

        if room_size > 0:
            # Rough estimate: one notification device per 20 feet
            recommended_notifications = max(1, int(room_size / 20) ** 2)

            if notification_count < recommended_notifications:
                suggestions.append(
                    f"⚠️ INSUFFICIENT NOTIFICATION: {notification_count} devices, "
                    f"recommend {recommended_notifications} for room size."
                )
            else:
                suggestions.append(
                    f"✓ Notification coverage appears adequate ({notification_count} devices)."
                )

        # Analyze power requirements
        power = self.system.power_requirements
        calculated_load = power.get("calculated_load", 0)

        if calculated_load > 8:  # High load threshold
            suggestions.append(
                f"⚠️ HIGH POWER LOAD: {calculated_load:.2f}A calculated. "
                "Consider using addressable devices or multiple power supplies."
            )
        elif calculated_load < 1:  # Very low load
            suggestions.append(
                "⚠️ LOW POWER LOAD: System may be under-utilized. "
                "Consider adding more devices or verify calculations."
            )

        # Check for device diversity
        device_types_used = sum(1 for cat in devices.values() if len(cat) > 0)

        if device_types_used < 3:
            suggestions.append(
                "⚠️ LIMITED DEVICE TYPES: Using only basic device types. "
                "Consider adding different detection methods for redundancy."
            )

        # Cost optimization suggestions
        if smoke_count > heat_count * 2:
            suggestions.append(
                "💡 COST OPTIMIZATION: Many smoke detectors. "
                "Consider replacing some with heat detectors in appropriate areas."
            )

        # Report results
        optimization_report += f"Total Devices: {total_devices}\n"
        optimization_report += f"Room Area: {room_area} sq ft\n\n"

        if suggestions:
            optimization_report += "OPTIMIZATION SUGGESTIONS:\n"
            optimization_report += "-" * 25 + "\n"
            for suggestion in suggestions:
                optimization_report += f"• {suggestion}\n"
        else:
            optimization_report += "✓ System appears well-optimized with no major issues found.\n"

        self.optimization_text.setPlainText(optimization_report)

    def _update_coverage_analysis(self):
        """Update coverage analysis when room dimensions change."""
        self._analyze_coverage()

    def _analyze_coverage(self):
        """Analyze coverage requirements for the current system and room."""
        analysis_report = "Coverage Analysis Report\n"
        analysis_report += "=" * 30 + "\n\n"

        # Room dimensions
        length = self.room_length_spin.value()
        width = self.room_width_spin.value()
        height = self.ceiling_height_spin.value()
        area = length * width

        analysis_report += f"Room Dimensions: {length}' x {width}' x {height}' ceiling\n"
        analysis_report += f"Room Area: {area} sq ft\n\n"

        # NFPA 72 spacing requirements (simplified)
        analysis_report += "NFPA 72 SPACING REQUIREMENTS:\n"

        # Smoke detector spacing
        smoke_spacing = 900  # sq ft per detector (simplified)
        max_smoke_detectors = max(1, area // smoke_spacing)
        analysis_report += (
            f"Smoke Detectors: Max {max_smoke_detectors} per room (900 sq ft spacing)\n"
        )

        # Heat detector spacing
        heat_spacing = 2500  # sq ft per detector (simplified)
        max_heat_detectors = max(1, area // heat_spacing)
        analysis_report += (
            f"Heat Detectors: Max {max_heat_detectors} per room (2500 sq ft spacing)\n\n"
        )

        # Current system analysis
        analysis_report += "CURRENT SYSTEM ANALYSIS:\n"
        smoke_count = len(self.system.devices.get("smoke_detectors", []))
        heat_count = len(self.system.devices.get("heat_detectors", []))
        total_detectors = smoke_count + heat_count

        analysis_report += f"Smoke Detectors: {smoke_count}\n"
        analysis_report += f"Heat Detectors: {heat_count}\n"
        analysis_report += f"Total Detectors: {total_detectors}\n\n"

        # Coverage assessment
        if total_detectors == 0:
            analysis_report += "⚠️  NO DETECTORS - Coverage requirement not met\n"
        elif total_detectors < max_smoke_detectors:
            coverage_percent = (total_detectors / max_smoke_detectors) * 100
            analysis_report += (
                f"✓ Coverage: {coverage_percent:.1f}% of recommended smoke detector density\n"
            )
        else:
            analysis_report += f"⚠️  OVER-COVERAGE: {total_detectors} detectors vs recommended max {max_smoke_detectors}\n"

        # Strobe coverage analysis
        analysis_report += "\nNOTIFICATION COVERAGE:\n"
        strobe_count = len(self.system.devices.get("horn_strobes", []))
        speaker_count = len(self.system.devices.get("speakers", []))

        # Simplified strobe requirements
        max_strobe_spacing = 20  # feet
        required_strobes = max(
            1, math.ceil(length / max_strobe_spacing) * math.ceil(width / max_strobe_spacing)
        )
        analysis_report += f"Horn/Strobes: {strobe_count} (recommended: {required_strobes} for {length}'x{width}' room)\n"
        analysis_report += f"Speakers: {speaker_count}\n"

        if strobe_count < required_strobes:
            analysis_report += (
                f"⚠️  Insufficient strobes - need {required_strobes - strobe_count} more\n"
            )
        else:
            analysis_report += "✓ Strobe coverage appears adequate\n"

        self.coverage_text.setPlainText(analysis_report)

    def _new_system(self):
        """Create a new system."""
        self.system = SystemConfiguration()
        self._load_system_data()
        self.status_label.setText("New system created")

    def _load_system(self):
        """Load a system from file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load System", "", "AutoFire Systems (*.afs);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    self.system = SystemConfiguration.from_dict(data)
                    self._load_system_data()
                    self.status_label.setText(f"Loaded system: {self.system.name}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Load Error", f"Failed to load system: {str(e)}"
                )

    def _save_system(self):
        """Save the current system."""
        # Update system data from UI
        self.system.name = self.system_name_edit.text()
        self.system.modified_date = QtCore.QDateTime.currentDateTime().toString()

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save System",
            f"{self.system.name}.afs",
            "AutoFire Systems (*.afs);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(self.system.to_dict(), f, indent=2)
                self.status_label.setText(f"Saved system: {self.system.name}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Save Error", f"Failed to save system: {str(e)}"
                )

    def _generate_report(self):
        """Generate system report."""
        report = f"""Fire Alarm System Report
System: {self.system.name}
FACP Type: {self.system.facp_type}
Created: {self.system.created_date}
Modified: {self.system.modified_date}

Device Summary:
"""

        total_devices = 0
        for device_type, devices in self.system.devices.items():
            count = len(devices)
            total_devices += count
            display_name = device_type.replace("_", " ").title()
            report += f"{display_name}: {count}\n"

        report += f"\nTotal Devices: {total_devices}\n\n"

        report += f"""Power Requirements:
Primary Voltage: {self.system.power_requirements['primary_voltage']}V
Secondary Voltage: {self.system.power_requirements['secondary_voltage']}V
Battery Backup: {self.system.power_requirements['battery_backup_hours']} hours
Calculated Load: {self.system.power_requirements['calculated_load']:.2f} A

Device Details:
"""

        for device_type, devices in self.system.devices.items():
            if devices:
                display_name = device_type.replace("_", " ").title()
                report += f"\n{display_name}:\n"
                for device in devices:
                    report += f"  - {device['name']} ({device['location']})\n"

        # Show report
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("System Report")
        dialog.resize(600, 400)

        layout = QtWidgets.QVBoxLayout(dialog)
        text_edit = QtWidgets.QTextEdit()
        text_edit.setPlainText(report)
        layout.addWidget(text_edit)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Close
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        def save_report():
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                dialog, "Save Report", "", "Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                with open(file_path, "w") as f:
                    f.write(report)

        buttons.accepted.connect(save_report)
        layout.addWidget(buttons)

        dialog.exec()


class AddDeviceDialog(QtWidgets.QDialog):
    """Dialog for adding a device to the system."""

    def __init__(self, device_type: str, parent=None):
        super().__init__(parent)
        self.device_type = device_type
        self.setWindowTitle(f"Add {device_type.replace('_', ' ').title()[:-1]}")
        self.setModal(True)

        layout = QtWidgets.QFormLayout(self)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Device name or model")

        self.location_edit = QtWidgets.QLineEdit()
        self.location_edit.setPlaceholderText("Room, zone, or location")

        self.quantity_spin = QtWidgets.QSpinBox()
        self.quantity_spin.setRange(1, 1000)
        self.quantity_spin.setValue(1)

        layout.addRow("Name/Model:", self.name_edit)
        layout.addRow("Location:", self.location_edit)
        layout.addRow("Quantity:", self.quantity_spin)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_device_data(self) -> dict[str, Any]:
        """Get device data from dialog."""
        return {
            "name": self.name_edit.text(),
            "location": self.location_edit.text(),
            "quantity": self.quantity_spin.value(),
            "added_date": QtCore.QDateTime.currentDateTime().toString(),
        }
