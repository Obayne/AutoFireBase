"""
Comprehensive Reports Dialog - Generate various system reports
"""

import json
from datetime import datetime
from typing import Any

from PySide6 import QtWidgets


class ReportsDialog(QtWidgets.QDialog):
    """Dialog for generating comprehensive system reports."""

    def __init__(self, system_data: dict[str, Any], wiring_tool=None, parent=None):
        super().__init__(parent)
        self.system_data = system_data
        self.wiring_tool = wiring_tool
        self.setWindowTitle("AutoFire Reports")
        self.setModal(False)
        self.resize(800, 600)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Report type selection
        type_group = QtWidgets.QGroupBox("Report Type")
        type_layout = QtWidgets.QHBoxLayout(type_group)

        self.report_type_combo = QtWidgets.QComboBox()
        self.report_type_combo.addItems(
            [
                "System Specifications",
                "Coverage Analysis",
                "NFPA Compliance",
                "Electrical Calculations",
                "Battery Calculations",
                "Bill of Materials (BOM)",
                "Complete System Report",
            ]
        )
        self.report_type_combo.currentTextChanged.connect(self._update_preview)
        type_layout.addWidget(self.report_type_combo)

        type_layout.addStretch()
        layout.addWidget(type_group)

        # Report preview
        preview_group = QtWidgets.QGroupBox("Report Preview")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)

        self.preview_text = QtWidgets.QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)

        layout.addWidget(preview_group)

        # Action buttons
        buttons_layout = QtWidgets.QHBoxLayout()

        self.btn_generate = QtWidgets.QPushButton("Generate Report")
        self.btn_generate.clicked.connect(self._generate_report)
        buttons_layout.addWidget(self.btn_generate)

        self.btn_save = QtWidgets.QPushButton("Save to File...")
        self.btn_save.clicked.connect(self._save_report)
        buttons_layout.addWidget(self.btn_save)

        self.btn_print = QtWidgets.QPushButton("Print...")
        self.btn_print.clicked.connect(self._print_report)
        buttons_layout.addWidget(self.btn_print)

        buttons_layout.addStretch()

        self.btn_close = QtWidgets.QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_close)

        layout.addLayout(buttons_layout)

        # Generate initial preview
        self._update_preview()

    def _update_preview(self):
        """Update the report preview based on selected type."""
        report_type = self.report_type_combo.currentText()

        if report_type == "System Specifications":
            content = self._generate_system_specs()
        elif report_type == "Coverage Analysis":
            content = self._generate_coverage_analysis()
        elif report_type == "NFPA Compliance":
            content = self._generate_nfpa_compliance()
        elif report_type == "Electrical Calculations":
            content = self._generate_electrical_calculations()
        elif report_type == "Battery Calculations":
            content = self._generate_battery_calculations()
        elif report_type == "Bill of Materials (BOM)":
            content = self._generate_bom()
        elif report_type == "Complete System Report":
            content = self._generate_complete_report()
        else:
            content = "Select a report type to preview."

        self.preview_text.setPlainText(content)

    def _generate_system_specs(self) -> str:
        """Generate system specifications report."""
        report = "AUTO-FIRE SYSTEM SPECIFICATIONS\n"
        report += "=" * 50 + "\n\n"

        # System info
        system_name = self.system_data.get("name", "Unnamed System")
        report += f"System Name: {system_name}\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Device summary
        devices = self.system_data.get("devices", {})
        report += "DEVICE INVENTORY:\n"
        report += "-" * 20 + "\n"

        total_devices = 0
        for category, device_list in devices.items():
            count = len(device_list)
            total_devices += count
            category_name = category.replace("_", " ").title()
            report += f"{category_name}: {count}\n"

        report += f"\nTotal Devices: {total_devices}\n\n"

        # Power requirements
        power = self.system_data.get("power_requirements", {})
        report += "POWER REQUIREMENTS:\n"
        report += "-" * 20 + "\n"
        report += f"Primary Voltage: {power.get('primary_voltage', 'N/A')}V\n"
        report += f"Secondary Voltage: {power.get('secondary_voltage', 'N/A')}V\n"
        report += f"Battery Backup: {power.get('battery_backup_hours', 'N/A')} hours\n"
        report += f"Calculated Load: {power.get('calculated_load', 0):.2f}A\n\n"

        # Coverage areas
        coverage_areas = self.system_data.get("coverage_areas", [])
        if coverage_areas:
            report += "COVERAGE AREAS:\n"
            report += "-" * 15 + "\n"
            for area in coverage_areas:
                report += (
                    f"• {area.get('name', 'Unnamed Area')}: {area.get('area_sqft', 0)} sq ft\n"
                )
            report += "\n"

        return report

    def _generate_coverage_analysis(self) -> str:
        """Generate coverage analysis report."""
        report = "COVERAGE ANALYSIS REPORT\n"
        report += "=" * 30 + "\n\n"

        # NFPA 72 spacing requirements (simplified)
        devices = self.system_data.get("devices", {})
        smoke_count = len(devices.get("smoke_detectors", []))
        heat_count = len(devices.get("heat_detectors", []))
        strobe_count = len(devices.get("horn_strobes", []))
        speaker_count = len(devices.get("speakers", []))

        report += "DETECTOR COVERAGE:\n"
        report += f"Smoke Detectors: {smoke_count}\n"
        report += f"Heat Detectors: {heat_count}\n"
        report += f"Total Detectors: {smoke_count + heat_count}\n\n"

        report += "NOTIFICATION COVERAGE:\n"
        report += f"Horn/Strobes: {strobe_count}\n"
        report += f"Speakers: {speaker_count}\n\n"

        # Basic coverage assessment
        coverage_areas = self.system_data.get("coverage_areas", [])
        if coverage_areas:
            total_area = sum(area.get("area_sqft", 0) for area in coverage_areas)
            report += f"Total Covered Area: {total_area} sq ft\n"

            # Rough detector density calculation
            detector_density = (
                (smoke_count + heat_count) / total_area * 1000 if total_area > 0 else 0
            )
            report += f"Detector Density: {detector_density:.1f} per 1000 sq ft\n\n"

            if detector_density < 1.0:
                report += "⚠️  LOW DETECTOR DENSITY - May not meet NFPA 72 requirements\n"
            elif detector_density > 3.0:
                report += "⚠️  HIGH DETECTOR DENSITY - Check for over-coverage\n"
            else:
                report += "✓ Detector density appears adequate\n"
        else:
            report += "⚠️  No coverage areas defined - Cannot analyze coverage\n"

        return report

    def _generate_nfpa_compliance(self) -> str:
        """Generate NFPA compliance report."""
        report = "NFPA 72 COMPLIANCE ANALYSIS\n"
        report += "=" * 35 + "\n\n"

        devices = self.system_data.get("devices", {})
        issues = []
        compliant_items = []

        # Check for required device types
        smoke_count = len(devices.get("smoke_detectors", []))
        heat_count = len(devices.get("heat_detectors", []))
        pull_count = len(devices.get("pull_stations", []))
        notification_count = len(devices.get("horn_strobes", [])) + len(devices.get("speakers", []))

        if smoke_count == 0 and heat_count == 0:
            issues.append(
                "No detection devices found - violates NFPA 72 requirement for automatic detection"
            )
        else:
            compliant_items.append("Detection devices present")

        if pull_count == 0:
            issues.append(
                "No manual pull stations found - violates NFPA 72 requirement for manual activation"
            )
        else:
            compliant_items.append("Manual activation devices present")

        if notification_count == 0:
            issues.append(
                "No notification appliances found - violates NFPA 72 occupant notification requirements"
            )
        else:
            compliant_items.append("Notification appliances present")

        # Power supply requirements
        power = self.system_data.get("power_requirements", {})
        calculated_load = power.get("calculated_load", 0)

        if calculated_load > 10:  # Rough threshold
            issues.append(
                f"High calculated load ({calculated_load:.2f}A) - verify power supply capacity"
            )
        else:
            compliant_items.append("Power load within typical limits")

        # Report results
        if issues:
            report += "COMPLIANCE ISSUES FOUND:\n"
            report += "-" * 25 + "\n"
            for issue in issues:
                report += f"• {issue}\n"
            report += "\n"

        if compliant_items:
            report += "COMPLIANT ITEMS:\n"
            report += "-" * 15 + "\n"
            for item in compliant_items:
                report += f"✓ {item}\n"
            report += "\n"

        report += "RECOMMENDATIONS:\n"
        report += "• Consult NFPA 72 for complete requirements\n"
        report += "• Verify detector spacing per Chapter 17\n"
        report += "• Ensure proper notification appliance coverage per Chapter 18\n"
        report += "• Confirm power supply and battery calculations\n"
        report += "• Review installation and testing requirements\n"

        return report

    def _generate_electrical_calculations(self) -> str:
        """Generate electrical calculations report."""
        report = "ELECTRICAL CALCULATIONS REPORT\n"
        report += "=" * 35 + "\n\n"

        devices = self.system_data.get("devices", {})
        power = self.system_data.get("power_requirements", {})

        # Device current calculations
        device_currents = {
            "smoke_detectors": 0.02,  # A per device
            "heat_detectors": 0.02,
            "pull_stations": 0.01,
            "horn_strobes": 0.15,
            "speakers": 0.20,
            "other": 0.05,
        }

        report += "DEVICE CURRENT REQUIREMENTS:\n"
        report += "-" * 30 + "\n"

        total_current = 0.0
        for device_type, current_per_device in device_currents.items():
            count = len(devices.get(device_type, []))
            type_current = count * current_per_device
            total_current += type_current

            type_name = device_type.replace("_", " ").title()
            report += f"{type_name}: {count} × {current_per_device:.3f}A = {type_current:.3f}A\n"

        report += f"\nTotal Device Current: {total_current:.3f}A\n\n"

        # Circuit information from wiring tool
        if self.wiring_tool:
            circuit_summary = self.wiring_tool.get_circuit_summary()
            report += "CIRCUIT ANALYSIS:\n"
            report += "-" * 18 + "\n"
            report += circuit_summary + "\n"
        else:
            report += "No circuit information available.\n\n"

        # Power supply requirements
        primary_voltage = power.get("primary_voltage", 120)
        secondary_voltage = power.get("secondary_voltage", 24)
        battery_hours = power.get("battery_backup_hours", 24)

        report += "POWER SUPPLY REQUIREMENTS:\n"
        report += "-" * 28 + "\n"
        report += f"Primary Voltage: {primary_voltage}V\n"
        report += f"Secondary Voltage: {secondary_voltage}V\n"
        report += f"Battery Backup: {battery_hours} hours\n"
        report += f"Calculated Load: {power.get('calculated_load', 0):.3f}A\n\n"

        # Battery size calculation (simplified)
        battery_capacity = total_current * battery_hours * 1.25  # 25% safety factor
        report += f"Estimated Battery Capacity: {battery_capacity:.1f}Ah (at 25% safety factor)\n"

        return report

    def _generate_battery_calculations(self) -> str:
        """Generate battery calculations report with simple and advanced options."""
        report = "BATTERY CALCULATIONS\n"
        report += "=" * 20 + "\n\n"

        power = self.system_data.get("power_requirements", {})
        devices = self.system_data.get("devices", {})

        # Calculate total current from devices
        total_current = 0.0
        standby_current = 0.0
        alarm_current = 0.0

        for device_data in devices.values():
            if isinstance(device_data, dict):
                # Extract current values from device properties
                props = device_data.get("properties", {})
                if isinstance(props, str):
                    try:
                        props = json.loads(props)
                    except:
                        props = {}

                standby_current += props.get("standby_current_a", 0.02)  # Default detector current
                alarm_current += props.get("alarm_current_a", 0.15)  # Default notification current

        total_current = max(standby_current, alarm_current)  # Use higher of the two for simple calc

        # Simple calculation (current method)
        battery_hours = power.get("battery_backup_hours", 24)
        battery_capacity_simple = total_current * battery_hours * 1.25

        report += "SIMPLE BATTERY CALCULATION:\n"
        report += "-" * 25 + "\n"
        report += f"Total System Current: {total_current:.3f}A\n"
        report += f"Battery Backup Hours: {battery_hours}\n"
        report += "Safety Factor: 1.25 (25%)\n"
        report += f"Required Battery Capacity: {battery_capacity_simple:.1f}Ah\n\n"

        # Advanced calculation (NFPA 72 compliant)
        try:
            from app.battery_calculator import BatteryCalculator, BatteryChemistry

            calc = BatteryCalculator()
            advanced_results = calc.calculate_battery_capacity(
                standby_current_a=standby_current,
                alarm_current_a=alarm_current,
                standby_hours=int(battery_hours),
                alarm_hours=0.5,  # NFPA 72 requires 30 minutes alarm time
                battery_voltage=power.get("secondary_voltage", 24.0),
                battery_chemistry=BatteryChemistry.LEAD_ACID,
                temperature_f=77.0,  # 25°C
                safety_factor=1.25,
            )

            report += "ADVANCED BATTERY CALCULATION (NFPA 72):\n"
            report += "-" * 35 + "\n"
            report += f"Standby Current: {advanced_results['standby_current_a']:.3f}A\n"
            report += f"Alarm Current: {advanced_results['alarm_current_a']:.3f}A\n"
            report += f"Standby Hours: {battery_hours}\n"
            report += "Alarm Hours: 0.5 (NFPA 72 requirement)\n"
            report += f"Temperature: {advanced_results['temperature_f']:.0f}°F\n"
            report += (
                f"Required Battery Capacity: {advanced_results['battery_capacity_ah']:.1f}Ah\n\n"
            )

            # Battery recommendations
            recommendations = calc.get_battery_recommendations(
                advanced_results["battery_capacity_ah"], power.get("secondary_voltage", 24.0)
            )

            if recommendations:
                report += "BATTERY RECOMMENDATIONS:\n"
                report += "-" * 23 + "\n"
                for rec in recommendations[:3]:  # Show top 3 recommendations
                    config = rec["configuration"]
                    size = rec["battery_size_ah"]
                    qty = rec["quantity"]
                    utilization = rec["utilization_percent"]
                    report += f"• {config} × {size}Ah batteries ({qty} total) - {utilization:.1f}% utilization\n"

        except ImportError:
            report += "Advanced battery calculations not available.\n"
            report += "Install battery calculator module for NFPA 72 compliant calculations.\n"

        return report

    def _generate_bom(self) -> str:
        """Generate Bill of Materials report."""
        report = "BILL OF MATERIALS (BOM)\n"
        report += "=" * 25 + "\n\n"

        devices = self.system_data.get("devices", {})

        # Group devices by type and count quantities
        device_counts = {}
        for device_type, device_list in devices.items():
            for device in device_list:
                name = device.get("name", "Unknown Device")
                manufacturer = device.get("manufacturer", "Unknown")
                part_number = device.get("part_number", "")

                key = f"{manufacturer} {name}"
                if part_number:
                    key += f" ({part_number})"

                if key not in device_counts:
                    device_counts[key] = {"quantity": 0, "type": device_type}

                device_counts[key]["quantity"] += device.get("quantity", 1)

        report += "REQUIRED DEVICES:\n"
        report += "-" * 17 + "\n"

        total_quantity = 0
        for device_name, info in sorted(device_counts.items()):
            quantity = info["quantity"]
            total_quantity += quantity
            device_type = info["type"].replace("_", " ").title()
            report += f"{quantity:3d} × {device_name} ({device_type})\n"

        report += f"\nTotal Quantity: {total_quantity} devices\n\n"

        # Add power supply requirements
        power = self.system_data.get("power_requirements", {})
        calculated_load = power.get("calculated_load", 0)

        report += "POWER SUPPLY REQUIREMENTS:\n"
        report += "-" * 28 + "\n"
        report += f"• FACP Power Supply (calculated load: {calculated_load:.2f}A)\n"
        report += f"• Battery Backup System ({power.get('battery_backup_hours', 24)} hours)\n"
        report += f"• Primary Power: {power.get('primary_voltage', 120)}V\n"
        report += f"• Secondary Power: {power.get('secondary_voltage', 24)}V\n\n"

        # Add cable requirements (estimated)
        if self.wiring_tool and hasattr(self.wiring_tool, "circuits"):
            total_wire_length = sum(
                circuit.wire_length for circuit in self.wiring_tool.circuits.values()
            )
            report += "CABLE REQUIREMENTS (estimated):\n"
            report += "-" * 32 + "\n"
            report += f"• Total Wire Length: {total_wire_length:.1f} feet\n"
            report += f"• 18 AWG Fire Alarm Cable: {total_wire_length:.1f} feet\n"
            report += f"• Cable Connectors/Terminals: {len(self.wiring_tool.circuits) * 4} pieces\n"

        return report

    def _generate_complete_report(self) -> str:
        """Generate complete system report combining all sections."""
        report = "COMPLETE AUTO-FIRE SYSTEM REPORT\n"
        report += "=" * 40 + "\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += self._generate_system_specs()
        report += "\n" + "=" * 50 + "\n\n"
        report += self._generate_coverage_analysis()
        report += "\n" + "=" * 50 + "\n\n"
        report += self._generate_nfpa_compliance()
        report += "\n" + "=" * 50 + "\n\n"
        report += self._generate_electrical_calculations()
        report += "\n" + "=" * 50 + "\n\n"
        report += self._generate_bom()

        return report

    def _generate_report(self):
        """Generate the selected report (same as preview for now)."""
        self._update_preview()

    def _save_report(self):
        """Save the current report to a file."""
        report_type = self.report_type_combo.currentText()
        content = self.preview_text.toPlainText()

        # Suggest filename based on report type
        filename_suggestions = {
            "System Specifications": "system_specs.txt",
            "Coverage Analysis": "coverage_analysis.txt",
            "NFPA Compliance": "nfpa_compliance.txt",
            "Electrical Calculations": "electrical_calculations.txt",
            "Bill of Materials (BOM)": "bill_of_materials.txt",
            "Complete System Report": "complete_system_report.txt",
        }

        suggested_name = filename_suggestions.get(report_type, "report.txt")

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Report", suggested_name, "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                QtWidgets.QMessageBox.information(
                    self, "Report Saved", f"Report saved successfully to:\n{file_path}"
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Save Error", f"Failed to save report:\n{str(e)}"
                )

    def _print_report(self):
        """Print the current report."""
        # For now, just show a message that printing is not implemented
        QtWidgets.QMessageBox.information(
            self,
            "Print Report",
            "Printing functionality will be implemented in a future version.\n\n"
            "For now, please save the report to a file and print it manually.",
        )
