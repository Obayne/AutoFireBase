from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QPushButton
from PySide6.QtCore import Qt

from app import catalog


class BomReportDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bill of Materials Report")
        self.setMinimumSize(900, 700)

        layout = QVBoxLayout(self)

        # Header with project info
        header_group = QGroupBox("Project Information")
        header_layout = QVBoxLayout(header_group)

        # Project name and date
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("Project:"))
        self.project_name = QLabel("Current Project")
        project_layout.addWidget(self.project_name)
        project_layout.addStretch()

        project_layout.addWidget(QLabel("Date:"))
        self.report_date = QLabel(QtCore.QDate.currentDate().toString("MM/dd/yyyy"))
        project_layout.addWidget(self.report_date)

        header_layout.addLayout(project_layout)
        layout.addWidget(header_group)

        # Main content tabs
        self.tabs = QtWidgets.QTabWidget()

        # Devices Tab
        self.tabs.addTab(self._create_devices_tab(), "Devices")

        # Materials Tab
        self.tabs.addTab(self._create_materials_tab(), "Materials")

        # Summary Tab
        self.tabs.addTab(self._create_summary_tab(), "Summary")

        layout.addWidget(self.tabs)

        # Export buttons
        button_layout = QHBoxLayout()

        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.clicked.connect(self._export_csv)
        button_layout.addWidget(export_csv_btn)

        export_pdf_btn = QPushButton("Export PDF")
        export_pdf_btn.clicked.connect(self._export_pdf)
        button_layout.addWidget(export_pdf_btn)

        button_layout.addStretch()

        ok_btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        ok_btn.accepted.connect(self.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # Load data
        self._load_bom_data()

    def _create_devices_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Devices table
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(6)
        self.devices_table.setHorizontalHeaderLabels([
            "Device Type", "Manufacturer", "Model", "Quantity", "Unit Cost", "Total Cost"
        ])
        self.devices_table.horizontalHeader().setStretchLastSection(True)
        self.devices_table.setAlternatingRowColors(True)
        self.devices_table.setSortingEnabled(True)

        layout.addWidget(self.devices_table)

        # Device totals
        totals_group = QGroupBox("Device Totals")
        totals_layout = QVBoxLayout(totals_group)

        self.device_totals_text = QLabel()
        totals_layout.addWidget(self.device_totals_text)

        layout.addWidget(totals_group)

        return widget

    def _create_materials_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Materials table
        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(4)
        self.materials_table.setHorizontalHeaderLabels([
            "Material Type", "Description", "Quantity", "Estimated Cost"
        ])
        self.materials_table.horizontalHeader().setStretchLastSection(True)
        self.materials_table.setAlternatingRowColors(True)

        layout.addWidget(self.materials_table)

        # Materials note
        note_label = QLabel("Note: Material quantities are estimates based on typical fire alarm system requirements.\nActual quantities should be calculated based on specific site conditions and NFPA requirements.")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(note_label)

        return widget

    def _create_summary_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Summary information
        summary_group = QGroupBox("Project Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.summary_text = QLabel()
        self.summary_text.setWordWrap(True)
        summary_layout.addWidget(self.summary_text)

        layout.addWidget(summary_group)

        # Cost breakdown
        cost_group = QGroupBox("Cost Breakdown")
        cost_layout = QVBoxLayout(cost_group)

        self.cost_breakdown_text = QLabel()
        cost_layout.addWidget(self.cost_breakdown_text)

        layout.addWidget(cost_group)

        return widget

    def _load_bom_data(self):
        # Get device data from parent window if available
        parent = self.parent()
        devices = None
        if parent and hasattr(parent, 'devices_all'):
            try:
                devices = getattr(parent, 'devices_all', None)
            except:
                devices = None

        if not devices:
            devices = catalog.load_catalog()

        # Load device BOM
        self._load_device_bom(devices)

        # Load materials
        self._load_materials_bom(devices)

        # Load summary
        self._load_summary()

    def _load_device_bom(self, devices):
        # Group devices by type, manufacturer, model
        device_groups = {}

        for device in devices:
            key = (
                device.get('type', 'Unknown'),
                device.get('manufacturer', 'Unknown'),
                device.get('model', 'Unknown')
            )

            cost = device.get('cost', 0) or 0

            if key not in device_groups:
                device_groups[key] = {
                    'quantity': 0,
                    'unit_cost': cost,
                    'total_cost': 0
                }

            device_groups[key]['quantity'] += 1
            device_groups[key]['total_cost'] += cost

        # Populate table
        self.devices_table.setRowCount(len(device_groups))

        total_quantity = 0
        total_cost = 0

        for row, ((device_type, manufacturer, model), data) in enumerate(device_groups.items()):
            self.devices_table.setItem(row, 0, QTableWidgetItem(device_type))
            self.devices_table.setItem(row, 1, QTableWidgetItem(manufacturer))
            self.devices_table.setItem(row, 2, QTableWidgetItem(model))
            self.devices_table.setItem(row, 3, QTableWidgetItem(str(data['quantity'])))
            self.devices_table.setItem(row, 4, QTableWidgetItem(f"${data['unit_cost']:.2f}"))
            self.devices_table.setItem(row, 5, QTableWidgetItem(f"${data['total_cost']:.2f}"))

            total_quantity += data['quantity']
            total_cost += data['total_cost']

        # Device totals
        self.device_totals_text.setText(f"""
Total Device Types: {len(device_groups)}
Total Quantity: {total_quantity}
Total Cost: ${total_cost:.2f}
""".strip())

    def _load_materials_bom(self, devices):
        # Estimate materials based on device counts
        materials = []

        # Count device types
        device_counts = {}
        for device in devices:
            device_type = device.get('type', 'Unknown')
            device_counts[device_type] = device_counts.get(device_type, 0) + 1

        # Estimate conduit and wire
        total_devices = len(devices)
        estimated_conduit_feet = total_devices * 50  # Rough estimate: 50 ft per device
        estimated_wire_feet = total_devices * 100    # Rough estimate: 100 ft per device

        materials.extend([
            ("Conduit", "EMT Conduit (3/4\")", f"{estimated_conduit_feet} ft", f"${estimated_conduit_feet * 2.50:.2f}"),
            ("Wire", "Fire Alarm Cable (18 AWG)", f"{estimated_wire_feet} ft", f"${estimated_wire_feet * 0.75:.2f}"),
            ("Boxes", "Electrical Boxes (4\")", f"{total_devices // 2}", f"${(total_devices // 2) * 8.50:.2f}"),
            ("Connectors", "Wire Nuts & Connectors", f"{total_devices * 3}", f"${total_devices * 3 * 0.25:.2f}"),
        ])

        # Add panel materials if FACP devices exist
        facp_count = device_counts.get('Fire Alarm Control Panel', 0)
        if facp_count > 0:
            materials.extend([
                ("Panel", "FACP Cabinet", f"{facp_count}", f"${facp_count * 2500:.2f}"),
                ("Battery", "Backup Batteries (12V)", f"{facp_count * 2}", f"${facp_count * 2 * 150:.2f}"),
            ])

        # Populate table
        self.materials_table.setRowCount(len(materials))

        for row, (mat_type, description, quantity, cost) in enumerate(materials):
            self.materials_table.setItem(row, 0, QTableWidgetItem(mat_type))
            self.materials_table.setItem(row, 1, QTableWidgetItem(description))
            self.materials_table.setItem(row, 2, QTableWidgetItem(quantity))
            self.materials_table.setItem(row, 3, QTableWidgetItem(cost))

    def _load_summary(self):
        # Get data from other tabs
        device_count = self.devices_table.rowCount()
        material_count = self.materials_table.rowCount()

        # Calculate totals
        device_total = 0
        material_total = 0

        for row in range(device_count):
            item = self.devices_table.item(row, 5)
            if item:
                cost_text = item.text()
                device_total += float(cost_text.replace('$', ''))

        for row in range(material_count):
            item = self.materials_table.item(row, 3)
            if item:
                cost_text = item.text()
                material_total += float(cost_text.replace('$', ''))

        grand_total = device_total + material_total

        # Summary text
        summary = f"""
This Bill of Materials includes all devices and estimated materials for the fire alarm system.

Device Types: {device_count}
Material Items: {material_count}

Note: Material quantities are estimates only. Final quantities should be determined by:
- Actual site survey and measurements
- Local building codes and NFPA requirements
- Specific manufacturer recommendations
- Electrical contractor assessment
"""

        self.summary_text.setText(summary.strip())

        # Cost breakdown
        cost_breakdown = f"""
Device Costs: ${device_total:.2f}
Material Costs: ${material_total:.2f}
Grand Total: ${grand_total:.2f}

Note: Does not include labor, permits, or installation costs.
"""
        self.cost_breakdown_text.setText(cost_breakdown.strip())

    def _export_csv(self):
        """Export BOM data to CSV file"""
        # TODO: Implement CSV export
        QtWidgets.QMessageBox.information(self, "Export CSV", "CSV export will be implemented here.")

    def _export_pdf(self):
        """Export BOM data to PDF file"""
        # TODO: Implement PDF export
        QtWidgets.QMessageBox.information(self, "Export PDF", "PDF export will be implemented here.")