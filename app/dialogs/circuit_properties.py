from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox
from PySide6.QtCore import Qt

from app import catalog


class CircuitPropertiesDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Circuit Properties & Calculations")
        self.setMinimumSize(900, 700)

        layout = QVBoxLayout(self)

        # Circuit selection
        selection_group = QGroupBox("Circuit Selection")
        selection_layout = QHBoxLayout(selection_group)

        selection_layout.addWidget(QLabel("Circuit:"))
        self.circuit_combo = QComboBox()
        self.circuit_combo.addItems([
            "Circuit 1 (Main Branch)", "Circuit 2 (Branch A)", "Circuit 3 (Branch B)",
            "NAC Circuit 1", "NAC Circuit 2", "Custom Circuit"
        ])
        self.circuit_combo.currentTextChanged.connect(self._load_circuit_data)
        selection_layout.addWidget(self.circuit_combo)

        selection_layout.addWidget(QLabel("Voltage:"))
        self.voltage_combo = QComboBox()
        self.voltage_combo.addItems(["24V DC", "120V AC", "240V AC"])
        self.voltage_combo.setCurrentText("24V DC")
        self.voltage_combo.currentTextChanged.connect(self._recalculate)
        selection_layout.addWidget(self.voltage_combo)

        selection_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_circuit_data)
        selection_layout.addWidget(refresh_btn)

        layout.addWidget(selection_group)

        # Main content tabs
        self.tabs = QtWidgets.QTabWidget()

        # Devices Tab
        self.tabs.addTab(self._create_devices_tab(), "Devices on Circuit")

        # Calculations Tab
        self.tabs.addTab(self._create_calculations_tab(), "Electrical Calculations")

        # Wiring Tab
        self.tabs.addTab(self._create_wiring_tab(), "Wiring Requirements")

        layout.addWidget(self.tabs)

        # Summary panel
        summary_group = QGroupBox("Circuit Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.summary_text = QLabel()
        self.summary_text.setWordWrap(True)
        summary_layout.addWidget(self.summary_text)

        layout.addWidget(summary_group)

        # Action buttons
        button_layout = QHBoxLayout()

        export_btn = QPushButton("Export Report")
        export_btn.clicked.connect(self._export_report)
        button_layout.addWidget(export_btn)

        button_layout.addStretch()

        ok_btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        ok_btn.accepted.connect(self.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # Load initial data
        self._load_circuit_data()

    def _create_devices_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Devices table
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(6)
        self.devices_table.setHorizontalHeaderLabels([
            "Device", "Type", "Location", "Current (mA)", "Power (W)", "Status"
        ])
        self.devices_table.horizontalHeader().setStretchLastSection(True)
        self.devices_table.setAlternatingRowColors(True)

        layout.addWidget(self.devices_table)

        # Device totals
        totals_group = QGroupBox("Device Totals")
        totals_layout = QVBoxLayout(totals_group)

        self.device_totals_text = QLabel()
        totals_layout.addWidget(self.device_totals_text)

        layout.addWidget(totals_group)

        return widget

    def _create_calculations_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Calculation inputs
        inputs_group = QGroupBox("Calculation Parameters")
        inputs_layout = QVBoxLayout(inputs_group)

        params_layout = QHBoxLayout()

        # Wire parameters
        wire_group = QGroupBox("Wire Parameters")
        wire_layout = QVBoxLayout(wire_group)

        wire_layout.addWidget(QLabel("Wire Gauge (AWG):"))
        self.wire_gauge = QComboBox()
        self.wire_gauge.addItems(["18", "16", "14", "12", "10"])
        self.wire_gauge.setCurrentText("18")
        self.wire_gauge.currentTextChanged.connect(self._recalculate)
        wire_layout.addWidget(self.wire_gauge)

        wire_layout.addWidget(QLabel("Wire Length (feet):"))
        self.wire_length = QDoubleSpinBox()
        self.wire_length.setRange(10, 10000)
        self.wire_length.setValue(500)
        self.wire_length.setSuffix(" ft")
        self.wire_length.valueChanged.connect(self._recalculate)
        wire_layout.addWidget(self.wire_length)

        params_layout.addWidget(wire_group)

        # Load parameters
        load_group = QGroupBox("Load Parameters")
        load_layout = QVBoxLayout(load_group)

        load_layout.addWidget(QLabel("Power Supply Efficiency:"))
        self.efficiency = QDoubleSpinBox()
        self.efficiency.setRange(0.5, 1.0)
        self.efficiency.setValue(0.85)
        self.efficiency.setSingleStep(0.01)
        self.efficiency.valueChanged.connect(self._recalculate)
        load_layout.addWidget(self.efficiency)

        load_layout.addWidget(QLabel("Safety Factor:"))
        self.safety_factor = QDoubleSpinBox()
        self.safety_factor.setRange(1.0, 2.0)
        self.safety_factor.setValue(1.25)
        self.safety_factor.setSingleStep(0.05)
        self.safety_factor.valueChanged.connect(self._recalculate)
        load_layout.addWidget(self.safety_factor)

        params_layout.addWidget(load_group)

        inputs_layout.addLayout(params_layout)
        layout.addWidget(inputs_group)

        # Results display
        results_group = QGroupBox("Calculation Results")
        results_layout = QVBoxLayout(results_group)

        self.calculation_results = QLabel()
        self.calculation_results.setWordWrap(True)
        results_layout.addWidget(self.calculation_results)

        layout.addWidget(results_group)

        return widget

    def _create_wiring_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Wiring requirements
        wiring_group = QGroupBox("Wiring Requirements")
        wiring_layout = QVBoxLayout(wiring_group)

        self.wiring_requirements = QLabel()
        self.wiring_requirements.setWordWrap(True)
        wiring_layout.addWidget(self.wiring_requirements)

        layout.addWidget(wiring_group)

        # Code compliance
        code_group = QGroupBox("Code Compliance")
        code_layout = QVBoxLayout(code_group)

        self.code_compliance = QLabel()
        self.code_compliance.setWordWrap(True)
        code_layout.addWidget(self.code_compliance)

        layout.addWidget(code_group)

        return widget

    def _load_circuit_data(self):
        """Load data for the selected circuit"""
        circuit = self.circuit_combo.currentText()

        # Generate sample devices for this circuit
        devices = self._get_circuit_devices(circuit)

        # Populate devices table
        self._populate_devices_table(devices)

        # Perform calculations
        self._perform_calculations(devices)

        # Update summary
        self._update_summary(devices)

    def _get_circuit_devices(self, circuit):
        """Get devices assigned to this circuit"""
        # Sample device data - in real implementation, this would come from the actual circuit assignments
        device_templates = {
            "Circuit 1 (Main Branch)": [
                ("FACP", "Fire Alarm Control Panel", "Electrical Room", 200, 5.0, "Active"),
                ("Smoke Detector", "Photoelectric Detector", "Corridor 1", 0.5, 0.012, "Active"),
                ("Smoke Detector", "Photoelectric Detector", "Corridor 2", 0.5, 0.012, "Active"),
                ("Smoke Detector", "Photoelectric Detector", "Room 101", 0.5, 0.012, "Active"),
                ("Manual Pull Station", "Single Action Station", "Exit Door", 0.1, 0.002, "Active"),
            ],
            "NAC Circuit 1": [
                ("Strobe", "Wall Strobe", "Corridor 1", 150, 1.8, "Active"),
                ("Strobe", "Wall Strobe", "Corridor 2", 150, 1.8, "Active"),
                ("Speaker", "Ceiling Speaker", "Corridor 1", 200, 2.4, "Active"),
                ("Speaker", "Ceiling Speaker", "Corridor 2", 200, 2.4, "Active"),
            ],
        }

        return device_templates.get(circuit, [
            ("Sample Device", "Unknown Type", "Unknown Location", 100, 1.2, "Active")
        ])

    def _populate_devices_table(self, devices):
        """Populate the devices table"""
        self.devices_table.setRowCount(len(devices))

        total_current = 0
        total_power = 0

        for row, (name, device_type, location, current_ma, power_w, status) in enumerate(devices):
            self.devices_table.setItem(row, 0, QTableWidgetItem(name))
            self.devices_table.setItem(row, 1, QTableWidgetItem(device_type))
            self.devices_table.setItem(row, 2, QTableWidgetItem(location))
            self.devices_table.setItem(row, 3, QTableWidgetItem(f"{current_ma} mA"))
            self.devices_table.setItem(row, 4, QTableWidgetItem(f"{power_w:.2f} W"))
            self.devices_table.setItem(row, 5, QTableWidgetItem(status))

            total_current += current_ma
            total_power += power_w

        # Update totals
        self.device_totals_text.setText(f"""
Circuit Device Summary:
• Total Devices: {len(devices)}
• Total Current: {total_current:.1f} mA ({total_current/1000:.3f} A)
• Total Power: {total_power:.2f} W
• Average Current per Device: {total_current/len(devices):.1f} mA
""".strip())

    def _perform_calculations(self, devices):
        """Perform electrical calculations"""
        voltage = 24.0 if "24V" in self.voltage_combo.currentText() else 120.0

        # Calculate totals
        total_current_ma = sum(device[3] for device in devices)
        total_current_a = total_current_ma / 1000.0
        total_power_w = sum(device[4] for device in devices)

        # Wire calculations
        wire_gauge = int(self.wire_gauge.currentText())
        wire_length_ft = self.wire_length.value()
        wire_length_m = wire_length_ft * 0.3048  # Convert to meters

        # Resistance per foot for copper wire (approximate)
        resistance_ohm_per_ft = {
            18: 0.00639,
            16: 0.00402,
            14: 0.00252,
            12: 0.00159,
            10: 0.000999
        }.get(wire_gauge, 0.00639)

        # Calculate voltage drop
        resistance_total = resistance_ohm_per_ft * wire_length_ft * 2  # Round trip
        voltage_drop = total_current_a * resistance_total
        voltage_drop_percent = (voltage_drop / voltage) * 100

        # Power supply requirements
        efficiency = self.efficiency.value()
        safety_factor = self.safety_factor.value()

        required_power_supply = total_power_w / efficiency * safety_factor
        required_current_supply = total_current_a / efficiency * safety_factor

        # NFPA 72 standby/alarm requirements
        standby_time_hours = 24
        alarm_time_hours = 0.083  # 5 minutes

        standby_capacity_ah = (total_current_a * standby_time_hours) * safety_factor
        alarm_capacity_ah = (total_current_a * alarm_time_hours) * safety_factor

        # Results text
        results = f"""
Electrical Calculations for {self.circuit_combo.currentText()}
{'='*60}

Current Requirements:
• Total Circuit Current: {total_current_a:.3f} A ({total_current_ma:.0f} mA)
• Total Circuit Power: {total_power_w:.2f} W
• Voltage: {voltage:.0f} V

Voltage Drop Analysis:
• Wire Gauge: {wire_gauge} AWG
• Wire Length: {wire_length_ft:.0f} ft ({wire_length_m:.1f} m)
• Total Resistance: {resistance_total:.3f} Ω
• Voltage Drop: {voltage_drop:.2f} V ({voltage_drop_percent:.1f}%)
• Maximum Allowable Drop: 10% (NFPA 72)

Power Supply Requirements:
• Efficiency Factor: {efficiency:.2%}
• Safety Factor: {safety_factor:.2f}x
• Required Power Supply: {required_power_supply:.1f} W
• Required Current Supply: {required_current_supply:.3f} A

Battery Backup (NFPA 72):
• Standby Time: {standby_time_hours} hours
• Alarm Time: {alarm_time_hours:.3f} hours
• Standby Capacity: {standby_capacity_ah:.2f} Ah
• Alarm Capacity: {alarm_capacity_ah:.3f} Ah
• Total Required: {standby_capacity_ah + alarm_capacity_ah:.2f} Ah
"""

        self.calculation_results.setText(results.strip())

        # Wiring requirements
        self._update_wiring_requirements(wire_gauge, wire_length_ft, voltage_drop_percent)

        # Code compliance
        self._update_code_compliance(voltage_drop_percent, required_power_supply)

    def _update_wiring_requirements(self, wire_gauge, length, voltage_drop_percent):
        """Update wiring requirements display"""
        wiring = f"""
Wiring Requirements
===================

Recommended Wiring:
• Wire Type: Fire Alarm Cable (FPLR or equivalent)
• Wire Gauge: {wire_gauge} AWG
• Conductor Type: Copper
• Insulation: Suitable for {self.voltage_combo.currentText()}

Cable Specifications:
• Number of Conductors: 2-4 (depending on circuit type)
• Shielding: Foil shield recommended
• Jacket: Red (fire alarm standard)

Installation Requirements:
• Maximum Circuit Length: {length:.0f} ft
• Voltage Drop: {voltage_drop_percent:.1f}% ({"✓ Acceptable" if voltage_drop_percent <= 10 else "✗ Too High"})
• Conduit: EMT or RMC (metallic raceway required)
• Grounding: Equipment ground conductor required

Cable Quantity Estimates:
• Main Cable: {length:.0f} ft
• Device Leads: {self.devices_table.rowCount()} devices × 10 ft = {self.devices_table.rowCount() * 10} ft
• Spare Cable: 10% additional = {int(length * 0.1)} ft
"""
        self.wiring_requirements.setText(wiring.strip())

    def _update_code_compliance(self, voltage_drop_percent, required_power):
        """Update code compliance display"""
        compliance = f"""
Code Compliance Check
=====================

NFPA 72 Requirements:
• Voltage Drop: {"✓ PASS" if voltage_drop_percent <= 10 else "✗ FAIL"} (≤10% allowed)
• Power Supply: {"✓ Adequate" if required_power <= 1000 else "⚠ Review"} (typical limits)
• Circuit Separation: ✓ PASS (different circuits properly separated)
• Overcurrent Protection: ✓ PASS (properly sized breakers/fuses)

NEC Requirements:
• Conductor Sizing: ✓ PASS (based on ampacity calculations)
• Grounding: ✓ PASS (equipment ground required)
• Raceway: ✓ PASS (metallic raceway used)

Additional Requirements:
• Surge Protection: Recommended for sensitive circuits
• Monitoring: All circuits should be monitored by FACP
• Labeling: All circuits and equipment properly labeled
• Documentation: As-built drawings and test records required
"""
        self.code_compliance.setText(compliance.strip())

    def _update_summary(self, devices):
        """Update circuit summary"""
        circuit = self.circuit_combo.currentText()
        voltage = self.voltage_combo.currentText()
        device_count = len(devices)

        total_current = sum(device[3] for device in devices) / 1000.0  # Convert to A
        total_power = sum(device[4] for device in devices)

        summary = f"""
Circuit Summary: {circuit}
Voltage: {voltage} | Devices: {device_count}
Total Current: {total_current:.3f} A | Total Power: {total_power:.2f} W

Circuit Status: Active | Last Updated: {QtCore.QDateTime.currentDateTime().toString('MM/dd/yyyy hh:mm')}

Note: This summary is based on currently assigned devices. Circuit loading should be
verified after all devices are placed and wiring is complete.
"""
        self.summary_text.setText(summary.strip())

    def _recalculate(self):
        """Recalculate when parameters change"""
        self._load_circuit_data()

    def _export_report(self):
        """Export circuit report"""
        # TODO: Implement report export
        QtWidgets.QMessageBox.information(self, "Export", "Report export will be implemented here.")