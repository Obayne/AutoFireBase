"""
Canvas Status Summary - Status display widget
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class CanvasStatusSummary(QWidget):
    """Widget showing canvas status summary."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Canvas Status")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title)

        # Status items
        self.device_count = QLabel("Devices: 0")
        layout.addWidget(self.device_count)

        self.wire_count = QLabel("Wires: 0")
        layout.addWidget(self.wire_count)

        self.circuit_count = QLabel("Circuits: 0")
        layout.addWidget(self.circuit_count)

    def update_counts(self, devices=0, wires=0, circuits=0):
        """Update the displayed counts."""
        self.device_count.setText(f"Devices: {devices}")
        self.wire_count.setText(f"Wires: {wires}")
        self.circuit_count.setText(f"Circuits: {circuits}")
