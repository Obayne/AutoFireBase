import csv

from PySide6 import QtWidgets


class DeviceScheduleReportDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Device Schedule Report")
        self.setModal(True)
        self.resize(1000, 700)

        self.main_window = parent
        self.device_data = []

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Device Schedule Report")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Report options
        options_group = QtWidgets.QGroupBox("Report Options")
        options_layout = QtWidgets.QGridLayout(options_group)

        # Columns to include
        self.include_location = QtWidgets.QCheckBox("Location")
        self.include_location.setChecked(True)
        options_layout.addWidget(self.include_location, 0, 0)

        self.include_device = QtWidgets.QCheckBox("Device")
        self.include_device.setChecked(True)
        options_layout.addWidget(self.include_device, 0, 1)

        self.include_address = QtWidgets.QCheckBox("Address")
        self.include_address.setChecked(True)
        options_layout.addWidget(self.include_address, 0, 2)

        self.include_circuit = QtWidgets.QCheckBox("Circuit")
        self.include_circuit.setChecked(True)
        options_layout.addWidget(self.include_circuit, 0, 3)

        self.include_zone = QtWidgets.QCheckBox("Zone")
        options_layout.addWidget(self.include_zone, 1, 0)

        self.include_room = QtWidgets.QCheckBox("Room")
        options_layout.addWidget(self.include_room, 1, 1)

        self.include_floor = QtWidgets.QCheckBox("Floor")
        options_layout.addWidget(self.include_floor, 1, 2)

        self.include_area = QtWidgets.QCheckBox("Area")
        options_layout.addWidget(self.include_area, 1, 3)

        # Sort options
        sort_label = QtWidgets.QLabel("Sort By:")
        self.sort_combo = QtWidgets.QComboBox()
        self.sort_combo.addItems(["Location", "Device", "Address", "Circuit"])
        self.sort_combo.setCurrentText("Location")

        options_layout.addWidget(sort_label, 2, 0)
        options_layout.addWidget(self.sort_combo, 2, 1)

        layout.addWidget(options_group)

        # Device schedule table
        self.schedule_table = QtWidgets.QTableWidget()
        self.schedule_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        layout.addWidget(self.schedule_table)

        # Summary
        summary_layout = QtWidgets.QHBoxLayout()
        self.total_devices_label = QtWidgets.QLabel("Total Devices: 0")
        summary_layout.addWidget(self.total_devices_label)
        summary_layout.addStretch()
        layout.addLayout(summary_layout)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.export_csv_btn = QtWidgets.QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)
        button_layout.addWidget(self.export_csv_btn)

        self.export_pdf_btn = QtWidgets.QPushButton("Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(self.export_pdf_btn)

        button_layout.addStretch()

        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_report)
        button_layout.addWidget(self.refresh_btn)

        self.ok_btn = QtWidgets.QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

        # Generate initial report
        self.refresh_report()

    def refresh_report(self):
        """Generate the device schedule report."""
        # Collect device data from the main window
        devices = []
        if self.main_window:
            for item in self.main_window.layer_devices.childItems():
                if hasattr(item, "name") and hasattr(item, "symbol"):
                    device = {
                        "location": getattr(item, "location", ""),
                        "device": f"{item.name} ({item.symbol})",
                        "address": getattr(item, "address", ""),
                        "circuit": getattr(item, "circuit", ""),
                        "zone": getattr(item, "zone", ""),
                        "room": getattr(item, "room", ""),
                        "floor": getattr(item, "floor", ""),
                        "area": getattr(item, "area", ""),
                        "manufacturer": getattr(item, "manufacturer", ""),
                        "part_number": getattr(item, "part_number", ""),
                        "x": getattr(item, "x", 0),
                        "y": getattr(item, "y", 0),
                    }
                    devices.append(device)

        # Sort devices
        sort_by = self.sort_combo.currentText().lower()
        if sort_by == "location":
            devices.sort(key=lambda x: (x["floor"], x["area"], x["room"], x["x"], x["y"]))
        elif sort_by == "device":
            devices.sort(key=lambda x: x["device"])
        elif sort_by == "address":
            devices.sort(key=lambda x: x["address"])
        elif sort_by == "circuit":
            devices.sort(key=lambda x: x["circuit"])

        # Update table
        self.update_table(devices)

        # Update summary
        self.total_devices_label.setText(f"Total Devices: {len(devices)}")

        # Store data for export
        self.device_data = devices

    def update_table(self, devices):
        """Update the schedule table with data."""
        # Set up columns based on options
        columns = []
        if self.include_location.isChecked():
            columns.extend(["Floor", "Area", "Room", "Location"])
        if self.include_device.isChecked():
            columns.append("Device")
        if self.include_address.isChecked():
            columns.append("Address")
        if self.include_circuit.isChecked():
            columns.append("Circuit")
        if self.include_zone.isChecked():
            columns.append("Zone")

        self.schedule_table.setColumnCount(len(columns))
        self.schedule_table.setHorizontalHeaderLabels(columns)
        self.schedule_table.setRowCount(len(devices))

        # Populate table
        for row, device in enumerate(devices):
            col = 0
            if self.include_location.isChecked():
                self.schedule_table.setItem(row, col, QtWidgets.QTableWidgetItem(device["floor"]))
                col += 1
                self.schedule_table.setItem(row, col, QtWidgets.QTableWidgetItem(device["area"]))
                col += 1
                self.schedule_table.setItem(row, col, QtWidgets.QTableWidgetItem(device["room"]))
                col += 1
                self.schedule_table.setItem(
                    row, col, QtWidgets.QTableWidgetItem(f"({device['x']:.1f}, {device['y']:.1f})")
                )
                col += 1
            if self.include_device.isChecked():
                self.schedule_table.setItem(row, col, QtWidgets.QTableWidgetItem(device["device"]))
                col += 1
            if self.include_address.isChecked():
                self.schedule_table.setItem(row, col, QtWidgets.QTableWidgetItem(device["address"]))
                col += 1
            if self.include_circuit.isChecked():
                self.schedule_table.setItem(row, col, QtWidgets.QTableWidgetItem(device["circuit"]))
                col += 1
            if self.include_zone.isChecked():
                self.schedule_table.setItem(row, col, QtWidgets.QTableWidgetItem(device["zone"]))
                col += 1

        # Resize columns to content
        self.schedule_table.resizeColumnsToContents()

    def export_csv(self):
        """Export device schedule to CSV file."""
        if not self.device_data:
            QtWidgets.QMessageBox.information(self, "Export CSV", "No data to export.")
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Device Schedule to CSV", "", "CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                # Build fieldnames based on selected options
                fieldnames = []
                if self.include_location.isChecked():
                    fieldnames.extend(["Floor", "Area", "Room", "X", "Y"])
                if self.include_device.isChecked():
                    fieldnames.extend(["Device", "Manufacturer", "Part Number"])
                if self.include_address.isChecked():
                    fieldnames.append("Address")
                if self.include_circuit.isChecked():
                    fieldnames.append("Circuit")
                if self.include_zone.isChecked():
                    fieldnames.append("Zone")

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for device in self.device_data:
                    row = {}
                    if self.include_location.isChecked():
                        row["Floor"] = device["floor"]
                        row["Area"] = device["area"]
                        row["Room"] = device["room"]
                        row["X"] = device["x"]
                        row["Y"] = device["y"]
                    if self.include_device.isChecked():
                        row["Device"] = device["device"]
                        row["Manufacturer"] = device["manufacturer"]
                        row["Part Number"] = device["part_number"]
                    if self.include_address.isChecked():
                        row["Address"] = device["address"]
                    if self.include_circuit.isChecked():
                        row["Circuit"] = device["circuit"]
                    if self.include_zone.isChecked():
                        row["Zone"] = device["zone"]

                    writer.writerow(row)

            QtWidgets.QMessageBox.information(
                self, "Export CSV", f"Device schedule exported successfully to {file_path}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Export Error", f"Failed to export device schedule: {str(e)}"
            )

    def export_pdf(self):
        """Export device schedule to PDF file."""
        QtWidgets.QMessageBox.information(
            self, "Export PDF", "PDF export functionality would be implemented here."
        )
