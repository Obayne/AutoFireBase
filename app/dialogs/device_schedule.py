from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QPushButton, QComboBox
from PySide6.QtCore import Qt

from app import catalog


class DeviceScheduleReportDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Device Schedule Report")
        self.setMinimumSize(1000, 700)

        layout = QVBoxLayout(self)

        # Header with filters
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("Device Type:"))
        self.device_type_filter = QComboBox()
        self.device_type_filter.addItem("All Types")
        self.device_type_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.device_type_filter)

        filter_layout.addWidget(QLabel("Circuit:"))
        self.circuit_filter = QComboBox()
        self.circuit_filter.addItem("All Circuits")
        self.circuit_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.circuit_filter)

        filter_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_device_schedule)
        filter_layout.addWidget(refresh_btn)

        layout.addWidget(filter_group)

        # Main content
        self.tabs = QtWidgets.QTabWidget()

        # Device Schedule Tab
        self.tabs.addTab(self._create_schedule_tab(), "Device Schedule")

        # Location Map Tab
        self.tabs.addTab(self._create_location_tab(), "Location Map")

        # Statistics Tab
        self.tabs.addTab(self._create_statistics_tab(), "Statistics")

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
        self._load_device_schedule()

    def _create_schedule_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Device schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(8)
        self.schedule_table.setHorizontalHeaderLabels([
            "Device ID", "Type", "Location", "Circuit", "Zone", "Coverage", "Status", "Notes"
        ])
        self.schedule_table.horizontalHeader().setStretchLastSection(True)
        self.schedule_table.setAlternatingRowColors(True)
        self.schedule_table.setSortingEnabled(True)

        layout.addWidget(self.schedule_table)

        return widget

    def _create_location_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Location map (text-based for now)
        self.location_text = QtWidgets.QTextEdit()
        self.location_text.setReadOnly(True)
        layout.addWidget(self.location_text)

        return widget

    def _create_statistics_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Statistics display
        stats_group = QGroupBox("Device Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_text = QLabel()
        self.stats_text.setWordWrap(True)
        stats_layout.addWidget(self.stats_text)

        layout.addWidget(stats_group)

        # Coverage analysis
        coverage_group = QGroupBox("Coverage Analysis")
        coverage_layout = QVBoxLayout(coverage_group)

        self.coverage_text = QLabel()
        self.coverage_text.setWordWrap(True)
        coverage_layout.addWidget(self.coverage_text)

        layout.addWidget(coverage_group)

        return widget

    def _load_device_schedule(self):
        # Get placed devices from parent window
        parent = self.parent()
        placed_devices = []

        if parent and hasattr(parent, 'scene'):
            try:
                scene = getattr(parent, 'scene', None)
                if scene:
                    # Look for device items in the scene
                    for item in scene.items():
                        if hasattr(item, 'device_data') and item.device_data:
                            placed_devices.append({
                                'item': item,
                                'data': item.device_data,
                                'position': item.pos()
                            })
            except:
                pass

        # Update filters
        self._update_filters(placed_devices)

        # Load schedule table
        self._load_schedule_table(placed_devices)

        # Load location map
        self._load_location_map(placed_devices)

        # Load statistics
        self._load_statistics(placed_devices)

    def _update_filters(self, devices):
        # Update device type filter
        device_types = set()
        circuits = set()

        for device in devices:
            device_types.add(device['data'].get('type', 'Unknown'))
            circuits.add(device['data'].get('circuit', 'Not Assigned'))

        self.device_type_filter.clear()
        self.device_type_filter.addItem("All Types")
        for dt in sorted(device_types):
            self.device_type_filter.addItem(dt)

        self.circuit_filter.clear()
        self.circuit_filter.addItem("All Circuits")
        for circuit in sorted(circuits):
            self.circuit_filter.addItem(circuit)

    def _load_schedule_table(self, devices):
        # Apply filters
        filtered_devices = self._apply_device_filters(devices)

        # Populate table
        self.schedule_table.setRowCount(len(filtered_devices))

        for row, device in enumerate(filtered_devices):
            data = device['data']
            pos = device['position']

            # Device ID (use position as identifier for now)
            device_id = f"{pos.x():.1f}, {pos.y():.1f}"

            # Device info
            device_type = data.get('type', 'Unknown')
            location = f"X: {pos.x():.1f}, Y: {pos.y():.1f}"
            circuit = data.get('circuit', 'Not Assigned')
            zone = data.get('zone', 'Not Assigned')
            coverage = self._calculate_coverage(device)
            status = data.get('status', 'Active')
            notes = data.get('notes', '')

            self.schedule_table.setItem(row, 0, QTableWidgetItem(device_id))
            self.schedule_table.setItem(row, 1, QTableWidgetItem(device_type))
            self.schedule_table.setItem(row, 2, QTableWidgetItem(location))
            self.schedule_table.setItem(row, 3, QTableWidgetItem(circuit))
            self.schedule_table.setItem(row, 4, QTableWidgetItem(zone))
            self.schedule_table.setItem(row, 5, QTableWidgetItem(coverage))
            self.schedule_table.setItem(row, 6, QTableWidgetItem(status))
            self.schedule_table.setItem(row, 7, QTableWidgetItem(notes))

    def _apply_device_filters(self, devices):
        device_type_filter = self.device_type_filter.currentText()
        circuit_filter = self.circuit_filter.currentText()

        filtered = []
        for device in devices:
            data = device['data']

            # Apply device type filter
            if device_type_filter != "All Types":
                if data.get('type', 'Unknown') != device_type_filter:
                    continue

            # Apply circuit filter
            if circuit_filter != "All Circuits":
                if data.get('circuit', 'Not Assigned') != circuit_filter:
                    continue

            filtered.append(device)

        return filtered

    def _calculate_coverage(self, device):
        """Calculate coverage area for a device"""
        data = device['data']
        device_type = data.get('type', '').lower()

        if 'smoke' in device_type:
            return "900 sq ft (30x30 ft)"
        elif 'heat' in device_type:
            return "2500 sq ft (50x50 ft)"
        elif 'strobe' in device_type:
            return "Visual coverage area"
        elif 'speaker' in device_type:
            return "Audio coverage area"
        else:
            return "N/A"

    def _load_location_map(self, devices):
        """Create a text-based location map"""
        if not devices:
            self.location_text.setPlainText("No devices placed in current drawing.")
            return

        # Group devices by approximate location (grid)
        grid_size = 100  # feet
        location_grid = {}

        for device in devices:
            pos = device['position']
            grid_x = int(pos.x() // grid_size)
            grid_y = int(pos.y() // grid_size)
            grid_key = (grid_x, grid_y)

            if grid_key not in location_grid:
                location_grid[grid_key] = []

            location_grid[grid_key].append(device)

        # Create text map
        map_text = "Device Location Map\n"
        map_text += "=" * 50 + "\n\n"

        for (grid_x, grid_y), devices_in_cell in sorted(location_grid.items()):
            map_text += f"Grid Cell ({grid_x}, {grid_y}) - Area: {grid_x*grid_size}-{grid_x*grid_size+grid_size}ft x {grid_y*grid_size}-{grid_y*grid_size+grid_size}ft\n"

            for device in devices_in_cell:
                data = device['data']
                pos = device['position']
                device_type = data.get('type', 'Unknown')
                map_text += f"  • {device_type} at ({pos.x():.1f}, {pos.y():.1f})\n"

            map_text += "\n"

        self.location_text.setPlainText(map_text)

    def _load_statistics(self, devices):
        if not devices:
            self.stats_text.setText("No devices placed in current drawing.")
            self.coverage_text.setText("No coverage analysis available.")
            return

        # Count by type
        type_counts = {}
        circuit_counts = {}
        total_devices = len(devices)

        for device in devices:
            data = device['data']

            device_type = data.get('type', 'Unknown')
            type_counts[device_type] = type_counts.get(device_type, 0) + 1

            circuit = data.get('circuit', 'Not Assigned')
            circuit_counts[circuit] = circuit_counts.get(circuit, 0) + 1

        # Statistics text
        stats = f"""
Device Statistics:
==================
Total Devices: {total_devices}

By Type:
"""

        for device_type, count in sorted(type_counts.items()):
            percentage = (count / total_devices) * 100
            stats += f"• {device_type}: {count} ({percentage:.1f}%)\n"

        stats += f"\nBy Circuit:\n"
        for circuit, count in sorted(circuit_counts.items()):
            stats += f"• {circuit}: {count}\n"

        self.stats_text.setText(stats.strip())

        # Coverage analysis
        coverage = f"""
Coverage Analysis:
==================
Devices placed: {total_devices}

Coverage Types:
• Smoke Detectors: {sum(1 for d in devices if 'smoke' in d['data'].get('type', '').lower())}
• Heat Detectors: {sum(1 for d in devices if 'heat' in d['data'].get('type', '').lower())}
• Strobes: {sum(1 for d in devices if 'strobe' in d['data'].get('type', '').lower())}
• Speakers: {sum(1 for d in devices if 'speaker' in d['data'].get('type', '').lower())}

Note: Coverage calculations are estimates based on NFPA 72 requirements.
Actual coverage should be verified through proper engineering analysis.
"""
        self.coverage_text.setText(coverage.strip())

    def _apply_filters(self):
        """Re-apply filters to current data"""
        self._load_device_schedule()

    def _export_csv(self):
        """Export device schedule to CSV file"""
        # TODO: Implement CSV export
        QtWidgets.QMessageBox.information(self, "Export CSV", "CSV export will be implemented here.")

    def _export_pdf(self):
        """Export device schedule to PDF file"""
        # TODO: Implement PDF export
        QtWidgets.QMessageBox.information(self, "Export PDF", "PDF export will be implemented here.")