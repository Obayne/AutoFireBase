from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QLabel, QGroupBox, QScrollArea, QFormLayout, QWidget, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtCore import Qt

from app import catalog


class CalculationsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculations Report")
        self.resize(1000, 700)  # Default size instead of minimum
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)

        # Create tab widget for different calculation types
        self.tabs = QtWidgets.QTabWidget()
        # self.tabs.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Device Summary Tab
        self.tabs.addTab(self._create_device_summary_tab(), "Device Summary")

        # Battery Calculations Tab
        self.tabs.addTab(self._create_battery_tab(), "Battery Calculations")

        # Coverage Analysis Tab
        self.tabs.addTab(self._create_coverage_tab(), "Coverage Analysis")

        # Circuit Analysis Tab
        self.tabs.addTab(self._create_circuit_tab(), "Circuit Analysis")

        layout.addWidget(self.tabs)

        # OK Button
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        # Load data
        self._load_calculations()

    def _create_device_summary_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Device counts table
        group = QGroupBox("Device Counts")
        group_layout = QVBoxLayout(group)

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(3)
        self.device_table.setHorizontalHeaderLabels(["Device Type", "Count", "Total Cost"])
        self.device_table.horizontalHeader().setStretchLastSection(True)
        group_layout.addWidget(self.device_table)

        layout.addWidget(group)

        # Summary text
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        layout.addWidget(self.summary_text)

        return widget

    def _create_battery_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Battery Calculations (NFPA 72)")
        group_layout = QVBoxLayout(group)

        self.battery_text = QTextEdit()
        self.battery_text.setReadOnly(True)
        group_layout.addWidget(self.battery_text)

        layout.addWidget(group)
        return widget

    def _create_coverage_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Create scroll area for content
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QtWidgets.QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Coverage status
        status_group = QGroupBox("Coverage Status")
        status_layout = QVBoxLayout(status_group)

        self.coverage_status_label = QLabel("Coverage analysis requires device placement data.")
        self.coverage_status_label.setWordWrap(True)
        self.coverage_status_label.setStyleSheet("font-weight: bold; color: #666;")
        status_layout.addWidget(self.coverage_status_label)

        content_layout.addWidget(status_group)

        # Coverage requirements
        req_group = QGroupBox("NFPA 72 Coverage Requirements")
        req_layout = QFormLayout(req_group)

        req_layout.addRow("Smoke Detectors:", QLabel("One per 900 sq ft, max 30x30 ft spacing"))
        req_layout.addRow("Heat Detectors:", QLabel("One per 2500 sq ft, max 50x50 ft spacing"))
        req_layout.addRow("Strobe Lights:", QLabel("15-110 cd depending on room size"))
        req_layout.addRow("Speaker Coverage:", QLabel("Minimum 2 sq ft per speaker"))
        req_layout.addRow("Manual Stations:", QLabel("One per 200 ft of travel distance"))

        content_layout.addWidget(req_group)

        # Analysis results
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)

        self.coverage_results_text = QLabel("No devices placed yet. Add devices to the drawing to see coverage analysis.")
        self.coverage_results_text.setWordWrap(True)
        self.coverage_results_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        results_layout.addWidget(self.coverage_results_text)

        content_layout.addWidget(results_group)

        # Recommendations
        rec_group = QGroupBox("Recommendations")
        rec_layout = QVBoxLayout(rec_group)

        self.coverage_recommendations = QLabel("• Place devices according to NFPA 72 spacing requirements\n• Verify ceiling height and construction type\n• Consider room usage and occupant density\n• Test coverage with approved calculation methods")
        self.coverage_recommendations.setWordWrap(True)
        rec_layout.addWidget(self.coverage_recommendations)

        content_layout.addWidget(rec_group)

        content_layout.addStretch()  # Push content to top

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        return widget

    def _create_circuit_tab(self):
        widget = QtWidgets.QWidget()
        layout = QVBoxLayout(widget)

        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QtWidgets.QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Circuit status
        status_group = QGroupBox("Circuit Analysis Status")
        status_layout = QVBoxLayout(status_group)

        self.circuit_status_label = QLabel("Circuit analysis requires device-to-circuit assignments.")
        self.circuit_status_label.setWordWrap(True)
        self.circuit_status_label.setStyleSheet("font-weight: bold; color: #666;")
        status_layout.addWidget(self.circuit_status_label)

        content_layout.addWidget(status_group)

        # Circuit requirements
        req_group = QGroupBox("NFPA 72 Circuit Requirements")
        req_layout = QFormLayout(req_group)

        req_layout.addRow("Initiating Circuits:", QLabel("Style 4, 6, or 7 (addressable)"))
        req_layout.addRow("Notification Circuits:", QLabel("Style Z, Y, or X (power supervision)"))
        req_layout.addRow("Circuit Loading:", QLabel("Max 2A per circuit (typical)"))
        req_layout.addRow("Voltage Drop:", QLabel("Max 10% of nominal voltage"))
        req_layout.addRow("Supervision:", QLabel("All circuits must be supervised"))

        content_layout.addWidget(req_group)

        # Analysis results
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)

        self.circuit_results_text = QLabel("Circuit analysis requires devices to be assigned to specific circuits.\n\nUse the Circuit Properties dialog for detailed circuit calculations.")
        self.circuit_results_text.setWordWrap(True)
        self.circuit_results_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        results_layout.addWidget(self.circuit_results_text)

        content_layout.addWidget(results_group)

        # Recommendations
        rec_group = QGroupBox("Recommendations")
        rec_layout = QVBoxLayout(rec_group)

        self.circuit_recommendations = QLabel("• Assign devices to appropriate circuits\n• Balance circuit loading for optimal performance\n• Calculate voltage drop for long cable runs\n• Use proper wire sizing per NEC requirements\n• Implement circuit supervision and monitoring")
        self.circuit_recommendations.setWordWrap(True)
        rec_layout.addWidget(self.circuit_recommendations)

        content_layout.addWidget(rec_group)

        content_layout.addStretch()  # Push content to top

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        return widget

    def _load_calculations(self):
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

        # Device summary
        self._load_device_summary(devices)

        # Battery calculations
        self._load_battery_calculations(devices)

        # Coverage analysis
        self._load_coverage_analysis()

        # Circuit analysis
        self._load_circuit_analysis()

    def _load_device_summary(self, devices):
        # Count devices by type
        device_counts = {}
        total_cost = 0

        for device in devices:
            device_type = device.get('type', 'Unknown')
            cost = device.get('cost', 0) or 0

            if device_type not in device_counts:
                device_counts[device_type] = {'count': 0, 'cost': 0}

            device_counts[device_type]['count'] += 1
            device_counts[device_type]['cost'] += cost
            total_cost += cost

        # Populate table
        self.device_table.setRowCount(len(device_counts))

        for row, (device_type, data) in enumerate(device_counts.items()):
            self.device_table.setItem(row, 0, QTableWidgetItem(device_type))
            self.device_table.setItem(row, 1, QTableWidgetItem(str(data['count'])))
            self.device_table.setItem(row, 2, QTableWidgetItem(f"${data['cost']:.2f}"))

        # Summary text
        total_devices = sum(data['count'] for data in device_counts.values())
        summary = f"""
Total Devices: {total_devices}
Total Cost: ${total_cost:.2f}
Device Types: {len(device_counts)}

Note: This summary shows catalog devices. For placed devices in the current drawing,
use the Device Schedule report.
"""
        self.summary_text.setPlainText(summary.strip())

    def _load_battery_calculations(self, devices):
        # NFPA 72 Battery Calculations
        # This is a simplified calculation - real implementation would need more device details

        standby_hours = 24  # NFPA 72 requirement
        alarm_hours = 0.083  # 5 minutes = 0.083 hours

        # Estimate current draws (simplified)
        standby_current = 0
        alarm_current = 0

        for device in devices:
            # Simplified current estimates based on device type
            device_type = device.get('type', '').lower()
            if 'smoke' in device_type:
                standby_current += 0.0003  # 300µA standby
                alarm_current += 0.050     # 50mA alarm
            elif 'heat' in device_type:
                standby_current += 0.00005  # 50µA standby
                alarm_current += 0.020      # 20mA alarm
            elif 'pull' in device_type or 'manual' in device_type:
                standby_current += 0.00001  # 10µA standby
                alarm_current += 0.010      # 10mA alarm

        standby_ah = standby_current * standby_hours
        alarm_ah = alarm_current * alarm_hours
        total_ah = standby_ah + alarm_ah

        # NFPA 72 requires 1.25x safety factor
        required_ah = total_ah * 1.25

        battery_text = f"""
NFPA 72 Battery Calculations
=============================

Estimated Device Counts (from catalog):
- Total devices analyzed: {len(devices)}

Current Requirements:
- Standby current: {standby_current:.4f} A
- Alarm current: {alarm_current:.2f} A

Time Requirements:
- Standby time: {standby_hours} hours
- Alarm time: {alarm_hours} hours

Battery Capacity Required:
- Standby capacity: {standby_ah:.2f} Ah
- Alarm capacity: {alarm_ah:.2f} Ah
- Total capacity: {total_ah:.2f} Ah
- NFPA 72 required (1.25x): {required_ah:.2f} Ah

Recommended Battery: {self._recommend_battery(required_ah)} Ah

Note: This is a simplified calculation. Actual battery sizing requires:
- Specific device current draws from manufacturers
- Circuit configuration and wiring details
- Temperature derating factors
- Maintenance factors
"""
        self.battery_text.setPlainText(battery_text.strip())

    def _recommend_battery(self, required_ah):
        # Common battery sizes
        sizes = [4, 5, 6, 7, 8, 10, 12, 18, 24, 36, 48, 60, 80, 100]
        for size in sizes:
            if size >= required_ah:
                return size
        return required_ah * 1.5  # Fallback

    def _load_coverage_analysis(self):
        # Update coverage status
        self.coverage_status_label.setText("Coverage analysis is based on NFPA 72 requirements and device placement.")

        # Update results
        results_text = """
Current Implementation Status:
• Device placement tracking: Active
• Coverage area calculations: Basic estimates available
• NFPA 72 compliance checking: Framework in place
• Advanced coverage modeling: Requires additional development

To perform detailed coverage analysis:
1. Place devices in the drawing area
2. Use the Device Schedule report for placement verification
3. Consider room dimensions, ceiling height, and construction type
4. Verify spacing meets NFPA 72 requirements
"""
        self.coverage_results_text.setText(results_text.strip())

    def _load_circuit_analysis(self):
        # Update circuit status
        self.circuit_status_label.setText("Circuit analysis requires device-to-circuit assignments.\n\nCurrent Status: Framework implemented, detailed calculations pending.")

        # Update analysis results
        results_text = """Circuit Analysis Results:
• Circuit loading calculations: Not implemented
• Voltage drop analysis: Not implemented
• Wire size recommendations: Not implemented
• Power supply requirements: Not implemented
• Circuit breaker sizing: Not implemented

Use the Circuit Properties dialog for detailed circuit calculations."""
        self.circuit_results_text.setText(results_text)