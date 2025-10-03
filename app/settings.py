from PySide6 import QtWidgets


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, init=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        init = init or {}
        form = QtWidgets.QFormLayout(self)

        self.chk_grid = QtWidgets.QCheckBox()
        self.chk_grid.setChecked(bool(init.get("show_grid", True)))
        self.chk_snap = QtWidgets.QCheckBox()
        self.chk_snap.setChecked(bool(init.get("snap", True)))

        self.cmb_theme = QtWidgets.QComboBox()
        self.cmb_theme.addItems(["dark", "light"])
        self.cmb_theme.setCurrentText(init.get("theme") or "dark")

        self.spin_ppf = QtWidgets.QDoubleSpinBox()
        self.spin_ppf.setRange(1.0, 2000.0)
        self.spin_ppf.setDecimals(2)
        self.spin_ppf.setValue(float(init.get("px_per_ft", 12.0)))

        self.chk_ai = QtWidgets.QCheckBox()
        self.chk_ai.setChecked(bool(init.get("ai_enabled", True)))

        self.chk_proj_overview = QtWidgets.QCheckBox()
        self.chk_proj_overview.setChecked(bool(init.get("show_project_overview_window", False)))

        # CAD Functionality settings
        self.cmb_units = QtWidgets.QComboBox()
        self.cmb_units.addItems(["Imperial (feet)", "Metric (meters)"])
        self.cmb_units.setCurrentText(init.get("units", "Imperial (feet)"))

        self.cmb_scale = QtWidgets.QComboBox()
        self.cmb_scale.addItems(["1:1", "1:2", "1:4", "1:8", "1:16", "1:32", "1:64"])
        self.cmb_scale.setCurrentText(init.get("drawing_scale", "1:1"))

        self.spin_line_weight = QtWidgets.QSpinBox()
        self.spin_line_weight.setRange(1, 10)
        self.spin_line_weight.setValue(int(init.get("default_line_weight", 1)))

        self.le_default_color = QtWidgets.QLineEdit()
        self.le_default_color.setText(init.get("default_color", "#000000"))
        self.le_default_color.setPlaceholderText("#RRGGBB")

        # Menu and Table settings
        self.chk_device_palette = QtWidgets.QCheckBox()
        self.chk_device_palette.setChecked(bool(init.get("show_device_palette", True)))

        self.chk_properties_dock = QtWidgets.QCheckBox()
        self.chk_properties_dock.setChecked(bool(init.get("show_properties_dock", True)))

        self.chk_status_bar = QtWidgets.QCheckBox()
        self.chk_status_bar.setChecked(bool(init.get("show_status_bar", True)))

        # Additional settings
        self.spin_auto_save = QtWidgets.QSpinBox()
        self.spin_auto_save.setRange(0, 60)
        self.spin_auto_save.setValue(int(init.get("auto_save_interval", 5)))
        self.spin_auto_save.setSuffix(" min")

        self.chk_osnap = QtWidgets.QCheckBox()
        self.chk_osnap.setChecked(bool(init.get("enable_osnap", True)))

        form.addRow("Show grid", self.chk_grid)
        form.addRow("Snap to grid/step", self.chk_snap)
        form.addRow("Theme", self.cmb_theme)
        form.addRow("Pixels per foot", self.spin_ppf)
        form.addRow("Enable AI Assistant", self.chk_ai)
        form.addRow("Show Project Overview on startup", self.chk_proj_overview)

        # CAD Functionality
        form.addRow("Units", self.cmb_units)
        form.addRow("Drawing Scale", self.cmb_scale)
        form.addRow("Default Line Weight", self.spin_line_weight)
        form.addRow("Default Color", self.le_default_color)

        # Menus and Tables
        form.addRow("Show Device Palette", self.chk_device_palette)
        form.addRow("Show Properties Dock", self.chk_properties_dock)
        form.addRow("Show Status Bar", self.chk_status_bar)

        # Additional
        form.addRow("Auto-save Interval", self.spin_auto_save)
        form.addRow("Enable OSNAP", self.chk_osnap)

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def values(self):
        return {
            "show_grid": self.chk_grid.isChecked(),
            "snap": self.chk_snap.isChecked(),
            "theme": self.cmb_theme.currentText(),
            "px_per_ft": float(self.spin_ppf.value()),
            "ai_enabled": self.chk_ai.isChecked(),
            "show_project_overview_window": self.chk_proj_overview.isChecked(),
            "units": self.cmb_units.currentText(),
            "drawing_scale": self.cmb_scale.currentText(),
            "default_line_weight": self.spin_line_weight.value(),
            "default_color": self.le_default_color.text(),
            "show_device_palette": self.chk_device_palette.isChecked(),
            "show_properties_dock": self.chk_properties_dock.isChecked(),
            "show_status_bar": self.chk_status_bar.isChecked(),
            "auto_save_interval": self.spin_auto_save.value(),
            "enable_osnap": self.chk_osnap.isChecked(),
        }
