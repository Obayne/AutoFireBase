from PySide6 import QtWidgets


class CircuitPropertiesDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Circuit Properties")
        self.setModal(True)
        self.resize(500, 400)

        self.main_window = parent
        self.circuit_data = {}

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Circuit Properties")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Circuit information
        info_group = QtWidgets.QGroupBox("Circuit Information")
        info_layout = QtWidgets.QFormLayout(info_group)

        self.circuit_name_edit = QtWidgets.QLineEdit()
        info_layout.addRow("Circuit Name:", self.circuit_name_edit)

        self.panel_combo = QtWidgets.QComboBox()
        info_layout.addRow("Panel:", self.panel_combo)

        self.circuit_type_combo = QtWidgets.QComboBox()
        self.circuit_type_combo.addItems(["SLC", "NAC", "Class B", "Class A"])
        info_layout.addRow("Circuit Type:", self.circuit_type_combo)

        layout.addWidget(info_group)

        # Electrical properties
        electrical_group = QtWidgets.QGroupBox("Electrical Properties")
        electrical_layout = QtWidgets.QFormLayout(electrical_group)

        self.voltage_spin = QtWidgets.QDoubleSpinBox()
        self.voltage_spin.setRange(12.0, 48.0)
        self.voltage_spin.setSingleStep(1.0)
        self.voltage_spin.setValue(24.0)
        electrical_layout.addRow("Voltage (V):", self.voltage_spin)

        self.max_current_spin = QtWidgets.QDoubleSpinBox()
        self.max_current_spin.setRange(0.0, 10.0)
        self.max_current_spin.setSingleStep(0.1)
        self.max_current_spin.setValue(2.0)
        self.max_current_spin.setSuffix(" A")
        electrical_layout.addRow("Max Current:", self.max_current_spin)

        self.wire_gauge_combo = QtWidgets.QComboBox()
        self.populate_wire_gauges()
        electrical_layout.addRow("Wire Gauge:", self.wire_gauge_combo)

        self.wire_length_spin = QtWidgets.QDoubleSpinBox()
        self.wire_length_spin.setRange(0.0, 1000.0)
        self.wire_length_spin.setSingleStep(1.0)
        self.wire_length_spin.setValue(100.0)
        self.wire_length_spin.setSuffix(" ft")
        electrical_layout.addRow("Wire Length:", self.wire_length_spin)

        self.resistance_label = QtWidgets.QLabel("0.0 Ω")
        electrical_layout.addRow("Total Resistance:", self.resistance_label)

        layout.addWidget(electrical_group)

        # Load calculation
        load_group = QtWidgets.QGroupBox("Load Calculation")
        load_layout = QtWidgets.QFormLayout(load_group)

        self.total_devices_label = QtWidgets.QLabel("0")
        load_layout.addRow("Total Devices:", self.total_devices_label)

        self.total_current_label = QtWidgets.QLabel("0.0 A")
        load_layout.addRow("Total Current:", self.total_current_label)

        self.load_percentage_label = QtWidgets.QLabel("0%")
        load_layout.addRow("Load Percentage:", self.load_percentage_label)

        layout.addWidget(load_group)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.calculate_btn = QtWidgets.QPushButton("Calculate")
        self.calculate_btn.clicked.connect(self.calculate_load)
        button_layout.addWidget(self.calculate_btn)
        button_layout.addStretch()

        self.ok_btn = QtWidgets.QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # Connect signals
        self.wire_gauge_combo.currentTextChanged.connect(self.update_resistance)
        self.wire_length_spin.valueChanged.connect(self.update_resistance)

        # Populate panels
        self.populate_panels()

        # Initial calculations
        self.update_resistance()
        self.calculate_load()

    def populate_panels(self):
        """Populate the panel combo box with available panels."""
        # In a real application, this would come from the connections tree or database
        self.panel_combo.addItems(["Panel 1", "Panel 2", "Panel 3"])

    def populate_wire_gauges(self):
        """Populate the wire gauge combo box with available gauges."""
        # Sample wire gauges - in a real application, this would come from the database
        gauges = ["18/2", "16/2", "14/2", "12/2"]
        self.wire_gauge_combo.addItems(gauges)

    def update_resistance(self):
        """Update the resistance calculation based on wire gauge and length."""
        gauge = self.wire_gauge_combo.currentText()
        length = self.wire_length_spin.value()

        # Resistance per 1000 feet for common wire gauges (approximate values)
        resistance_per_1000ft = {"18/2": 6.39, "16/2": 4.02, "14/2": 2.52, "12/2": 1.59}

        resistance_per_ft = resistance_per_1000ft.get(gauge, 0.0) / 1000.0
        total_resistance = resistance_per_ft * length * 2  # Round trip
        self.resistance_label.setText(f"{total_resistance:.3f} Ω")

    def calculate_load(self):
        """Calculate the circuit load."""
        # Sample calculation - in a real application, this would be based on actual devices
        total_devices = 25
        total_current = 1.2  # Amps
        max_current = self.max_current_spin.value()

        self.total_devices_label.setText(str(total_devices))
        self.total_current_label.setText(f"{total_current:.1f} A")

        if max_current > 0:
            load_percentage = (total_current / max_current) * 100
            self.load_percentage_label.setText(f"{load_percentage:.1f}%")

            # Color code the load percentage
            if load_percentage > 80:
                self.load_percentage_label.setStyleSheet("color: red; font-weight: bold;")
            elif load_percentage > 60:
                self.load_percentage_label.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.load_percentage_label.setStyleSheet("color: green;")
        else:
            self.load_percentage_label.setText("0%")
            self.load_percentage_label.setStyleSheet("")

    def get_circuit_data(self):
        """Return the circuit data."""
        return {
            "name": self.circuit_name_edit.text(),
            "panel": self.panel_combo.currentText(),
            "type": self.circuit_type_combo.currentText(),
            "voltage": self.voltage_spin.value(),
            "max_current": self.max_current_spin.value(),
            "wire_gauge": self.wire_gauge_combo.currentText(),
            "wire_length": self.wire_length_spin.value(),
            "total_resistance": float(self.resistance_label.text().replace(" Ω", "")),
            "total_devices": int(self.total_devices_label.text()),
            "total_current": float(self.total_current_label.text().replace(" A", "")),
            "load_percentage": float(self.load_percentage_label.text().replace("%", "")),
        }
