import csv
import json

from PySide6 import QtCore, QtWidgets


class BomReportDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bill of Materials Report")
        self.setModal(True)
        self.resize(800, 600)

        self.main_window = parent
        self.bom_data = []

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Bill of Materials")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Report options
        options_group = QtWidgets.QGroupBox("Report Options")
        options_layout = QtWidgets.QFormLayout(options_group)

        self.group_by_combo = QtWidgets.QComboBox()
        self.group_by_combo.addItems(["Category", "Manufacturer", "Device Type"])
        options_layout.addRow("Group By:", self.group_by_combo)

        self.include_quantities = QtWidgets.QCheckBox("Include Quantities")
        self.include_quantities.setChecked(True)
        options_layout.addRow("Quantities:", self.include_quantities)

        self.include_specs = QtWidgets.QCheckBox("Include Specifications")
        self.include_specs.setChecked(True)
        options_layout.addRow("Specifications:", self.include_specs)

        layout.addWidget(options_group)

        # BOM table
        self.bom_table = QtWidgets.QTableWidget()
        self.bom_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        layout.addWidget(self.bom_table)

        # Summary
        summary_layout = QtWidgets.QHBoxLayout()
        self.total_devices_label = QtWidgets.QLabel("Total Devices: 0")
        self.total_unique_label = QtWidgets.QLabel("Unique Devices: 0")
        summary_layout.addWidget(self.total_devices_label)
        summary_layout.addWidget(self.total_unique_label)
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
        """Generate the BOM report."""
        # Collect device data from the main window
        devices = []
        if self.main_window:
            for item in self.main_window.layer_devices.childItems():
                if hasattr(item, "name") and hasattr(item, "symbol"):
                    device = {
                        "name": item.name,
                        "symbol": item.symbol,
                        "manufacturer": getattr(item, "manufacturer", ""),
                        "part_number": getattr(item, "part_number", ""),
                        "category": getattr(item, "system_category", "Unknown"),
                        "type": getattr(item, "type", "Unknown"),
                        "specs": getattr(item, "specs", {}),
                    }
                    devices.append(device)

        # Group devices
        grouped_devices = {}
        group_by = self.group_by_combo.currentText().lower()

        for device in devices:
            if group_by == "category":
                key = device.get("category", "Unknown")
            elif group_by == "manufacturer":
                key = device.get("manufacturer", "Unknown")
            else:  # device type
                key = device.get("type", "Unknown")

            if key not in grouped_devices:
                grouped_devices[key] = []
            grouped_devices[key].append(device)

        # Count quantities
        bom_data = []
        total_devices = 0
        unique_devices = set()

        for group, group_devices in grouped_devices.items():
            # Group by device name and part number
            device_counts = {}
            for device in group_devices:
                key = (device["name"], device["part_number"])
                unique_devices.add(key)
                if key not in device_counts:
                    device_counts[key] = {
                        "name": device["name"],
                        "symbol": device["symbol"],
                        "manufacturer": device["manufacturer"],
                        "part_number": device["part_number"],
                        "category": device["category"],
                        "type": device["type"],
                        "specs": device["specs"],
                        "count": 0,
                    }
                device_counts[key]["count"] += 1
                total_devices += 1

            # Add to BOM data
            for device_info in device_counts.values():
                bom_data.append(device_info)

        # Sort by group, then by device name
        bom_data.sort(key=lambda x: (x.get(group_by, ""), x["name"]))

        # Update table
        self.update_table(bom_data)

        # Update summary
        self.total_devices_label.setText(f"Total Devices: {total_devices}")
        self.total_unique_label.setText(f"Unique Devices: {len(unique_devices)}")

        # Store data for export
        self.bom_data = bom_data

    def update_table(self, bom_data):
        """Update the BOM table with data."""
        # Set up columns based on options
        columns = ["Name", "Symbol", "Manufacturer", "Part Number", "Quantity"]
        if self.include_specs.isChecked():
            columns.extend(["Category", "Type"])

        self.bom_table.setColumnCount(len(columns))
        self.bom_table.setHorizontalHeaderLabels(columns)
        self.bom_table.setRowCount(len(bom_data))

        # Populate table
        for row, device in enumerate(bom_data):
            self.bom_table.setItem(row, 0, QtWidgets.QTableWidgetItem(device["name"]))
            self.bom_table.setItem(row, 1, QtWidgets.QTableWidgetItem(device["symbol"]))
            self.bom_table.setItem(row, 2, QtWidgets.QTableWidgetItem(device["manufacturer"]))
            self.bom_table.setItem(row, 3, QtWidgets.QTableWidgetItem(device["part_number"]))
            qty_item = QtWidgets.QTableWidgetItem(str(device["count"]))
            qty_item.setTextAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
            self.bom_table.setItem(row, 4, qty_item)

            if self.include_specs.isChecked():
                self.bom_table.setItem(row, 5, QtWidgets.QTableWidgetItem(device["category"]))
                self.bom_table.setItem(row, 6, QtWidgets.QTableWidgetItem(device["type"]))

        # Resize columns to content
        self.bom_table.resizeColumnsToContents()

    def export_csv(self):
        """Export BOM to CSV file."""
        if not self.bom_data:
            QtWidgets.QMessageBox.information(self, "Export CSV", "No data to export.")
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export BOM to CSV", "", "CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Name", "Symbol", "Manufacturer", "Part Number", "Quantity"]
                if self.include_specs.isChecked():
                    fieldnames.extend(["Category", "Type", "Specifications"])

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for device in self.bom_data:
                    row = {
                        "Name": device["name"],
                        "Symbol": device["symbol"],
                        "Manufacturer": device["manufacturer"],
                        "Part Number": device["part_number"],
                        "Quantity": device["count"],
                    }
                    if self.include_specs.isChecked():
                        row["Category"] = device["category"]
                        row["Type"] = device["type"]
                        row["Specifications"] = (
                            json.dumps(device["specs"]) if device["specs"] else ""
                        )

                    writer.writerow(row)

            QtWidgets.QMessageBox.information(
                self, "Export CSV", f"BOM exported successfully to {file_path}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to export BOM: {str(e)}")

    def export_pdf(self):
        """Export BOM to PDF file."""
        QtWidgets.QMessageBox.information(
            self, "Export PDF", "PDF export functionality would be implemented here."
        )
