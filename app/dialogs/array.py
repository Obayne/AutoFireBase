from PySide6 import QtWidgets

from app import units


class ArrayDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, default_px_per_ft=12.0):
        super().__init__(parent)
        self.setWindowTitle("Place Array")
        self.setModal(True)
        self.setMinimumWidth(360)

        self.spin_rows = QtWidgets.QSpinBox()
        self.spin_rows.setRange(1, 500)
        self.spin_rows.setValue(3)
        self.spin_cols = QtWidgets.QSpinBox()
        self.spin_cols.setRange(1, 500)
        self.spin_cols.setValue(3)
        self.spin_spacing_ft = QtWidgets.QDoubleSpinBox()
        self.spin_spacing_ft.setRange(0.1, 1000)
        self.spin_spacing_ft.setValue(30.0)
        self.spin_spacing_ft.setDecimals(2)
        self.spin_px_per_ft = QtWidgets.QDoubleSpinBox()
        self.spin_px_per_ft.setRange(1, 2000)
        self.spin_px_per_ft.setValue(default_px_per_ft)
        self.chk_use_cov = QtWidgets.QCheckBox("Use selected device coverage tile for spacing")

        form = QtWidgets.QFormLayout()
        form.addRow("Rows", self.spin_rows)
        form.addRow("Columns", self.spin_cols)
        form.addRow("Spacing (ft)", self.spin_spacing_ft)
        form.addRow("Pixels per foot", self.spin_px_per_ft)
        form.addRow(self.chk_use_cov)

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        main = QtWidgets.QVBoxLayout(self)
        main.addLayout(form)
        main.addWidget(btns)

    def get_params(self):
        return {
            "rows": self.spin_rows.value(),
            "cols": self.spin_cols.value(),
            "spacing_px": units.ft_to_px(self.spin_spacing_ft.value(), self.spin_px_per_ft.value()),
            "use_coverage_tile": self.chk_use_cov.isChecked(),
        }
