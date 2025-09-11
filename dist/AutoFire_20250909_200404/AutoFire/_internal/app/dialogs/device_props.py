
from PySide6 import QtCore, QtGui, QtWidgets

class DevicePropsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, item=None, px_per_ft=12.0):
        super().__init__(parent)
        self.setWindowTitle("Device Properties")
        self.item = item
        self.px_per_ft = float(px_per_ft)

        form = QtWidgets.QFormLayout(self)

        self.ed_name = QtWidgets.QLineEdit(item.name if item else "")
        self.ed_symbol = QtWidgets.QLineEdit(item.symbol if item else "")
        self.ed_mfr = QtWidgets.QLineEdit(item.manufacturer if item else "")
        self.ed_part = QtWidgets.QLineEdit(item.part_number if item else "")
        self.spin_off_x = QtWidgets.QDoubleSpinBox(); self.spin_off_x.setRange(-9999, 9999); self.spin_off_x.setDecimals(2)
        self.spin_off_y = QtWidgets.QDoubleSpinBox(); self.spin_off_y.setRange(-9999, 9999); self.spin_off_y.setDecimals(2)
        if item:
            self.spin_off_x.setValue(item.label_offset.x() / self.px_per_ft * 12.0)
            self.spin_off_y.setValue(item.label_offset.y() / self.px_per_ft * 12.0)

        form.addRow("Name", self.ed_name)
        form.addRow("Symbol", self.ed_symbol)
        form.addRow("Manufacturer", self.ed_mfr)
        form.addRow("Part #", self.ed_part)
        form.addRow("Label offset X (in)", self.spin_off_x)
        form.addRow("Label offset Y (in)", self.spin_off_y)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        form.addRow(btns)

    def values(self):
        dx_px = float(self.spin_off_x.value()) / 12.0 * self.px_per_ft
        dy_px = float(self.spin_off_y.value()) / 12.0 * self.px_per_ft
        return {
            "name": self.ed_name.text().strip(),
            "symbol": self.ed_symbol.text().strip(),
            "manufacturer": self.ed_mfr.text().strip(),
            "part_number": self.ed_part.text().strip(),
            "label_offset_px": (dx_px, dy_px),
        }
