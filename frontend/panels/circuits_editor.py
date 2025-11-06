"""
Circuits Editor - Professional circuit editing interface
"""

from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget


class CircuitsEditor(QWidget):
    """Professional circuit editor widget."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Circuits Editor")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Circuit list
        self.circuit_list = QListWidget()
        self.circuit_list.addItem("Circuit 1 - Power")
        self.circuit_list.addItem("Circuit 2 - Lighting")
        layout.addWidget(self.circuit_list)

        # Instructions
        instructions = QLabel("Select a circuit to edit properties")
        instructions.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(instructions)
