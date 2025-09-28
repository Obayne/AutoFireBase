from PySide6 import QtWidgets


class GridStyleDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, scene=None, prefs: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Grid Style")
        self.scene = scene
        self.prefs = prefs if isinstance(prefs, dict) else {}

        v = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.s_opacity = QtWidgets.QDoubleSpinBox()
        self.s_opacity.setRange(0.05, 1.0)
        self.s_opacity.setSingleStep(0.05)
        self.s_width = QtWidgets.QDoubleSpinBox()
        self.s_width.setRange(0.0, 2.0)
        self.s_width.setSingleStep(0.1)
        self.s_major = QtWidgets.QSpinBox()
        self.s_major.setRange(2, 12)

        # load from prefs or scene defaults
        op = float(self.prefs.get("grid_opacity", getattr(scene, "grid_opacity", 0.35)))
        wd = float(self.prefs.get("grid_width_px", getattr(scene, "grid_width", 0.0)))
        mj = int(self.prefs.get("grid_major_every", getattr(scene, "major_every", 5)))
        self.s_opacity.setValue(op)
        self.s_width.setValue(wd)
        self.s_major.setValue(mj)

        form.addRow("Opacity:", self.s_opacity)
        form.addRow("Line width (px):", self.s_width)
        form.addRow("Major line every N:", self.s_major)
        v.addLayout(form)

        bb = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        v.addWidget(bb)

    def apply(self):
        op = float(self.s_opacity.value())
        wd = float(self.s_width.value())
        mj = int(self.s_major.value())
        if self.scene:
            self.scene.set_grid_style(op, wd, mj)
        if self.prefs is not None:
            self.prefs["grid_opacity"] = op
            self.prefs["grid_width_px"] = wd
            self.prefs["grid_major_every"] = mj
        return op, wd, mj
