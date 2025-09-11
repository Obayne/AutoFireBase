from PySide6 import QtCore, QtGui, QtWidgets

class CoverageDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, existing=None, px_per_ft=12.0):
        super().__init__(parent)
        self.setWindowTitle("Coverage Settings")
        self.px_per_ft = float(px_per_ft)

        lay = QtWidgets.QVBoxLayout(self)

        # Mode
        self.mode = QtWidgets.QComboBox(); self.mode.addItems(["none","speaker","strobe","detector"])
        # Mount
        self.mount = QtWidgets.QComboBox(); self.mount.addItems(["ceiling","wall"])
        # Manual radius (ft)
        self.radius = QtWidgets.QDoubleSpinBox(); self.radius.setRange(0, 1000); self.radius.setDecimals(2); self.radius.setValue(25.0)
        self.radius.setSuffix(" ft")

        # Speaker physics
        self.db_ref   = QtWidgets.QDoubleSpinBox(); self.db_ref.setRange(0, 200); self.db_ref.setValue(95.0); self.db_ref.setSuffix(" dB")
        self.target_db= QtWidgets.QDoubleSpinBox(); self.target_db.setRange(0, 200); self.target_db.setValue(75.0); self.target_db.setSuffix(" dB")
        self.loss10   = QtWidgets.QDoubleSpinBox(); self.loss10.setRange(0.1, 50); self.loss10.setSingleStep(0.1); self.loss10.setValue(6.0); self.loss10.setSuffix(" dB/10ft")

        form = QtWidgets.QFormLayout()
        form.addRow("Mode:", self.mode)
        form.addRow("Mount:", self.mount)
        form.addRow("Manual radius:", self.radius)
        form.addRow(QtWidgets.QLabel("<b>Speaker (approx)</b>"))
        form.addRow("Ref dB:", self.db_ref)
        form.addRow("Target dB:", self.target_db)
        form.addRow("Loss/10ft:", self.loss10)

        lay.addLayout(form)

        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        lay.addWidget(bb)

        if existing:
            self.mode.setCurrentText(existing.get("mode","none"))
            self.mount.setCurrentText(existing.get("mount","ceiling"))
            self.radius.setValue(float(existing.get("radius_ft", 25.0)))
            sp = existing.get("speaker",{})
            self.db_ref.setValue(float(sp.get("db_ref",95.0)))
            self.target_db.setValue(float(sp.get("target_db",75.0)))
            self.loss10.setValue(float(sp.get("loss10",6.0)))

    def get_settings(self):
        m = self.mode.currentText()
        radius_ft = float(self.radius.value())
        # quick physics for speaker coverage
        if m == "speaker":
            db_ref   = float(self.db_ref.value())
            target   = float(self.target_db.value())
            loss10   = float(self.loss10.value())
            if loss10 > 0:
                # every 10ft loses loss10 dB => distance multiplier (db_ref - target)/loss10
                mult = max(0.0, (db_ref - target)/loss10)
                radius_ft = max(radius_ft, mult*10.0)
            settings = {"mode":m,"mount":self.mount.currentText(),"radius_ft":radius_ft,
                        "speaker":{"db_ref":db_ref,"target_db":target,"loss10":loss10}}
        else:
            settings = {"mode":m,"mount":self.mount.currentText(),"radius_ft":radius_ft}
        settings["px_per_ft"] = self.px_per_ft
        settings["computed_radius_px"] = radius_ft * self.px_per_ft
        return settings
