from PySide6 import QtCore, QtWidgets

DEFAULTS = {
    "quick_tools_enabled": True,
    "quick_tools_items": [
        "draw_line",
        "draw_rect",
        "draw_circle",
        "wiring_mode",
        "ortho_always",
        "toggle_snap",
        "align_submenu"
    ],
    "theme": "Light",
    "quick_tools_filter_visibility": False  # when True, only show enabled items in menus/toolbars
}

TOOL_LABELS = {
    "draw_line": "Draw Line",
    "draw_rect": "Draw Rect",
    "draw_circle": "Draw Circle",
    "wiring_mode": "Wiring Mode",
    "ortho_always": "Ortho Always (wires)",
    "toggle_snap": "Snap On/Off",
    "align_submenu": "Align / Distribute"
}

THEMES = ["Light", "Dark", "High Contrast (Dark)"]

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, prefs: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.prefs = prefs
        self.resize(480, 560)

        layout = QtWidgets.QVBoxLayout(self)

        # Theme
        theme_grp = QtWidgets.QGroupBox("Appearance")
        v0 = QtWidgets.QFormLayout(theme_grp)
        self.cmb_theme = QtWidgets.QComboBox()
        self.cmb_theme.addItems(THEMES)
        current_theme = str(self.prefs.get("theme", DEFAULTS["theme"]))
        if current_theme in THEMES:
            self.cmb_theme.setCurrentIndex(THEMES.index(current_theme))
        v0.addRow("Theme:", self.cmb_theme)
        layout.addWidget(theme_grp)

        # Visibility behavior
        vis_grp = QtWidgets.QGroupBox("Menus & Toolbars")
        vvis = QtWidgets.QVBoxLayout(vis_grp)
        self.chk_filter_vis = QtWidgets.QCheckBox("Only show enabled tools in menus/toolbars")
        self.chk_filter_vis.setChecked(bool(self.prefs.get("quick_tools_filter_visibility", DEFAULTS["quick_tools_filter_visibility"])))
        help_lbl = QtWidgets.QLabel("When on: drawing actions mirror the enabled list below. Core toggles (Grid/Snap/Wiring/Layers) always remain visible.")
        help_lbl.setWordWrap(True)
        vvis.addWidget(self.chk_filter_vis)
        vvis.addWidget(help_lbl)
        layout.addWidget(vis_grp)

        # Right-click Quick Tools
        grp = QtWidgets.QGroupBox("Right-click Quick Tools")
        v = QtWidgets.QVBoxLayout(grp)
        self.chk_enable = QtWidgets.QCheckBox("Enable quick tools menu on right-click")
        self.chk_enable.setChecked(bool(self.prefs.get("quick_tools_enabled", DEFAULTS["quick_tools_enabled"])))
        v.addWidget(self.chk_enable)

        v.addWidget(QtWidgets.QLabel("Show these items:"))
        self.list = QtWidgets.QListWidget()
        self.list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        v.addWidget(self.list, 1)

        # populate checkboxes
        items = list(TOOL_LABELS.keys())
        current = set(self.prefs.get("quick_tools_items", DEFAULTS["quick_tools_items"]))
        for key in items:
            it = QtWidgets.QListWidgetItem(TOOL_LABELS[key])
            it.setFlags(it.flags() | QtCore.Qt.ItemIsUserCheckable)
            it.setCheckState(QtCore.Qt.Checked if key in current else QtCore.Qt.Unchecked)
            it.setData(QtCore.Qt.UserRole, key)
            self.list.addItem(it)

        layout.addWidget(grp, 1)

        # Buttons
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(bb)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

    def apply(self):
        self.prefs["quick_tools_enabled"] = bool(self.chk_enable.isChecked())
        chosen = []
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.checkState() == QtCore.Qt.Checked:
                chosen.append(it.data(QtCore.Qt.UserRole))
        self.prefs["quick_tools_items"] = chosen
        self.prefs["theme"] = self.cmb_theme.currentText()
        self.prefs["quick_tools_filter_visibility"] = bool(self.chk_filter_vis.isChecked())
        return self.prefs
