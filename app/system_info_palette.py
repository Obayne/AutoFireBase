"""
System Information Palette - Shows fire alarm system status and configuration
"""

import json
import os
from typing import Any

from PySide6 import QtWidgets


class SystemInfoPalette(QtWidgets.QDockWidget):
    """Dockable palette showing fire alarm system information and controls."""

    def __init__(self, app_controller, parent=None):
        super().__init__("System Information", parent)

        # Initialize system data
        self.system_data = self._load_system_data()

        self._setup_ui()
        self._update_display()

        # Connect to model space changes
        self.app_controller = app_controller
        self.app_controller.model_space_changed.connect(self._on_model_space_changed)

        # Store reference to wiring tool for circuit info (will be set later)
        self.wiring_tool = None

        # Initialize circuits display
        self.circuits_text.setPlainText("No circuits defined.")

    def _setup_ui(self):
        """Setup the user interface."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # System controls
        controls_group = QtWidgets.QGroupBox("System Controls")
        controls_layout = QtWidgets.QVBoxLayout(controls_group)

        # System builder button
        self.btn_system_builder = QtWidgets.QPushButton("System Builder...")
        self.btn_system_builder.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        self.btn_system_builder.clicked.connect(self._open_system_builder)
        controls_layout.addWidget(self.btn_system_builder)

        # Wire spool button
        self.btn_wire_spool = QtWidgets.QPushButton("Wire Spool...")
        self.btn_wire_spool.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """
        )
        self.btn_wire_spool.clicked.connect(self._open_wire_spool)
        controls_layout.addWidget(self.btn_wire_spool)

        layout.addWidget(controls_group)

        # System status
        status_group = QtWidgets.QGroupBox("System Status")
        status_layout = QtWidgets.QFormLayout(status_group)

        self.lbl_system_name = QtWidgets.QLabel("No system loaded")
        self.lbl_facp_count = QtWidgets.QLabel("0")
        self.lbl_fcps_count = QtWidgets.QLabel("0")
        self.lbl_amp_count = QtWidgets.QLabel("0")
        self.lbl_detector_count = QtWidgets.QLabel("0")
        self.lbl_notification_count = QtWidgets.QLabel("0")
        self.lbl_initiating_count = QtWidgets.QLabel("0")
        self.lbl_total_devices = QtWidgets.QLabel("0")

        status_layout.addRow("System:", self.lbl_system_name)
        status_layout.addRow("FACPs:", self.lbl_facp_count)
        status_layout.addRow("FCPS:", self.lbl_fcps_count)
        status_layout.addRow("AMPs:", self.lbl_amp_count)
        status_layout.addRow("Detectors:", self.lbl_detector_count)
        status_layout.addRow("Notifications:", self.lbl_notification_count)
        status_layout.addRow("Initiating:", self.lbl_initiating_count)
        status_layout.addRow("Total Devices:", self.lbl_total_devices)

        layout.addWidget(status_group)

        # Power information
        power_group = QtWidgets.QGroupBox("Power Information")
        power_layout = QtWidgets.QFormLayout(power_group)

        self.lbl_primary_voltage = QtWidgets.QLabel("-")
        self.lbl_secondary_voltage = QtWidgets.QLabel("-")
        self.lbl_battery_backup = QtWidgets.QLabel("-")
        self.lbl_calculated_load = QtWidgets.QLabel("-")

        power_layout.addRow("Primary:", self.lbl_primary_voltage)
        power_layout.addRow("Secondary:", self.lbl_secondary_voltage)
        power_layout.addRow("Battery:", self.lbl_battery_backup)
        power_layout.addRow("Load:", self.lbl_calculated_load)

        layout.addWidget(power_group)

        # Wire inventory summary
        wire_group = QtWidgets.QGroupBox("Wire Inventory")
        wire_layout = QtWidgets.QFormLayout(wire_group)

        self.lbl_total_spools = QtWidgets.QLabel("0")
        self.lbl_total_wire_ft = QtWidgets.QLabel("0 ft")
        self.lbl_remaining_wire_ft = QtWidgets.QLabel("0 ft")

        wire_layout.addRow("Spools:", self.lbl_total_spools)
        wire_layout.addRow("Total:", self.lbl_total_wire_ft)
        wire_layout.addRow("Remaining:", self.lbl_remaining_wire_ft)

        layout.addWidget(wire_group)

        # Quick actions
        actions_group = QtWidgets.QGroupBox("Quick Actions")
        actions_layout = QtWidgets.QVBoxLayout(actions_group)

        self.btn_calculate_power = QtWidgets.QPushButton("Calculate Power")
        self.btn_calculate_power.clicked.connect(self._calculate_power)
        actions_layout.addWidget(self.btn_calculate_power)

        self.btn_generate_report = QtWidgets.QPushButton("Generate Report")
        self.btn_generate_report.clicked.connect(self._generate_report)
        actions_layout.addWidget(self.btn_generate_report)

        self.btn_reports = QtWidgets.QPushButton("Reports...")
        self.btn_reports.clicked.connect(self._open_reports_dialog)
        actions_layout.addWidget(self.btn_reports)

        layout.addWidget(actions_group)

        # Electrical circuits
        circuits_group = QtWidgets.QGroupBox("Electrical Circuits")
        circuits_layout = QtWidgets.QVBoxLayout(circuits_group)

        self.circuits_text = QtWidgets.QTextEdit()
        self.circuits_text.setReadOnly(True)
        self.circuits_text.setMaximumHeight(200)
        circuits_layout.addWidget(self.circuits_text)

        layout.addWidget(circuits_group)

        layout.addStretch()
        self.setWidget(widget)

    def _load_system_data(self) -> dict[str, Any]:
        """Load current system data."""
        # Try to load from saved system
        system_file = os.path.join(os.path.expanduser("~"), "AutoFire", "current_system.json")
        if os.path.exists(system_file):
            try:
                with open(system_file) as f:
                    return json.load(f)
            except Exception:
                pass

        # Return default empty system
        return {
            "name": "No system loaded",
            "facp_type": "Conventional",
            "devices": {
                "facp": [],
                "fcps": [],
                "amp": [],
                "detectors": [],
                "notifications": [],
                "initiating": [],
            },
            "power_requirements": {
                "primary_voltage": 120,
                "secondary_voltage": 24,
                "battery_backup_hours": 24,
                "calculated_load": 0.0,
            },
        }

    def _update_display(self):
        """Update the display with current system data."""
        data = self.system_data

        self.lbl_system_name.setText(data.get("name", "No system loaded"))

        devices = data.get("devices", {})
        self.lbl_facp_count.setText(str(len(devices.get("facp", []))))
        self.lbl_fcps_count.setText(str(len(devices.get("fcps", []))))
        self.lbl_amp_count.setText(str(len(devices.get("amp", []))))
        self.lbl_detector_count.setText(str(len(devices.get("detectors", []))))
        self.lbl_notification_count.setText(str(len(devices.get("notifications", []))))
        self.lbl_initiating_count.setText(str(len(devices.get("initiating", []))))

        total_devices = sum(
            len(devices.get(cat, []))
            for cat in ["facp", "fcps", "amp", "detectors", "notifications", "initiating"]
        )
        self.lbl_total_devices.setText(str(total_devices))

        power = data.get("power_requirements", {})
        self.lbl_primary_voltage.setText(f"{power.get('primary_voltage', 0)}V")
        self.lbl_secondary_voltage.setText(f"{power.get('secondary_voltage', 0)}V")
        self.lbl_battery_backup.setText(f"{power.get('battery_backup_hours', 0)}h")
        self.lbl_calculated_load.setText(f"{power.get('calculated_load', 0):.2f}A")

        # Update wire inventory
        self._update_wire_inventory()

        # Update circuit info (only if wiring tool is available)
        if hasattr(self, "wiring_tool") and self.wiring_tool:
            self._update_circuit_info()

    def _update_circuit_info(self):
        """Update circuit information display."""
        if self.wiring_tool:
            circuit_summary = self.wiring_tool.get_circuit_summary()
            self.circuits_text.setPlainText(circuit_summary)
        else:
            self.circuits_text.setPlainText("No circuits defined.")

    def _open_reports_dialog(self):
        """Open the comprehensive reports dialog."""
        from app.reports_dialog import ReportsDialog

        dialog = ReportsDialog(self.system_data, self.wiring_tool, self)
        dialog.exec()

    def _update_wire_inventory(self):
        """Update wire inventory display."""
        try:
            # Try to load wire inventory directly
            inventory_file = os.path.join(
                os.path.expanduser("~"), "AutoFire", "wire_inventory.json"
            )
            if os.path.exists(inventory_file):
                with open(inventory_file) as f:
                    data = json.load(f)
                    total_spools = len(data)
                    total_wire = sum(
                        spool_data.get("total_length_ft", 0) for spool_data in data.values()
                    )
                    remaining_wire = sum(
                        spool_data.get("remaining_length_ft", 0) for spool_data in data.values()
                    )

                    self.lbl_total_spools.setText(str(total_spools))
                    self.lbl_total_wire_ft.setText(f"{total_wire:.0f} ft")
                    self.lbl_remaining_wire_ft.setText(f"{remaining_wire:.0f} ft")
            else:
                self.lbl_total_spools.setText("0")
                self.lbl_total_wire_ft.setText("0 ft")
                self.lbl_remaining_wire_ft.setText("0 ft")
        except Exception:
            self.lbl_total_spools.setText("0")
            self.lbl_total_wire_ft.setText("0 ft")
            self.lbl_remaining_wire_ft.setText("0 ft")

    def _open_system_builder(self):
        """Open the system builder dialog."""
        try:
            from app.system_builder import SystemBuilderDialog

            dialog = SystemBuilderDialog(self)
            dialog.exec()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to open System Builder: {e}")

    def _open_wire_spool(self):
        """Open the wire spool dialog."""
        try:
            from app.wire_spool import WireSpoolDialog

            dialog = WireSpoolDialog(self)
            dialog.exec()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to open Wire Spool: {e}")

    def _calculate_power(self):
        """Calculate system power requirements."""
        QtWidgets.QMessageBox.information(
            self,
            "Calculate Power",
            "Power calculation would analyze all devices in the current system and calculate total load requirements.",
        )

    def _generate_report(self):
        """Generate system report."""
        QtWidgets.QMessageBox.information(
            self,
            "Generate Report",
            "Report generation would create a comprehensive system documentation including device lists, wiring requirements, and power calculations.",
        )

    def _on_model_space_changed(self, change_data):
        """Handle model space changes to update system info."""
        change_type = change_data.get("type", "general")
        if change_type in ["device_placed", "device_removed", "system_updated"]:
            # Reload system data and update display
            self.system_data = self._load_system_data()
            self._update_display()

    def update_system_data(self, new_data: dict[str, Any]):
        """Update the system data and refresh display."""
        self.system_data = new_data
        self._update_display()

        # Save to file
        system_file = os.path.join(os.path.expanduser("~"), "AutoFire", "current_system.json")
        try:
            os.makedirs(os.path.dirname(system_file), exist_ok=True)
            with open(system_file, "w") as f:
                json.dump(new_data, f, indent=2)
        except Exception:
            pass
