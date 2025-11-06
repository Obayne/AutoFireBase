"""
System Builder Guided - Guided system building interface
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class SystemBuilderWidget(QWidget):
    """Guided system builder widget."""

    # Signal emitted when CAD is ready
    cad_ready = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("System Builder (Guided)")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Description
        desc = QLabel("Build fire protection systems step-by-step")
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)

        # Start button
        start_btn = QPushButton("Start Building System")
        start_btn.clicked.connect(self._on_start_clicked)
        layout.addWidget(start_btn)

        # Status
        self.status_label = QLabel("Ready to build")
        self.status_label.setStyleSheet("color: #008000;")
        layout.addWidget(self.status_label)

    def _on_start_clicked(self):
        """Handle start button click."""
        # Emit cad_ready signal with default settings
        settings = {"mode": "guided", "system_type": "fire_alarm"}
        self.cad_ready.emit(settings)
        self.status_label.setText("System building started...")
