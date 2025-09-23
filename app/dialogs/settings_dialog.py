from PySide6 import QtWidgets, QtGui

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 400)

        self.parent = parent

        layout = QtWidgets.QVBoxLayout(self)

        # Theme settings
        theme_group = QtWidgets.QGroupBox("Theme")
        theme_layout = QtWidgets.QFormLayout(theme_group)

        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "High Contrast"])
        self.theme_combo.setCurrentText(self.parent.prefs.get("theme", "dark").title())
        theme_layout.addRow("Theme:", self.theme_combo)

        self.primary_color_button = QtWidgets.QPushButton("Select Primary Color")
        self.primary_color_button.clicked.connect(self.select_primary_color)
        theme_layout.addRow("Primary Color:", self.primary_color_button)

        layout.addWidget(theme_group)

        # Add OK and Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def select_primary_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.parent.prefs["primary_color"] = color.name()
            self.parent.set_theme(self.parent.prefs.get("theme", "dark"))

    def accept(self):
        self.parent.prefs["theme"] = self.theme_combo.currentText().lower()
        self.parent.set_theme(self.parent.prefs["theme"])
        super().accept()
