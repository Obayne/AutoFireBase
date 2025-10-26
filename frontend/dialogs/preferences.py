from __future__ import annotations

from typing import Any, Dict

from PySide6 import QtWidgets


class PreferencesDialog(QtWidgets.QDialog):
    """Simple Preferences dialog for export defaults.

    Exposes three fields:
      - Default export folder (report_default_dir)
      - Include Device Docs in submittal (include_device_docs_in_submittal)
      - Export image/PDF DPI (export_image_dpi)
    """

    def __init__(self, parent=None, initial: Dict[str, Any] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.resize(480, 220)

        prefs = dict(initial or {})

        form = QtWidgets.QFormLayout()
        form.setContentsMargins(12, 12, 12, 12)
        form.setSpacing(10)

        # Default export folder
        folder_row = QtWidgets.QHBoxLayout()
        self.folder_edit = QtWidgets.QLineEdit(prefs.get("report_default_dir", ""))
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(self._choose_folder)
        folder_row.addWidget(self.folder_edit)
        folder_row.addWidget(browse_btn)
        folder_row_w = QtWidgets.QWidget()
        folder_row_w.setLayout(folder_row)
        form.addRow("Default export folder:", folder_row_w)

        # Include docs in submittal
        self.include_docs_chk = QtWidgets.QCheckBox("Include device docs in HTML submittal")
        self.include_docs_chk.setChecked(bool(prefs.get("include_device_docs_in_submittal", True)))
        form.addRow("Submittal:", self.include_docs_chk)

        # Export DPI
        self.dpi_spin = QtWidgets.QSpinBox()
        self.dpi_spin.setRange(72, 1200)
        self.dpi_spin.setSingleStep(25)
        self.dpi_spin.setValue(int(prefs.get("export_image_dpi", 300)))
        form.addRow("Export DPI:", self.dpi_spin)

        # Buttons
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        outer = QtWidgets.QVBoxLayout(self)
        outer.addLayout(form)
        outer.addWidget(btn_box)

    def _choose_folder(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose export folder", self.folder_edit.text())
        if path:
            self.folder_edit.setText(path)

    def values(self) -> Dict[str, Any]:
        return {
            "report_default_dir": self.folder_edit.text().strip(),
            "include_device_docs_in_submittal": self.include_docs_chk.isChecked(),
            "export_image_dpi": int(self.dpi_spin.value()),
        }
