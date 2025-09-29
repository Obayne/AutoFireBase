from PySide6 import QtWidgets


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, init=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        init = init or {}
        self.setMinimumWidth(500)

        # Create tab widget for organized settings
        tab_widget = QtWidgets.QTabWidget()

        # General tab
        general_tab = self._create_general_tab(init)
        tab_widget.addTab(general_tab, "General")

        # UI tab
        ui_tab = self._create_ui_tab(init)
        tab_widget.addTab(ui_tab, "User Interface")

        # Drawing tab
        drawing_tab = self._create_drawing_tab(init)
        tab_widget.addTab(drawing_tab, "Drawing")

        # Tool Palettes tab
        palettes_tab = self._create_palettes_tab(init)
        tab_widget.addTab(palettes_tab, "Tool Palettes")

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(tab_widget)

        # Buttons
        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _create_general_tab(self, init):
        """Create the general settings tab."""
        widget = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(widget)

        self.chk_grid = QtWidgets.QCheckBox()
        self.chk_grid.setChecked(bool(init.get("show_grid", True)))
        form.addRow("Show grid", self.chk_grid)

        self.chk_snap = QtWidgets.QCheckBox()
        self.chk_snap.setChecked(bool(init.get("snap", True)))
        form.addRow("Snap to grid/step", self.chk_snap)

        self.chk_coverage = QtWidgets.QCheckBox()
        self.chk_coverage.setChecked(bool(init.get("show_coverage", True)))
        form.addRow("Show coverage overlays", self.chk_coverage)

        self.chk_placement_coverage = QtWidgets.QCheckBox()
        self.chk_placement_coverage.setChecked(bool(init.get("show_placement_coverage", True)))
        form.addRow("Show placement coverage", self.chk_placement_coverage)

        self.spin_ppf = QtWidgets.QDoubleSpinBox()
        self.spin_ppf.setRange(1.0, 2000.0)
        self.spin_ppf.setDecimals(2)
        self.spin_ppf.setValue(float(init.get("px_per_ft", 12.0)))
        form.addRow("Pixels per foot", self.spin_ppf)

        return widget

    def _create_ui_tab(self, init):
        """Create the UI settings tab."""
        widget = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(widget)

        self.cmb_theme = QtWidgets.QComboBox()
        self.cmb_theme.addItems(["dark", "light", "high_contrast", "blue", "green"])
        self.cmb_theme.setCurrentText(init.get("theme") or "dark")
        form.addRow("Theme", self.cmb_theme)

        self.chk_status_bar = QtWidgets.QCheckBox()
        self.chk_status_bar.setChecked(bool(init.get("show_status_bar", True)))
        form.addRow("Show status bar", self.chk_status_bar)

        self.chk_toolbar = QtWidgets.QCheckBox()
        self.chk_toolbar.setChecked(bool(init.get("show_toolbar", True)))
        form.addRow("Show main toolbar", self.chk_toolbar)

        self.chk_command_line = QtWidgets.QCheckBox()
        self.chk_command_line.setChecked(bool(init.get("show_command_line", True)))
        form.addRow("Show command line palette", self.chk_command_line)

        return widget

    def _create_drawing_tab(self, init):
        """Create the drawing settings tab."""
        widget = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(widget)

        self.chk_crosshair = QtWidgets.QCheckBox()
        self.chk_crosshair.setChecked(bool(init.get("show_crosshair", True)))
        form.addRow("Show crosshair cursor", self.chk_crosshair)

        self.chk_ortho = QtWidgets.QCheckBox()
        self.chk_ortho.setChecked(bool(init.get("ortho_mode", False)))
        form.addRow("Orthogonal mode (ortho)", self.chk_ortho)

        self.spin_line_width = QtWidgets.QSpinBox()
        self.spin_line_width.setRange(1, 10)
        self.spin_line_width.setValue(int(init.get("default_line_width", 2)))
        form.addRow("Default line width", self.spin_line_width)

        self.cmb_line_style = QtWidgets.QComboBox()
        self.cmb_line_style.addItems(["solid", "dashed", "dotted", "dash-dot"])
        self.cmb_line_style.setCurrentText(init.get("default_line_style", "solid"))
        form.addRow("Default line style", self.cmb_line_style)

        return widget

    def _create_palettes_tab(self, init):
        """Create the tool palettes visibility tab."""
        widget = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(widget)

        self.chk_device_palette = QtWidgets.QCheckBox()
        self.chk_device_palette.setChecked(bool(init.get("show_device_palette", True)))
        form.addRow("Device Manager palette", self.chk_device_palette)

        self.chk_drawing_tools = QtWidgets.QCheckBox()
        self.chk_drawing_tools.setChecked(bool(init.get("show_drawing_tools", True)))
        form.addRow("Drawing Tools palette", self.chk_drawing_tools)

        self.chk_modify_tools = QtWidgets.QCheckBox()
        self.chk_modify_tools.setChecked(bool(init.get("show_modify_tools", True)))
        form.addRow("Modify Tools palette", self.chk_modify_tools)

        self.chk_annotation_tools = QtWidgets.QCheckBox()
        self.chk_annotation_tools.setChecked(bool(init.get("show_annotation_tools", True)))
        form.addRow("Annotation Tools palette", self.chk_annotation_tools)

        self.chk_layer_tools = QtWidgets.QCheckBox()
        self.chk_layer_tools.setChecked(bool(init.get("show_layer_tools", True)))
        form.addRow("Layer Tools palette", self.chk_layer_tools)

        self.chk_system_info = QtWidgets.QCheckBox()
        self.chk_system_info.setChecked(bool(init.get("show_system_info", True)))
        form.addRow("System Info palette", self.chk_system_info)

        return widget

    def values(self):
        return {
            # General
            "show_grid": self.chk_grid.isChecked(),
            "snap": self.chk_snap.isChecked(),
            "show_coverage": self.chk_coverage.isChecked(),
            "show_placement_coverage": self.chk_placement_coverage.isChecked(),
            "px_per_ft": float(self.spin_ppf.value()),
            # UI
            "theme": self.cmb_theme.currentText(),
            "show_status_bar": self.chk_status_bar.isChecked(),
            "show_toolbar": self.chk_toolbar.isChecked(),
            "show_command_line": self.chk_command_line.isChecked(),
            # Drawing
            "show_crosshair": self.chk_crosshair.isChecked(),
            "ortho_mode": self.chk_ortho.isChecked(),
            "default_line_width": self.spin_line_width.value(),
            "default_line_style": self.cmb_line_style.currentText(),
            # Tool Palettes
            "show_device_palette": self.chk_device_palette.isChecked(),
            "show_drawing_tools": self.chk_drawing_tools.isChecked(),
            "show_modify_tools": self.chk_modify_tools.isChecked(),
            "show_annotation_tools": self.chk_annotation_tools.isChecked(),
            "show_layer_tools": self.chk_layer_tools.isChecked(),
            "show_system_info": self.chk_system_info.isChecked(),
        }
