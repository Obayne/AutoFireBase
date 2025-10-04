"""
Settings Dialog - Comprehensive application preferences and configuration
"""

from typing import Any

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from frontend.ui.theme import apply_theme, get_available_themes


class SettingsDialog(QtWidgets.QDialog):
    """Comprehensive settings dialog for AutoFire application."""

    settings_changed = QtCore.Signal(dict)  # Emitted when settings are applied

    def __init__(self, current_prefs: dict[str, Any], parent=None):
        super().__init__(parent)
        self.current_prefs = current_prefs.copy()
        self.original_prefs = current_prefs.copy()

        self.setWindowTitle("AutoFire Settings")
        self.setModal(True)
        self.setMinimumSize(700, 600)

        self.setup_ui()
        self.load_current_settings()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_general_tab()
        self.create_appearance_tab()
        self.create_cad_tab()
        self.create_workspace_tab()

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.apply_button = QtWidgets.QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        self.apply_button.setDefault(True)
        button_layout.addWidget(self.apply_button)

        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def create_general_tab(self):
        """Create the General settings tab."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        # Units
        units_group = QtWidgets.QGroupBox("Units")
        units_layout = QtWidgets.QVBoxLayout(units_group)

        self.units_combo = QtWidgets.QComboBox()
        self.units_combo.addItems(["Imperial (feet)", "Metric (meters)"])
        units_layout.addWidget(QtWidgets.QLabel("Display Units:"))
        units_layout.addWidget(self.units_combo)

        layout.addWidget(units_group)

        # Auto-save
        autosave_group = QtWidgets.QGroupBox("Auto-Save")
        autosave_layout = QtWidgets.QVBoxLayout(autosave_group)

        self.autosave_spin = QtWidgets.QSpinBox()
        self.autosave_spin.setRange(1, 60)
        self.autosave_spin.setSuffix(" minutes")
        autosave_layout.addWidget(QtWidgets.QLabel("Auto-save interval:"))
        autosave_layout.addWidget(self.autosave_spin)

        layout.addWidget(autosave_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "General")

    def create_appearance_tab(self):
        """Create the Appearance settings tab."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        # Theme selection
        theme_group = QtWidgets.QGroupBox("Theme")
        theme_layout = QtWidgets.QVBoxLayout(theme_group)

        self.theme_combo = QtWidgets.QComboBox()
        themes = get_available_themes()
        for key, name in themes.items():
            self.theme_combo.addItem(name, key)
        theme_layout.addWidget(QtWidgets.QLabel("Application Theme:"))
        theme_layout.addWidget(self.theme_combo)

        # Theme preview
        self.theme_preview = QtWidgets.QTextEdit()
        self.theme_preview.setMaximumHeight(100)
        self.theme_preview.setPlainText(
            "Theme preview - this text shows how the selected theme looks."
        )
        self.theme_preview.setReadOnly(True)
        theme_layout.addWidget(QtWidgets.QLabel("Preview:"))
        theme_layout.addWidget(self.theme_preview)

        layout.addWidget(theme_group)

        # Font settings
        font_group = QtWidgets.QGroupBox("Fonts")
        font_layout = QtWidgets.QVBoxLayout(font_group)

        # Interface font
        iface_font_layout = QtWidgets.QHBoxLayout()
        iface_font_layout.addWidget(QtWidgets.QLabel("Interface:"))

        self.iface_font_button = QtWidgets.QPushButton("Choose Font...")
        self.iface_font_button.clicked.connect(self.choose_interface_font)
        iface_font_layout.addWidget(self.iface_font_button)
        iface_font_layout.addStretch()

        font_layout.addLayout(iface_font_layout)

        # CAD font
        cad_font_layout = QtWidgets.QHBoxLayout()
        cad_font_layout.addWidget(QtWidgets.QLabel("CAD Labels:"))

        self.cad_font_button = QtWidgets.QPushButton("Choose Font...")
        self.cad_font_button.clicked.connect(self.choose_cad_font)
        cad_font_layout.addWidget(self.cad_font_button)
        cad_font_layout.addStretch()

        font_layout.addLayout(cad_font_layout)

        layout.addWidget(font_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Appearance")

    def create_cad_tab(self):
        """Create the CAD settings tab."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        # Grid settings
        grid_group = QtWidgets.QGroupBox("Grid")
        grid_layout = QtWidgets.QVBoxLayout(grid_group)

        # Grid size
        grid_size_layout = QtWidgets.QHBoxLayout()
        grid_size_layout.addWidget(QtWidgets.QLabel("Grid Size (pixels):"))
        self.grid_size_spin = QtWidgets.QSpinBox()
        self.grid_size_spin.setRange(4, 100)
        grid_size_layout.addWidget(self.grid_size_spin)
        grid_size_layout.addStretch()
        grid_layout.addLayout(grid_size_layout)

        # Grid opacity
        grid_opacity_layout = QtWidgets.QHBoxLayout()
        grid_opacity_layout.addWidget(QtWidgets.QLabel("Grid Opacity:"))
        self.grid_opacity_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.grid_opacity_slider.setRange(0, 100)
        grid_opacity_layout.addWidget(self.grid_opacity_slider)
        self.grid_opacity_label = QtWidgets.QLabel("50%")
        grid_opacity_layout.addWidget(self.grid_opacity_label)
        grid_layout.addLayout(grid_opacity_layout)

        # Major grid lines
        major_layout = QtWidgets.QHBoxLayout()
        major_layout.addWidget(QtWidgets.QLabel("Major Grid Every:"))
        self.major_every_spin = QtWidgets.QSpinBox()
        self.major_every_spin.setRange(2, 20)
        major_layout.addWidget(self.major_every_spin)
        major_layout.addWidget(QtWidgets.QLabel("lines"))
        major_layout.addStretch()
        grid_layout.addLayout(major_layout)

        layout.addWidget(grid_group)

        # Drawing settings
        drawing_group = QtWidgets.QGroupBox("Drawing")
        drawing_layout = QtWidgets.QVBoxLayout(drawing_group)

        # Default line weight
        line_weight_layout = QtWidgets.QHBoxLayout()
        line_weight_layout.addWidget(QtWidgets.QLabel("Default Line Weight:"))
        self.line_weight_spin = QtWidgets.QSpinBox()
        self.line_weight_spin.setRange(1, 10)
        line_weight_layout.addWidget(self.line_weight_spin)
        line_weight_layout.addWidget(QtWidgets.QLabel("pixels"))
        line_weight_layout.addStretch()
        drawing_layout.addLayout(line_weight_layout)

        # Snap settings
        self.snap_to_grid_check = QtWidgets.QCheckBox("Snap to Grid")
        drawing_layout.addWidget(self.snap_to_grid_check)

        self.show_coverage_check = QtWidgets.QCheckBox("Show Device Coverage")
        drawing_layout.addWidget(self.show_coverage_check)

        layout.addWidget(drawing_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "CAD")

    def create_workspace_tab(self):
        """Create the Workspace settings tab."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)

        # Window layout
        windows_group = QtWidgets.QGroupBox("Window Layout")
        windows_layout = QtWidgets.QVBoxLayout(windows_group)

        self.show_device_palette_check = QtWidgets.QCheckBox("Show Device Palette")
        self.show_device_palette_check.setChecked(True)
        windows_layout.addWidget(self.show_device_palette_check)

        self.show_properties_check = QtWidgets.QCheckBox("Show Properties Panel")
        self.show_properties_check.setChecked(True)
        windows_layout.addWidget(self.show_properties_check)

        self.show_status_bar_check = QtWidgets.QCheckBox("Show Status Bar")
        self.show_status_bar_check.setChecked(True)
        windows_layout.addWidget(self.show_status_bar_check)

        layout.addWidget(windows_group)

        # Project settings
        project_group = QtWidgets.QGroupBox("Project")
        project_layout = QtWidgets.QVBoxLayout(project_group)

        # Default project location
        project_path_layout = QtWidgets.QHBoxLayout()
        project_path_layout.addWidget(QtWidgets.QLabel("Default Project Location:"))
        self.project_path_edit = QtWidgets.QLineEdit()
        project_path_layout.addWidget(self.project_path_edit)
        self.project_path_button = QtWidgets.QPushButton("Browse...")
        self.project_path_button.clicked.connect(self.choose_project_path)
        project_path_layout.addWidget(self.project_path_button)
        project_layout.addLayout(project_path_layout)

        layout.addWidget(project_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Workspace")

    def load_current_settings(self):
        """Load current settings into the UI."""
        # General
        units = self.current_prefs.get("units", "Imperial (feet)")
        self.units_combo.setCurrentText(units)

        autosave = self.current_prefs.get("auto_save_interval", 5)
        self.autosave_spin.setValue(autosave)

        # Appearance
        theme = self.current_prefs.get("theme", "dark")
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        # CAD
        grid_size = self.current_prefs.get("grid", 24)
        self.grid_size_spin.setValue(grid_size)

        grid_opacity = int(self.current_prefs.get("grid_opacity", 0.35) * 100)
        self.grid_opacity_slider.setValue(grid_opacity)
        self.update_opacity_label(grid_opacity)

        major_every = self.current_prefs.get("grid_major_every", 5)
        self.major_every_spin.setValue(major_every)

        line_weight = self.current_prefs.get("default_line_weight", 1)
        self.line_weight_spin.setValue(line_weight)

        self.snap_to_grid_check.setChecked(self.current_prefs.get("enable_osnap", True))
        self.show_coverage_check.setChecked(self.current_prefs.get("show_coverage", True))

        # Workspace
        self.show_device_palette_check.setChecked(
            self.current_prefs.get("show_device_palette", True)
        )
        self.show_properties_check.setChecked(self.current_prefs.get("show_properties_dock", True))
        self.show_status_bar_check.setChecked(self.current_prefs.get("show_status_bar", True))

        # Connect signals
        self.grid_opacity_slider.valueChanged.connect(self.update_opacity_label)
        self.theme_combo.currentIndexChanged.connect(self.update_theme_preview)

        self.update_theme_preview()

    def update_opacity_label(self, value):
        """Update the opacity label when slider changes."""
        self.grid_opacity_label.setText(f"{value}%")

    def update_theme_preview(self):
        """Update the theme preview when theme changes."""
        theme_key = self.theme_combo.currentData()
        if theme_key:
            # Apply theme temporarily to preview
            theme_data = apply_theme(QtWidgets.QApplication.instance(), theme_key)
            self.theme_preview.setStyleSheet(
                f"""
                QTextEdit {{
                    background-color: {theme_data['colors']['base']};
                    color: {theme_data['colors']['text']};
                    border: 1px solid {theme_data['colors']['border']};
                }}
            """
            )

    def choose_interface_font(self):
        """Choose interface font."""
        current_font = QtGui.QFont()
        if "interface_font" in self.current_prefs:
            current_font.fromString(self.current_prefs["interface_font"])

        font, ok = QtWidgets.QFontDialog.getFont(current_font, self)
        if ok:
            self.current_prefs["interface_font"] = str(font)

    def choose_cad_font(self):
        """Choose CAD font."""
        current_font = QtGui.QFont()
        if "cad_font" in self.current_prefs:
            current_font.fromString(self.current_prefs["cad_font"])

        font, ok = QtWidgets.QFontDialog.getFont(current_font, self)
        if ok:
            self.current_prefs["cad_font"] = str(font)

    def choose_project_path(self):
        """Choose default project path."""
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Choose Default Project Directory",
            self.project_path_edit.text() or QtCore.QDir.homePath(),
        )
        if path:
            self.project_path_edit.setText(path)

    def collect_settings(self) -> dict[str, Any]:
        """Collect all settings from the UI."""
        settings = self.current_prefs.copy()

        # General
        settings["units"] = self.units_combo.currentText()
        settings["auto_save_interval"] = self.autosave_spin.value()

        # Appearance
        settings["theme"] = self.theme_combo.currentData()

        # CAD
        settings["grid"] = self.grid_size_spin.value()
        settings["grid_opacity"] = self.grid_opacity_slider.value() / 100.0
        settings["grid_major_every"] = self.major_every_spin.value()
        settings["default_line_weight"] = self.line_weight_spin.value()
        settings["enable_osnap"] = self.snap_to_grid_check.isChecked()
        settings["show_coverage"] = self.show_coverage_check.isChecked()

        # Workspace
        settings["show_device_palette"] = self.show_device_palette_check.isChecked()
        settings["show_properties_dock"] = self.show_properties_check.isChecked()
        settings["show_status_bar"] = self.show_status_bar_check.isChecked()

        return settings

    def apply_settings(self):
        """Apply settings without closing dialog."""
        self.current_prefs = self.collect_settings()
        self.settings_changed.emit(self.current_prefs)

    def accept_settings(self):
        """Apply settings and close dialog."""
        self.apply_settings()
        self.accept()

    def get_settings(self) -> dict[str, Any]:
        """Get the final settings."""
        return self.current_prefs
