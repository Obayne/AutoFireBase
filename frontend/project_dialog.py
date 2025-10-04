"""
AutoFire New Project Dialog
Dialog for creating new fire alarm design projects.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class NewProjectDialog(QDialog):
    """Dialog for creating a new AutoFire project."""

    # Signal emitted when project is created
    project_created = Signal(dict)  # project data dict

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New AutoFire Project")
        self.setModal(True)
        self.resize(500, 400)

        self.project_data = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Form layout for project details
        form_layout = QFormLayout()

        # Project name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter project name")
        form_layout.addRow("Project Name:", self.name_edit)

        # Client
        self.client_edit = QLineEdit()
        self.client_edit.setPlaceholderText("Client name")
        form_layout.addRow("Client:", self.client_edit)

        # Address
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Project address")
        form_layout.addRow("Address:", self.address_edit)

        # AHJ Profile
        self.ahj_combo = QComboBox()
        self.ahj_combo.addItems(
            ["Local Fire Department", "State Fire Marshal", "NFPA Standard", "Custom Requirements"]
        )
        form_layout.addRow("AHJ Profile:", self.ahj_combo)

        # Occupancy
        self.occupancy_combo = QComboBox()
        self.occupancy_combo.addItems(
            [
                "Business",
                "Educational",
                "Healthcare",
                "Residential",
                "Assembly",
                "Mercantile",
                "Industrial",
                "Storage",
            ]
        )
        form_layout.addRow("Occupancy Type:", self.occupancy_combo)

        # Sheet size
        self.sheet_combo = QComboBox()
        self.sheet_combo.addItems(
            [
                "8.5x11 (Letter)",
                "11x17 (Tabloid)",
                "24x36 (Arch D)",
                "30x42 (Arch E)",
                "36x48 (Arch E1)",
            ]
        )
        form_layout.addRow("Sheet Size:", self.sheet_combo)

        # Units
        self.units_combo = QComboBox()
        self.units_combo.addItems(["Feet", "Meters"])
        self.units_combo.setCurrentText("Feet")
        form_layout.addRow("Units:", self.units_combo)

        # Pixels per foot
        self.ppf_spin = QSpinBox()
        self.ppf_spin.setRange(10, 200)
        self.ppf_spin.setValue(50)
        self.ppf_spin.setSuffix(" px/ft")
        form_layout.addRow("Scale (px/ft):", self.ppf_spin)

        layout.addLayout(form_layout)

        # Floorplan import section
        floorplan_layout = QHBoxLayout()
        floorplan_layout.addWidget(QLabel("Floorplan:"))

        self.floorplan_path_edit = QLineEdit()
        self.floorplan_path_edit.setPlaceholderText("Select DXF or PDF file...")
        self.floorplan_path_edit.setReadOnly(True)
        floorplan_layout.addWidget(self.floorplan_path_edit)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_floorplan)
        floorplan_layout.addWidget(self.browse_button)

        layout.addLayout(floorplan_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _browse_floorplan(self) -> None:
        """Browse for floorplan file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Floorplan", "", "DXF Files (*.dxf);;PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self.floorplan_path_edit.setText(file_path)

    def _accept(self) -> None:
        """Validate and accept the dialog."""
        # Validate required fields
        if not self.name_edit.text().strip():
            # For now, just proceed - we'll add validation later
            pass

        # Collect project data
        self.project_data = {
            "name": self.name_edit.text().strip(),
            "client": self.client_edit.text().strip(),
            "address": self.address_edit.text().strip(),
            "ahj_profile": self.ahj_combo.currentText(),
            "occupancy": self.occupancy_combo.currentText(),
            "sheet_size": self.sheet_combo.currentText(),
            "units": self.units_combo.currentText(),
            "pixels_per_foot": self.ppf_spin.value(),
            "floorplan_path": self.floorplan_path_edit.text().strip(),
        }

        self.project_created.emit(self.project_data)
        self.accept()


def show_new_project_dialog() -> dict | None:
    """
    Show the new project dialog and return project data.
    Returns None if cancelled.
    """
    dialog = NewProjectDialog()
    result = None

    def on_project_created(data: dict):
        nonlocal result
        result = data

    dialog.project_created.connect(on_project_created)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        return result

    return None
