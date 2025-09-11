
from PySide6 import QtCore, QtGui, QtWidgets

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, init=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        init = init or {}
        form = QtWidgets.QFormLayout(self)

        self.chk_grid = QtWidgets.QCheckBox(); self.chk_grid.setChecked(bool(init.get("show_grid", True)))
        self.chk_snap = QtWidgets.QCheckBox(); self.chk_snap.setChecked(bool(init.get("snap", True)))

        self.cmb_theme = QtWidgets.QComboBox(); self.cmb_theme.addItems(["dark","light"])
        self.cmb_theme.setCurrentText((init.get("theme") or "dark"))

        self.spin_ppf = QtWidgets.QDoubleSpinBox(); self.spin_ppf.setRange(1.0, 2000.0); self.spin_ppf.setDecimals(2)
        self.spin_ppf.setValue(float(init.get("px_per_ft", 12.0)))

        form.addRow("Show grid", self.chk_grid)
        form.addRow("Snap to grid/step", self.chk_snap)
        form.addRow("Theme", self.cmb_theme)
        form.addRow("Pixels per foot", self.spin_ppf)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        form.addRow(btns)

    def values(self):
        return {
            "show_grid": self.chk_grid.isChecked(),
            "snap": self.chk_snap.isChecked(),
            "theme": self.cmb_theme.currentText(),
            "px_per_ft": float(self.spin_ppf.value()),
        }
