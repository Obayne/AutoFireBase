"""
Canvas Status Summary Widget
Real-time status display for fire alarm system design
"""

from PySide6 import QtWidgets
from PySide6.QtCore import Qt


class CanvasStatusSummary(QtWidgets.QWidget):
    """Real-time summary of canvas content and system status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Status")
        self.setMinimumWidth(250)
        self.setup_ui()

        # Status tracking
        self.device_stats = {"placed": 0, "connected": 0, "unconnected": 0, "partial": 0}
        self.wire_stats = {"total_length_ft": 0.0, "circuits": 0, "segments": 0}
        self.system_stats = {"panels": 0, "zones": 0, "voltage_drop": 0.0, "battery_hours": 0.0}

    def setup_ui(self):
        """Setup the status summary UI."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QtWidgets.QLabel("System Status")
        title.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                background-color: #0078d4;
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 5px;
            }
        """
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Device Status Section
        device_group = self._create_status_group("🔧 Devices")
        self.device_placed_label = QtWidgets.QLabel("Placed: 0")
        self.device_connected_label = QtWidgets.QLabel("Connected: 0")
        self.device_unconnected_label = QtWidgets.QLabel("Unconnected: 0")
        self.device_partial_label = QtWidgets.QLabel("Partial: 0")

        device_layout = device_group.layout()
        device_layout.addWidget(self.device_placed_label)
        device_layout.addWidget(self.device_connected_label)
        device_layout.addWidget(self.device_unconnected_label)
        device_layout.addWidget(self.device_partial_label)

        layout.addWidget(device_group)

        # Wire Status Section
        wire_group = self._create_status_group("🔌 Wiring")
        self.wire_length_label = QtWidgets.QLabel("Total Length: 0 ft")
        self.wire_circuits_label = QtWidgets.QLabel("Circuits: 0")
        self.wire_segments_label = QtWidgets.QLabel("Segments: 0")

        wire_layout = wire_group.layout()
        wire_layout.addWidget(self.wire_length_label)
        wire_layout.addWidget(self.wire_circuits_label)
        wire_layout.addWidget(self.wire_segments_label)

        layout.addWidget(wire_group)

        # System Status Section
        system_group = self._create_status_group("⚡ System")
        self.system_panels_label = QtWidgets.QLabel("Panels: 0")
        self.system_zones_label = QtWidgets.QLabel("Zones: 0")
        self.system_voltage_label = QtWidgets.QLabel("Voltage Drop: 0.0V")
        self.system_battery_label = QtWidgets.QLabel("Battery: 0.0 hrs")

        system_layout = system_group.layout()
        system_layout.addWidget(self.system_panels_label)
        system_layout.addWidget(self.system_zones_label)
        system_layout.addWidget(self.system_voltage_label)
        system_layout.addWidget(self.system_battery_label)

        layout.addWidget(system_group)

        # Status Summary Section
        summary_group = self._create_status_group("📊 Summary")
        self.status_text = QtWidgets.QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
        """
        )
        self.status_text.setPlainText("System ready for design...")

        summary_layout = summary_group.layout()
        summary_layout.addWidget(self.status_text)

        layout.addWidget(summary_group)

        # Add stretch to push content to top
        layout.addStretch()

    def _create_status_group(self, title: str) -> QtWidgets.QGroupBox:
        """Create a status group box with consistent styling."""
        group = QtWidgets.QGroupBox(title)
        group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #0078d4;
                border-radius: 3px;
            }
            QLabel {
                color: #ffffff;
                padding: 2px;
                margin: 1px;
            }
        """
        )

        layout = QtWidgets.QVBoxLayout(group)
        layout.setSpacing(2)
        layout.setContentsMargins(10, 15, 10, 10)

        return group

    def update_device_stats(self, placed: int, connected: int, unconnected: int, partial: int = 0):
        """Update device statistics."""
        self.device_stats.update(
            {
                "placed": placed,
                "connected": connected,
                "unconnected": unconnected,
                "partial": partial,
            }
        )

        # Update labels with color coding
        self.device_placed_label.setText(f"Placed: {placed}")

        # Connected devices - green
        self.device_connected_label.setText(f"Connected: {connected}")
        self.device_connected_label.setStyleSheet("color: #00ff00;")

        # Unconnected devices - orange
        self.device_unconnected_label.setText(f"Unconnected: {unconnected}")
        self.device_unconnected_label.setStyleSheet(
            "color: #ffa500;" if unconnected > 0 else "color: #ffffff;"
        )

        # Partially connected - yellow
        self.device_partial_label.setText(f"Partial: {partial}")
        self.device_partial_label.setStyleSheet(
            "color: #ffff00;" if partial > 0 else "color: #ffffff;"
        )

        self._update_summary()

    def update_wire_stats(self, total_length_ft: float, circuits: int, segments: int):
        """Update wire statistics."""
        self.wire_stats.update(
            {"total_length_ft": total_length_ft, "circuits": circuits, "segments": segments}
        )

        self.wire_length_label.setText(f"Total Length: {total_length_ft:.1f} ft")
        self.wire_circuits_label.setText(f"Circuits: {circuits}")
        self.wire_segments_label.setText(f"Segments: {segments}")

        self._update_summary()

    def update_system_stats(
        self, panels: int, zones: int, voltage_drop: float, battery_hours: float
    ):
        """Update system statistics."""
        self.system_stats.update(
            {
                "panels": panels,
                "zones": zones,
                "voltage_drop": voltage_drop,
                "battery_hours": battery_hours,
            }
        )

        self.system_panels_label.setText(f"Panels: {panels}")
        self.system_zones_label.setText(f"Zones: {zones}")

        # Voltage drop - warn if > 3V
        vd_color = "#ff0000" if voltage_drop > 3.0 else "#ffffff"
        self.system_voltage_label.setText(f"Voltage Drop: {voltage_drop:.1f}V")
        self.system_voltage_label.setStyleSheet(f"color: {vd_color};")

        # Battery - warn if < 24 hours
        bat_color = "#ffa500" if battery_hours < 24.0 else "#00ff00"
        self.system_battery_label.setText(f"Battery: {battery_hours:.1f} hrs")
        self.system_battery_label.setStyleSheet(f"color: {bat_color};")

        self._update_summary()

    def _update_summary(self):
        """Update the summary text area."""
        summary_lines = []

        # Device summary
        dev = self.device_stats
        if dev["placed"] > 0:
            completion = (dev["connected"] / dev["placed"]) * 100 if dev["placed"] > 0 else 0
            summary_lines.append(f"Device completion: {completion:.1f}%")

            if dev["unconnected"] > 0:
                summary_lines.append(f"⚠️ {dev['unconnected']} devices need wiring")

        # Wire summary
        wire = self.wire_stats
        if wire["total_length_ft"] > 0:
            summary_lines.append(f"Wire used: {wire['total_length_ft']:.1f} ft")

        # System warnings
        sys = self.system_stats
        if sys["voltage_drop"] > 3.0:
            summary_lines.append("🔴 High voltage drop detected")
        if sys["battery_hours"] > 0 and sys["battery_hours"] < 24.0:
            summary_lines.append("🟡 Battery capacity low")

        # Overall status
        if dev["placed"] == 0:
            summary_lines.append("System ready - start placing devices")
        elif dev["unconnected"] == 0 and dev["placed"] > 0:
            summary_lines.append("✅ All devices connected")
        else:
            summary_lines.append("🔧 Design in progress...")

        self.status_text.setPlainText(
            "\n".join(summary_lines) if summary_lines else "System ready for design..."
        )

    def clear_stats(self):
        """Clear all statistics."""
        self.update_device_stats(0, 0, 0, 0)
        self.update_wire_stats(0.0, 0, 0)
        self.update_system_stats(0, 0, 0.0, 0.0)
