from PySide6 import QtWidgets

def _ft_in_row(ft=25, inch=0):
    wrap = QtWidgets.QWidget()
    row = QtWidgets.QHBoxLayout(wrap); row.setContentsMargins(0,0,0,0)
    sp_ft = QtWidgets.QSpinBox(); sp_ft.setRange(0, 1000); sp_ft.setValue(int(ft))
    sp_in = QtWidgets.QSpinBox(); sp_in.setRange(0, 11); sp_in.setValue(int(inch))
    row.addWidget(sp_ft); row.addWidget(QtWidgets.QLabel("ft")); row.addSpacing(12)
    row.addWidget(sp_in); row.addWidget(QtWidgets.QLabel("in"))
    return wrap, sp_ft, sp_in

class CoverageDialog(QtWidgets.QDialog):
    """
    Manual coverage controls.
    - Kind chooses the overlay shape:
        * Detector        -> circle
        * Strobe ceiling  -> circle + square
        * Strobe wall     -> rectangle
        * Speaker         -> circle (wall mode would be rectangle)
    - Radius set in feet+inches
    """
    def __init__(self, parent=None, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Coverage")
        self.setModal(True)
        form = QtWidgets.QFormLayout(self)
        ex = existing or {}

        self.cmb_kind = QtWidgets.QComboBox()
        opts = ["Detector (circle)", "Strobe — ceiling (circle+square)", "Strobe — wall (rectangle)", "Speaker (circle)"]
        self.cmb_kind.addItems(opts)
        kind_map = {"detector":0, "strobe_ceiling":1, "strobe_wall":2, "speaker":3}
        idx = kind_map.get(ex.get("kind","detector"), 0)
        self.cmb_kind.setCurrentIndex(idx)
        form.addRow("Kind:", self.cmb_kind)

        r_ft = float(ex.get("radius_ft", 25.0))
        ft = int(r_ft); inc = int(round((r_ft-ft)*12.0))
        row, self.sp_ft, self.sp_in = _ft_in_row(ft, inc)
        form.addRow("Radius:", row)

        self.chk_on = QtWidgets.QCheckBox("Enable overlay")
        self.chk_on.setChecked(ex.get("mode","none") != "none")
        form.addRow("", self.chk_on)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        form.addRow(btns)

    def get_settings(self):
        kidx = self.cmb_kind.currentIndex()
        kind = ["detector","strobe_ceiling","strobe_wall","speaker"][kidx]
        ft = self.sp_ft.value(); inc = self.sp_in.value()
        enabled = self.chk_on.isChecked()
        return {"kind": kind, "mode": ("none" if not enabled else "manual"), "radius_ft": float(ft + inc/12.0)}
