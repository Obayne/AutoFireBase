from PySide6 import QtWidgets

import db.loader as db_loader


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(800, 600)

        self.main_window = parent

        layout = QtWidgets.QVBoxLayout(self)

        # Create tab widget for different settings categories
        tab_widget = QtWidgets.QTabWidget()
        layout.addWidget(tab_widget)

        # General settings tab
        self.general_tab = self.create_general_tab()
        tab_widget.addTab(self.general_tab, "General")

        # CAD settings tab
        self.cad_tab = self.create_cad_tab()
        tab_widget.addTab(self.cad_tab, "CAD")

        # Display settings tab
        self.display_tab = self.create_display_tab()
        tab_widget.addTab(self.display_tab, "Display")

        # Project settings tab
        self.project_tab = self.create_project_tab()
        tab_widget.addTab(self.project_tab, "Project")

        # Database settings tab
        self.database_tab = self.create_database_tab()
        tab_widget.addTab(self.database_tab, "Database")

        # Add OK and Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_pref(self, key, default=None):
        """Safely get a preference value from the main window"""
        if self.main_window and hasattr(self.main_window, "prefs"):
            value = self.main_window.prefs.get(key, default)
            # Ensure we return a proper value, not None
            return value if value is not None else default
        return default

    def create_general_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Theme settings
        theme_group = QtWidgets.QGroupBox("Theme")
        theme_layout = QtWidgets.QFormLayout(theme_group)

        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "High Contrast"])
        theme_value = self.get_pref("theme", "dark")
        if theme_value:
            self.theme_combo.setCurrentText(str(theme_value).title())
        else:
            self.theme_combo.setCurrentText("Dark")
        theme_layout.addRow("Theme:", self.theme_combo)

        self.primary_color_button = QtWidgets.QPushButton("Select Primary Color")
        self.primary_color_button.clicked.connect(self.select_primary_color)
        theme_layout.addRow("Primary Color:", self.primary_color_button)

        layout.addWidget(theme_group)

        # Units settings
        units_group = QtWidgets.QGroupBox("Units")
        units_layout = QtWidgets.QFormLayout(units_group)

        self.units_combo = QtWidgets.QComboBox()
        self.units_combo.addItems(["Feet & Inches", "Meters", "Millimeters"])
        units_value = self.get_pref("units", "Feet & Inches")
        self.units_combo.setCurrentText(str(units_value) if units_value else "Feet & Inches")
        units_layout.addRow("Default Units:", self.units_combo)

        layout.addWidget(units_group)

        # Project settings
        project_group = QtWidgets.QGroupBox("Project")
        project_layout = QtWidgets.QFormLayout(project_group)

        self.default_strobe_diameter = QtWidgets.QDoubleSpinBox()
        self.default_strobe_diameter.setRange(10.0, 200.0)
        self.default_strobe_diameter.setSingleStep(5.0)
        strobe_value = self.get_pref("default_strobe_diameter_ft", 50.0)
        self.default_strobe_diameter.setValue(
            float(strobe_value) if strobe_value is not None else 50.0
        )
        project_layout.addRow("Default Strobe Diameter (ft):", self.default_strobe_diameter)

        self.default_smoke_spacing = QtWidgets.QDoubleSpinBox()
        self.default_smoke_spacing.setRange(10.0, 100.0)
        self.default_smoke_spacing.setSingleStep(5.0)
        smoke_value = self.get_pref("default_smoke_spacing_ft", 30.0)
        self.default_smoke_spacing.setValue(float(smoke_value) if smoke_value is not None else 30.0)
        project_layout.addRow("Default Smoke Spacing (ft):", self.default_smoke_spacing)

        layout.addWidget(project_group)
        layout.addStretch()

        return widget

    def create_cad_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Grid settings
        grid_group = QtWidgets.QGroupBox("Grid")
        grid_layout = QtWidgets.QFormLayout(grid_group)

        self.grid_size = QtWidgets.QSpinBox()
        self.grid_size.setRange(1, 100)
        grid_value = self.get_pref("grid", 10)
        self.grid_size.setValue(int(grid_value) if grid_value is not None else 10)
        grid_layout.addRow("Grid Size:", self.grid_size)

        self.snap_enabled = QtWidgets.QCheckBox("Enable Snap")
        snap_value = self.get_pref("snap", True)
        self.snap_enabled.setChecked(bool(snap_value))
        grid_layout.addRow("Snap:", self.snap_enabled)

        self.snap_step = QtWidgets.QDoubleSpinBox()
        self.snap_step.setRange(0.0, 12.0)
        self.snap_step.setSingleStep(0.125)
        step_value = self.get_pref("snap_step_in", 0.0)
        self.snap_step.setValue(float(step_value) if step_value is not None else 0.0)
        grid_layout.addRow("Snap Step (inches):", self.snap_step)

        layout.addWidget(grid_group)

        # Drawing settings
        drawing_group = QtWidgets.QGroupBox("Drawing")
        drawing_layout = QtWidgets.QFormLayout(drawing_group)

        self.default_line_width = QtWidgets.QDoubleSpinBox()
        self.default_line_width.setRange(0.1, 5.0)
        self.default_line_width.setSingleStep(0.1)
        line_width_value = self.get_pref("default_line_width", 1.0)
        self.default_line_width.setValue(
            float(line_width_value) if line_width_value is not None else 1.0
        )
        drawing_layout.addRow("Default Line Width:", self.default_line_width)

        self.default_text_size = QtWidgets.QDoubleSpinBox()
        self.default_text_size.setRange(1.0, 100.0)
        self.default_text_size.setSingleStep(1.0)
        text_size_value = self.get_pref("default_text_size", 12.0)
        self.default_text_size.setValue(
            float(text_size_value) if text_size_value is not None else 12.0
        )
        drawing_layout.addRow("Default Text Size:", self.default_text_size)

        layout.addWidget(drawing_group)

        # OSNAP settings
        osnap_group = QtWidgets.QGroupBox("Object Snap (OSNAP)")
        osnap_layout = QtWidgets.QVBoxLayout(osnap_group)

        self.osnap_end = QtWidgets.QCheckBox("Endpoint")
        osnap_end_value = self.get_pref("osnap_end", True)
        self.osnap_end.setChecked(bool(osnap_end_value))
        osnap_layout.addWidget(self.osnap_end)

        self.osnap_mid = QtWidgets.QCheckBox("Midpoint")
        osnap_mid_value = self.get_pref("osnap_mid", True)
        self.osnap_mid.setChecked(bool(osnap_mid_value))
        osnap_layout.addWidget(self.osnap_mid)

        self.osnap_center = QtWidgets.QCheckBox("Center")
        osnap_center_value = self.get_pref("osnap_center", True)
        self.osnap_center.setChecked(bool(osnap_center_value))
        osnap_layout.addWidget(self.osnap_center)

        self.osnap_intersect = QtWidgets.QCheckBox("Intersection")
        osnap_intersect_value = self.get_pref("osnap_intersect", True)
        self.osnap_intersect.setChecked(bool(osnap_intersect_value))
        osnap_layout.addWidget(self.osnap_intersect)

        self.osnap_perp = QtWidgets.QCheckBox("Perpendicular")
        osnap_perp_value = self.get_pref("osnap_perp", False)
        self.osnap_perp.setChecked(bool(osnap_perp_value))
        osnap_layout.addWidget(self.osnap_perp)

        layout.addWidget(osnap_group)
        layout.addStretch()

        return widget

    def create_display_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # View settings
        view_group = QtWidgets.QGroupBox("View")
        view_layout = QtWidgets.QFormLayout(view_group)

        self.px_per_ft = QtWidgets.QDoubleSpinBox()
        self.px_per_ft.setRange(1.0, 1000.0)
        self.px_per_ft.setSingleStep(1.0)
        px_per_ft_value = self.get_pref("px_per_ft", 12.0)
        self.px_per_ft.setValue(float(px_per_ft_value) if px_per_ft_value is not None else 12.0)
        view_layout.addRow("Pixels per Foot:", self.px_per_ft)

        self.show_crosshair = QtWidgets.QCheckBox("Show Crosshair")
        crosshair_value = self.get_pref("show_crosshair", True)
        self.show_crosshair.setChecked(bool(crosshair_value))
        view_layout.addRow("Crosshair:", self.show_crosshair)

        layout.addWidget(view_group)

        # Coverage settings
        coverage_group = QtWidgets.QGroupBox("Coverage Display")
        coverage_layout = QtWidgets.QFormLayout(coverage_group)

        self.show_placement_coverage = QtWidgets.QCheckBox("Show Placement Coverage")
        coverage_value = self.get_pref("show_placement_coverage", True)
        self.show_placement_coverage.setChecked(bool(coverage_value))
        coverage_layout.addRow("Placement Coverage:", self.show_placement_coverage)

        layout.addWidget(coverage_group)

        # Print settings
        print_group = QtWidgets.QGroupBox("Print")
        print_layout = QtWidgets.QFormLayout(print_group)

        self.print_dpi = QtWidgets.QSpinBox()
        self.print_dpi.setRange(72, 1200)
        self.print_dpi.setSingleStep(72)
        dpi_value = self.get_pref("print_dpi", 300)
        self.print_dpi.setValue(int(dpi_value) if dpi_value is not None else 300)
        print_layout.addRow("Print DPI:", self.print_dpi)

        self.page_margin = QtWidgets.QDoubleSpinBox()
        self.page_margin.setRange(0.0, 2.0)
        self.page_margin.setSingleStep(0.1)
        margin_value = self.get_pref("page_margin_in", 0.5)
        self.page_margin.setValue(float(margin_value) if margin_value is not None else 0.5)
        print_layout.addRow("Page Margin (inches):", self.page_margin)

        layout.addWidget(print_group)
        layout.addStretch()

        return widget

    def create_project_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Project information
        project_group = QtWidgets.QGroupBox("Project Information")
        project_layout = QtWidgets.QFormLayout(project_group)

        self.project_name = QtWidgets.QLineEdit()
        project_name_value = self.get_pref("project_name", "")
        self.project_name.setText(str(project_name_value) if project_name_value else "")
        project_layout.addRow("Project Name:", self.project_name)

        self.project_number = QtWidgets.QLineEdit()
        project_number_value = self.get_pref("project_number", "")
        self.project_number.setText(str(project_number_value) if project_number_value else "")
        project_layout.addRow("Project Number:", self.project_number)

        self.client_name = QtWidgets.QLineEdit()
        client_name_value = self.get_pref("client_name", "")
        self.client_name.setText(str(client_name_value) if client_name_value else "")
        project_layout.addRow("Client Name:", self.client_name)

        layout.addWidget(project_group)

        # Drawing standards
        standards_group = QtWidgets.QGroupBox("Drawing Standards")
        standards_layout = QtWidgets.QFormLayout(standards_group)

        self.drawing_standard = QtWidgets.QComboBox()
        self.drawing_standard.addItems(["NFPA 72", "NFPA 13", "Local Standards", "Other"])
        standard_value = self.get_pref("drawing_standard", "NFPA 72")
        self.drawing_standard.setCurrentText(str(standard_value) if standard_value else "NFPA 72")
        standards_layout.addRow("Standard:", self.drawing_standard)

        layout.addWidget(standards_group)
        layout.addStretch()

        return widget

    def create_database_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Database connection
        db_group = QtWidgets.QGroupBox("Database Connection")
        db_layout = QtWidgets.QFormLayout(db_group)

        self.db_path = QtWidgets.QLineEdit()
        db_path_value = self.get_pref("db_path", "")
        self.db_path.setText(str(db_path_value) if db_path_value else "")
        db_layout.addRow("Database Path:", self.db_path)

        self.browse_db_button = QtWidgets.QPushButton("Browse...")
        self.browse_db_button.clicked.connect(self.browse_database)
        db_layout.addRow("", self.browse_db_button)

        layout.addWidget(db_group)

        # Database operations
        operations_group = QtWidgets.QGroupBox("Database Operations")
        operations_layout = QtWidgets.QVBoxLayout(operations_group)

        self.seed_demo_button = QtWidgets.QPushButton("Seed Demo Data")
        self.seed_demo_button.clicked.connect(self.seed_demo_data)
        operations_layout.addWidget(self.seed_demo_button)

        self.reset_db_button = QtWidgets.QPushButton("Reset Database")
        self.reset_db_button.clicked.connect(self.reset_database)
        operations_layout.addWidget(self.reset_db_button)

        layout.addWidget(operations_group)
        layout.addStretch()

        return widget

    def select_primary_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid() and self.main_window:
            if not hasattr(self.main_window, "prefs"):
                self.main_window.prefs = {}
            self.main_window.prefs["primary_color"] = color.name()
            self.main_window.set_theme(self.main_window.prefs.get("theme", "dark"))

    def browse_database(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Database File", "", "Database Files (*.db *.sqlite);;All Files (*)"
        )
        if file_path:
            self.db_path.setText(file_path)

    def seed_demo_data(self):
        try:
            db_path = self.db_path.text()
            con = db_loader.connect(db_path if db_path else "")
            db_loader.seed_demo(con)
            con.close()
            QtWidgets.QMessageBox.information(self, "Success", "Demo data seeded successfully.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to seed demo data: {str(e)}")

    def reset_database(self):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset the database? This will delete all data.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                db_path = self.db_path.text()
                con = db_loader.connect(db_path if db_path else "")
                # This would require a reset function in db_loader
                # For now, we'll just show a message
                con.close()
                QtWidgets.QMessageBox.information(
                    self, "Reset", "Database reset functionality would go here."
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to reset database: {str(e)}")

    def accept(self):
        if not self.main_window:
            super().accept()
            return

        # Ensure prefs exists
        if not hasattr(self.main_window, "prefs"):
            self.main_window.prefs = {}

        # Save general settings
        self.main_window.prefs["theme"] = self.theme_combo.currentText().lower()
        self.main_window.prefs["units"] = self.units_combo.currentText()
        self.main_window.prefs["default_strobe_diameter_ft"] = float(
            self.default_strobe_diameter.value()
        )
        self.main_window.prefs["default_smoke_spacing_ft"] = float(
            self.default_smoke_spacing.value()
        )

        # Save CAD settings
        self.main_window.prefs["grid"] = int(self.grid_size.value())
        self.main_window.prefs["snap"] = bool(self.snap_enabled.isChecked())
        self.main_window.prefs["snap_step_in"] = float(self.snap_step.value())
        self.main_window.prefs["default_line_width"] = float(self.default_line_width.value())
        self.main_window.prefs["default_text_size"] = float(self.default_text_size.value())
        self.main_window.prefs["osnap_end"] = bool(self.osnap_end.isChecked())
        self.main_window.prefs["osnap_mid"] = bool(self.osnap_mid.isChecked())
        self.main_window.prefs["osnap_center"] = bool(self.osnap_center.isChecked())
        self.main_window.prefs["osnap_intersect"] = bool(self.osnap_intersect.isChecked())
        self.main_window.prefs["osnap_perp"] = bool(self.osnap_perp.isChecked())

        # Save display settings
        self.main_window.prefs["px_per_ft"] = float(self.px_per_ft.value())
        self.main_window.prefs["show_crosshair"] = bool(self.show_crosshair.isChecked())
        self.main_window.prefs["show_placement_coverage"] = bool(
            self.show_placement_coverage.isChecked()
        )
        self.main_window.prefs["print_dpi"] = int(self.print_dpi.value())
        self.main_window.prefs["page_margin_in"] = float(self.page_margin.value())

        # Save project settings
        self.main_window.prefs["project_name"] = self.project_name.text()
        self.main_window.prefs["project_number"] = self.project_number.text()
        self.main_window.prefs["client_name"] = self.client_name.text()
        self.main_window.prefs["drawing_standard"] = self.drawing_standard.currentText()

        # Save database settings
        self.main_window.prefs["db_path"] = self.db_path.text()

        # Apply settings
        self.main_window.set_theme(self.main_window.prefs["theme"])

        if hasattr(self.main_window, "scene"):
            self.main_window.scene.grid_size = int(self.main_window.prefs["grid"])
            self.main_window.scene.snap_enabled = bool(self.main_window.prefs["snap"])

        if hasattr(self.main_window, "_apply_snap_step_from_inches"):
            self.main_window._apply_snap_step_from_inches(self.main_window.prefs["snap_step_in"])

        if hasattr(self.main_window, "view"):
            self.main_window.view.show_crosshair = bool(self.main_window.prefs["show_crosshair"])

        if hasattr(self.main_window, "show_coverage"):
            self.main_window.show_coverage = bool(self.main_window.prefs["show_placement_coverage"])

        super().accept()
