from PySide6 import QtWidgets

# UI/dialog strings may be long for clarity. Allow E501 in this dialog.
# ruff: noqa: E501
# noqa: E501


class CoverageDialog(QtWidgets.QDialog):
    """Edit per-device coverage. v1 keeps it simple & honest:
    - Strobe: manual coverage diameter (ft); mount = wall/ceiling
    - Speaker: L@10ft and target dB -> inverse-square to compute radius
    - Smoke: spacing (ft) guide ring
    We store computed radius_ft, and caller passes px_per_ft.
    """

    def __init__(self, parent=None, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Coverage")
        self.setModal(True)
        v = QtWidgets.QVBoxLayout(self)

        # Mode
        form = QtWidgets.QFormLayout()
        self.cmb_mode = QtWidgets.QComboBox()
        self.cmb_mode.addItems(["none", "strobe", "speaker", "smoke"])
        self.cmb_mount = QtWidgets.QComboBox()
        self.cmb_mount.addItems(["ceiling", "wall"])
        self.ed_room_size = QtWidgets.QSpinBox()
        self.ed_room_size.setRange(0, 1000)
        self.ed_room_size.setSuffix(" ft")
        self.ed_room_size.setValue(20)
        self.ed_ceiling_height = QtWidgets.QSpinBox()
        self.ed_ceiling_height.setRange(0, 100)
        self.ed_ceiling_height.setSuffix(" ft")
        self.ed_ceiling_height.setValue(10)
        self.btn_suggest = QtWidgets.QPushButton("Suggest Candela")
        self.lbl_suggested_candela = QtWidgets.QLabel("")

        self.ed_diam = QtWidgets.QDoubleSpinBox()
        self.ed_diam.setRange(0, 1000)
        self.ed_diam.setSuffix(" ft")
        self.ed_diam.setValue(50.0)
        self.ed_L10 = QtWidgets.QDoubleSpinBox()
        self.ed_L10.setRange(40, 130)
        self.ed_L10.setSuffix(" dB")
        self.ed_L10.setValue(95.0)
        self.ed_target = QtWidgets.QDoubleSpinBox()
        self.ed_target.setRange(40, 120)
        self.ed_target.setSuffix(" dB")
        self.ed_target.setValue(75.0)
        self.ed_spacing = QtWidgets.QDoubleSpinBox()
        self.ed_spacing.setRange(0, 200)
        self.ed_spacing.setSuffix(" ft")
        self.ed_spacing.setValue(30.0)

        form.addRow("Mode:", self.cmb_mode)
        form.addRow("Mount:", self.cmb_mount)
        form.addRow("Room Size:", self.ed_room_size)
        form.addRow("Ceiling Height:", self.ed_ceiling_height)
        form.addRow(self.btn_suggest)
        form.addRow("Suggested Candela:", self.lbl_suggested_candela)

        form.addRow("Strobe coverage diameter:", self.ed_diam)
        form.addRow("Speaker level @10ft:", self.ed_L10)
        form.addRow("Speaker target dB:", self.ed_target)
        form.addRow("Smoke spacing:", self.ed_spacing)
        v.addLayout(form)

        self.lbl_info = QtWidgets.QLabel(
            "Tip: diameter/spacing are simple helpers; NFPA/manufacturer tables override in submittals."
        )
        self.lbl_info.setWordWrap(True)
        v.addWidget(self.lbl_info)

        bb = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        v.addWidget(bb)

        self.btn_suggest.clicked.connect(self.suggest_candela)

        # Track the source of the settings
        self.source = "manual"
        self.ed_diam.valueChanged.connect(self._on_manual_edit)
        self.ed_L10.valueChanged.connect(self._on_manual_edit)
        self.ed_target.valueChanged.connect(self._on_manual_edit)
        self.ed_spacing.valueChanged.connect(self._on_manual_edit)

        # Load any existing settings passed in
        if existing:
            mode = existing.get("mode", "none")
            i = self.cmb_mode.findText(mode)
            if i >= 0:
                self.cmb_mode.setCurrentIndex(i)
            mnt = existing.get("mount", "ceiling")
            j = self.cmb_mount.findText(mnt)
            if j >= 0:
                self.cmb_mount.setCurrentIndex(j)
            p = existing.get("params", {})
            if "diameter_ft" in p:
                self.ed_diam.setValue(float(p.get("diameter_ft", 50.0)))
            if "L10" in p:
                self.ed_L10.setValue(float(p.get("L10", 95.0)))
            if "target_db" in p:
                self.ed_target.setValue(float(p.get("target_db", 75.0)))
            if "spacing_ft" in p:
                self.ed_spacing.setValue(float(p.get("spacing_ft", 30.0)))

            # Set source based on existing data if available
            self.source = existing.get("source", "manual")

    def _on_manual_edit(self):
        self.source = "manual"
        self.lbl_suggested_candela.setText("(manual override)")

    def suggest_candela(self):
        try:
            from backend.coverage_service import (
                get_required_ceiling_strobe_candela,
                get_required_wall_strobe_candela,
            )

            room_size = self.ed_room_size.value()
            ceiling_height = self.ed_ceiling_height.value()
            mount = self.cmb_mount.currentText()

            candela = None
            if mount == "wall":
                candela = get_required_wall_strobe_candela(room_size)
            else:  # ceiling
                candela = get_required_ceiling_strobe_candela(ceiling_height, room_size)

            if candela:
                self.lbl_suggested_candela.setText(f"{candela} cd")
                # This mapping is based on NFPA 72 tables for wall strobes
                # where candela rating often corresponds to room size (e.g., 15cd for 20x20)
                candela_to_diameter = {
                    15: 20,
                    30: 30,
                    60: 40,
                    95: 50,
                    135: 60,
                    185: 70,
                    115: 60,  # Ceiling values
                    150: 70,
                    177: 80,
                }
                diameter = candela_to_diameter.get(candela, self.ed_diam.value())
                self.ed_diam.setValue(diameter)
                self.source = "auto"
            else:
                self.lbl_suggested_candela.setText("N/A (out of range)")
                self.source = "manual"
        except Exception as e:
            self.lbl_suggested_candela.setText(f"Error: {e}")
            self.source = "manual"

    def get_settings(self, px_per_ft: float):
        mode = self.cmb_mode.currentText()
        mount = self.cmb_mount.currentText()
        params = {}
        radius_ft = 0.0

        if mode == "strobe":
            diam = float(self.ed_diam.value())
            params = {"diameter_ft": diam}
            radius_ft = max(0.0, diam / 2.0)

        elif mode == "speaker":
            L10 = float(self.ed_L10.value())
            tgt = float(self.ed_target.value())
            params = {"L10": L10, "target_db": tgt}
            # inverse-square, ref at 10 ft: L(r) = L10 - 20*log10(r/10)
            # Solve for r: r = 10 * 10**((L10 - tgt)/20)
            radius_ft = 10.0 * (10.0 ** ((L10 - tgt) / 20.0))
            radius_ft = max(0.0, radius_ft)

        elif mode == "smoke":
            spacing = float(self.ed_spacing.value())
            params = {"spacing_ft": spacing}
            radius_ft = max(0.0, spacing / 2.0)

        else:  # none
            params = {}
            radius_ft = 0.0

        return {
            "source": self.source,
            "mode": mode,
            "mount": mount,
            "params": params,
            "computed_radius_ft": radius_ft,
            "px_per_ft": float(px_per_ft),
        }
