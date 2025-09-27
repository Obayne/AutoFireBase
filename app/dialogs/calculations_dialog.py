import math

from PySide6 import QtCore, QtWidgets


class CalculationsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Engineering Calculations")
        self.setModal(True)
        self.resize(600, 500)

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Engineering Calculations")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Tab widget for different calculation types
        self.tab_widget = QtWidgets.QTabWidget()
        layout.addWidget(self.tab_widget)

        # Battery calculation tab
        self.battery_tab = self.create_battery_tab()
        self.tab_widget.addTab(self.battery_tab, "Battery")

        # Wire sizing tab
        self.wire_tab = self.create_wire_tab()
        self.tab_widget.addTab(self.wire_tab, "Wire Sizing")

        # Coverage calculation tab
        self.coverage_tab = self.create_coverage_tab()
        self.tab_widget.addTab(self.coverage_tab, "Coverage")

        # Load calculation tab
        self.load_tab = self.create_load_tab()
        self.tab_widget.addTab(self.load_tab, "Load")

        # OK button
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        self.ok_btn = QtWidgets.QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)
        layout.addLayout(button_layout)

    def create_battery_tab(self):
        """Create the battery calculation tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Input group
        input_group = QtWidgets.QGroupBox("Battery Sizing Inputs")
        input_layout = QtWidgets.QFormLayout(input_group)

        self.battery_standby_current = QtWidgets.QDoubleSpinBox()
        self.battery_standby_current.setRange(0.0, 1000.0)
        self.battery_standby_current.setSingleStep(0.1)
        self.battery_standby_current.setValue(100.0)
        self.battery_standby_current.setSuffix(" mA")
        input_layout.addRow("Standby Current:", self.battery_standby_current)

        self.battery_alarm_current = QtWidgets.QDoubleSpinBox()
        self.battery_alarm_current.setRange(0.0, 1000.0)
        self.battery_alarm_current.setSingleStep(1.0)
        self.battery_alarm_current.setValue(500.0)
        self.battery_alarm_current.setSuffix(" mA")
        input_layout.addRow("Alarm Current:", self.battery_alarm_current)

        self.battery_backup_time = QtWidgets.QDoubleSpinBox()
        self.battery_backup_time.setRange(0.1, 24.0)
        self.battery_backup_time.setSingleStep(0.5)
        self.battery_backup_time.setValue(24.0)
        self.battery_backup_time.setSuffix(" hours")
        input_layout.addRow("Required Backup Time:", self.battery_backup_time)

        self.battery_voltage = QtWidgets.QDoubleSpinBox()
        self.battery_voltage.setRange(12.0, 48.0)
        self.battery_voltage.setSingleStep(1.0)
        self.battery_voltage.setValue(24.0)
        self.battery_voltage.setSuffix(" V")
        input_layout.addRow("System Voltage:", self.battery_voltage)

        layout.addWidget(input_group)

        # Calculation button
        calc_layout = QtWidgets.QHBoxLayout()
        self.battery_calc_btn = QtWidgets.QPushButton("Calculate Battery Size")
        self.battery_calc_btn.clicked.connect(self.calculate_battery)
        calc_layout.addWidget(self.battery_calc_btn)
        calc_layout.addStretch()
        layout.addLayout(calc_layout)

        # Results group
        self.battery_results_group = QtWidgets.QGroupBox("Results")
        self.battery_results_group.setVisible(False)
        results_layout = QtWidgets.QFormLayout(self.battery_results_group)

        self.battery_capacity_result = QtWidgets.QLabel()
        results_layout.addRow("Required Battery Capacity:", self.battery_capacity_result)

        self.battery_amp_hours_result = QtWidgets.QLabel()
        results_layout.addRow("Amp-Hours Required:", self.battery_amp_hours_result)

        self.battery_recommendation_result = QtWidgets.QLabel()
        results_layout.addRow("Recommendation:", self.battery_recommendation_result)

        layout.addWidget(self.battery_results_group)
        layout.addStretch()

        return widget

    def create_wire_tab(self):
        """Create the wire sizing calculation tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Input group
        input_group = QtWidgets.QGroupBox("Wire Sizing Inputs")
        input_layout = QtWidgets.QFormLayout(input_group)

        self.wire_current = QtWidgets.QDoubleSpinBox()
        self.wire_current.setRange(0.0, 100.0)
        self.wire_current.setSingleStep(0.1)
        self.wire_current.setValue(2.0)
        self.wire_current.setSuffix(" A")
        input_layout.addRow("Load Current:", self.wire_current)

        self.wire_length = QtWidgets.QDoubleSpinBox()
        self.wire_length.setRange(0.0, 1000.0)
        self.wire_length.setSingleStep(1.0)
        self.wire_length.setValue(100.0)
        self.wire_length.setSuffix(" ft")
        input_layout.addRow("Wire Length:", self.wire_length)

        self.wire_voltage = QtWidgets.QDoubleSpinBox()
        self.wire_voltage.setRange(12.0, 48.0)
        self.wire_voltage.setSingleStep(1.0)
        self.wire_voltage.setValue(24.0)
        self.wire_voltage.setSuffix(" V")
        input_layout.addRow("System Voltage:", self.wire_voltage)

        self.wire_max_voltage_drop = QtWidgets.QDoubleSpinBox()
        self.wire_max_voltage_drop.setRange(0.1, 10.0)
        self.wire_max_voltage_drop.setSingleStep(0.1)
        self.wire_max_voltage_drop.setValue(2.4)
        self.wire_max_voltage_drop.setSuffix(" V")
        input_layout.addRow("Max Voltage Drop:", self.wire_max_voltage_drop)

        layout.addWidget(input_group)

        # Calculation button
        calc_layout = QtWidgets.QHBoxLayout()
        self.wire_calc_btn = QtWidgets.QPushButton("Calculate Wire Size")
        self.wire_calc_btn.clicked.connect(self.calculate_wire)
        calc_layout.addWidget(self.wire_calc_btn)
        calc_layout.addStretch()
        layout.addLayout(calc_layout)

        # Results group
        self.wire_results_group = QtWidgets.QGroupBox("Results")
        self.wire_results_group.setVisible(False)
        results_layout = QtWidgets.QFormLayout(self.wire_results_group)

        self.wire_size_result = QtWidgets.QLabel()
        results_layout.addRow("Recommended Wire Size:", self.wire_size_result)

        self.wire_actual_drop_result = QtWidgets.QLabel()
        results_layout.addRow("Actual Voltage Drop:", self.wire_actual_drop_result)

        self.wire_drop_percentage_result = QtWidgets.QLabel()
        results_layout.addRow("Voltage Drop Percentage:", self.wire_drop_percentage_result)

        layout.addWidget(self.wire_results_group)
        layout.addStretch()

        return widget

    def create_coverage_tab(self):
        """Create the coverage calculation tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Input group
        input_group = QtWidgets.QGroupBox("Coverage Calculation Inputs")
        input_layout = QtWidgets.QFormLayout(input_group)

        self.coverage_room_length = QtWidgets.QDoubleSpinBox()
        self.coverage_room_length.setRange(0.0, 100.0)
        self.coverage_room_length.setSingleStep(1.0)
        self.coverage_room_length.setValue(20.0)
        self.coverage_room_length.setSuffix(" ft")
        input_layout.addRow("Room Length:", self.coverage_room_length)

        self.coverage_room_width = QtWidgets.QDoubleSpinBox()
        self.coverage_room_width.setRange(0.0, 100.0)
        self.coverage_room_width.setSingleStep(1.0)
        self.coverage_room_width.setValue(15.0)
        self.coverage_room_width.setSuffix(" ft")
        input_layout.addRow("Room Width:", self.coverage_room_width)

        self.coverage_ceiling_height = QtWidgets.QDoubleSpinBox()
        self.coverage_ceiling_height.setRange(8.0, 20.0)
        self.coverage_ceiling_height.setSingleStep(0.5)
        self.coverage_ceiling_height.setValue(10.0)
        self.coverage_ceiling_height.setSuffix(" ft")
        input_layout.addRow("Ceiling Height:", self.coverage_ceiling_height)

        self.coverage_device_type = QtWidgets.QComboBox()
        self.coverage_device_type.addItems(["Smoke Detector", "Heat Detector", "Strobe", "Speaker"])
        input_layout.addRow("Device Type:", self.coverage_device_type)

        layout.addWidget(input_group)

        # Calculation button
        calc_layout = QtWidgets.QHBoxLayout()
        self.coverage_calc_btn = QtWidgets.QPushButton("Calculate Coverage")
        self.coverage_calc_btn.clicked.connect(self.calculate_coverage)
        calc_layout.addWidget(self.coverage_calc_btn)
        calc_layout.addStretch()
        layout.addLayout(calc_layout)

        # Results group
        self.coverage_results_group = QtWidgets.QGroupBox("Results")
        self.coverage_results_group.setVisible(False)
        results_layout = QtWidgets.QFormLayout(self.coverage_results_group)

        self.coverage_area_result = QtWidgets.QLabel()
        results_layout.addRow("Room Area:", self.coverage_area_result)

        self.coverage_required_devices_result = QtWidgets.QLabel()
        results_layout.addRow("Required Devices:", self.coverage_required_devices_result)

        self.coverage_spacing_result = QtWidgets.QLabel()
        results_layout.addRow("Recommended Spacing:", self.coverage_spacing_result)

        layout.addWidget(self.coverage_results_group)
        layout.addStretch()

        return widget

    def create_load_tab(self):
        """Create the load calculation tab."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Input group
        input_group = QtWidgets.QGroupBox("Load Calculation Inputs")
        input_layout = QtWidgets.QFormLayout(input_group)

        self.load_circuit_type = QtWidgets.QComboBox()
        self.load_circuit_type.addItems(["SLC", "NAC", "Class B", "Class A"])
        input_layout.addRow("Circuit Type:", self.load_circuit_type)

        self.load_voltage = QtWidgets.QDoubleSpinBox()
        self.load_voltage.setRange(12.0, 48.0)
        self.load_voltage.setSingleStep(1.0)
        self.load_voltage.setValue(24.0)
        self.load_voltage.setSuffix(" V")
        input_layout.addRow("System Voltage:", self.load_voltage)

        self.load_max_current = QtWidgets.QDoubleSpinBox()
        self.load_max_current.setRange(0.0, 10.0)
        self.load_max_current.setSingleStep(0.1)
        self.load_max_current.setValue(2.0)
        self.load_max_current.setSuffix(" A")
        input_layout.addRow("Max Circuit Current:", self.load_max_current)

        layout.addWidget(input_group)

        # Devices list
        layout.addWidget(QtWidgets.QLabel("Devices on Circuit:"))
        self.devices_table = QtWidgets.QTableWidget()
        self.devices_table.setColumnCount(4)
        self.devices_table.setHorizontalHeaderLabels(
            ["Device", "Quantity", "Standby (mA)", "Alarm (mA)"]
        )
        self.devices_table.setRowCount(3)

        # Sample devices
        devices = [
            ("Smoke Detector", 10, 0.3, 0.3),
            ("Strobe", 5, 0.0, 2.0),
            ("Pull Station", 2, 0.0, 0.1),
        ]

        for i, (name, qty, standby, alarm) in enumerate(devices):
            self.devices_table.setItem(i, 0, QtWidgets.QTableWidgetItem(name))
            qty_item = QtWidgets.QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
            self.devices_table.setItem(i, 1, qty_item)
            standby_item = QtWidgets.QTableWidgetItem(f"{standby:.1f}")
            standby_item.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
            self.devices_table.setItem(i, 2, standby_item)
            alarm_item = QtWidgets.QTableWidgetItem(f"{alarm:.1f}")
            alarm_item.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
            self.devices_table.setItem(i, 3, alarm_item)

        layout.addWidget(self.devices_table)

        # Calculation button
        calc_layout = QtWidgets.QHBoxLayout()
        self.load_calc_btn = QtWidgets.QPushButton("Calculate Load")
        self.load_calc_btn.clicked.connect(self.calculate_load)
        calc_layout.addWidget(self.load_calc_btn)
        calc_layout.addStretch()
        layout.addLayout(calc_layout)

        # Results group
        self.load_results_group = QtWidgets.QGroupBox("Results")
        self.load_results_group.setVisible(False)
        results_layout = QtWidgets.QFormLayout(self.load_results_group)

        self.load_total_standby_result = QtWidgets.QLabel()
        results_layout.addRow("Total Standby Current:", self.load_total_standby_result)

        self.load_total_alarm_result = QtWidgets.QLabel()
        results_layout.addRow("Total Alarm Current:", self.load_total_alarm_result)

        self.load_percentage_result = QtWidgets.QLabel()
        results_layout.addRow("Load Percentage:", self.load_percentage_result)

        layout.addWidget(self.load_results_group)
        layout.addStretch()

        return widget

    def calculate_battery(self):
        """Calculate battery requirements."""
        standby_current = self.battery_standby_current.value() / 1000.0  # Convert to A
        alarm_current = self.battery_alarm_current.value() / 1000.0  # Convert to A
        backup_time = self.battery_backup_time.value()
        voltage = self.battery_voltage.value()

        # NFPA 72 requires 24 hours standby + 5 minutes alarm
        standby_energy = standby_current * backup_time  # Ah
        alarm_energy = alarm_current * (5.0 / 60.0)  # Ah (5 minutes)
        total_energy = standby_energy + alarm_energy  # Ah

        # Apply safety factor (1.25) and temperature factor (1.2 for 20°C)
        required_capacity = total_energy * 1.25 * 1.2

        # Find standard battery size
        standard_capacities = [18, 24, 31, 36, 40, 50, 60, 70, 80, 100, 120]
        recommended_capacity = next((c for c in standard_capacities if c >= required_capacity), 120)

        # Update results
        self.battery_capacity_result.setText(f"{required_capacity:.1f} Ah")
        self.battery_amp_hours_result.setText(f"{total_energy:.1f} Ah")
        self.battery_recommendation_result.setText(f"{recommended_capacity} Ah battery")
        self.battery_results_group.setVisible(True)

    def calculate_wire(self):
        """Calculate wire size requirements."""
        current = self.wire_current.value()
        length = self.wire_length.value()
        voltage = self.wire_voltage.value()
        max_drop = self.wire_max_voltage_drop.value()

        # Calculate required resistance (Ohm's law: V = I*R)
        max_resistance = max_drop / current if current > 0 else 0

        # Calculate resistance per foot (round trip)
        resistance_per_foot = max_resistance / (length * 2) if length > 0 else 0

        # Convert to resistance per 1000 feet
        resistance_per_1000ft = resistance_per_foot * 1000

        # Match to standard wire gauges (approximate values)
        wire_gauges = {
            "18 AWG": 6.39,
            "16 AWG": 4.02,
            "14 AWG": 2.52,
            "12 AWG": 1.59,
            "10 AWG": 1.00,
            "8 AWG": 0.63,
        }

        # Find suitable wire gauge
        recommended_gauge = "8 AWG"  # Default to largest
        for gauge, resistance in sorted(wire_gauges.items()):
            if resistance <= resistance_per_1000ft:
                recommended_gauge = gauge
                break

        # Calculate actual voltage drop with selected wire
        actual_resistance_per_1000ft = wire_gauges.get(recommended_gauge, 0.63)
        actual_resistance = (actual_resistance_per_1000ft / 1000) * (length * 2)
        actual_drop = current * actual_resistance
        drop_percentage = (actual_drop / voltage) * 100 if voltage > 0 else 0

        # Update results
        self.wire_size_result.setText(recommended_gauge)
        self.wire_actual_drop_result.setText(f"{actual_drop:.2f} V")
        self.wire_drop_percentage_result.setText(f"{drop_percentage:.1f}%")
        self.wire_results_group.setVisible(True)

    def calculate_coverage(self):
        """Calculate device coverage requirements."""
        length = self.coverage_room_length.value()
        width = self.coverage_room_width.value()
        height = self.coverage_ceiling_height.value()
        device_type = self.coverage_device_type.currentText()

        # Calculate room area
        area = length * width

        # Determine spacing based on device type and ceiling height
        if device_type == "Smoke Detector":
            # NFPA 72: Max 30 ft spacing for smooth ceilings up to 10 ft
            spacing = (
                30.0 if height <= 10.0 else 30.0 * (10.0 / height)
            )  # Adjust for higher ceilings
        elif device_type == "Heat Detector":
            # NFPA 72: Max 50 ft spacing
            spacing = 50.0
        elif device_type == "Strobe":
            # NFPA 72: Depends on candela rating
            spacing = 50.0  # Default for typical strobe
        else:  # Speaker
            spacing = 100.0  # Typical spacing for speakers

        # Calculate required devices (grid pattern)
        devices_x = math.ceil(length / spacing) + 1
        devices_y = math.ceil(width / spacing) + 1
        required_devices = devices_x * devices_y

        # Update results
        self.coverage_area_result.setText(f"{area:.0f} sq ft")
        self.coverage_required_devices_result.setText(str(required_devices))
        self.coverage_spacing_result.setText(f"{spacing:.0f} ft")
        self.coverage_results_group.setVisible(True)

    def calculate_load(self):
        """Calculate circuit load."""
        voltage = self.load_voltage.value()
        max_current = self.load_max_current.value()

        # Calculate total currents
        total_standby = 0.0
        total_alarm = 0.0

        for row in range(self.devices_table.rowCount()):
            qty_item = self.devices_table.item(row, 1)
            standby_item = self.devices_table.item(row, 2)
            alarm_item = self.devices_table.item(row, 3)

            if qty_item and standby_item and alarm_item:
                try:
                    qty = float(qty_item.text() if qty_item else "0")
                    standby = float(standby_item.text() if standby_item else "0")
                    alarm = float(alarm_item.text() if alarm_item else "0")

                    total_standby += qty * standby
                    total_alarm += qty * alarm
                except ValueError:
                    continue

        # Convert mA to A
        total_standby_a = total_standby / 1000.0
        total_alarm_a = total_alarm / 1000.0

        # Calculate load percentage
        load_percentage = (
            (max(total_standby_a, total_alarm_a) / max_current * 100) if max_current > 0 else 0
        )

        # Update results
        self.load_total_standby_result.setText(f"{total_standby_a:.2f} A ({total_standby:.0f} mA)")
        self.load_total_alarm_result.setText(f"{total_alarm_a:.2f} A ({total_alarm:.0f} mA)")
        self.load_percentage_result.setText(f"{load_percentage:.1f}%")
        self.load_results_group.setVisible(True)
