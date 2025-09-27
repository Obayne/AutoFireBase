from PySide6 import QtCore, QtWidgets

import db.loader as db_loader


class JobInfoDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Job Information")
        self.setModal(True)
        self.resize(500, 400)

        self.main_window = parent
        self.job_info = {}

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Job Information")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Job information form
        form_group = QtWidgets.QGroupBox("Project Details")
        form_layout = QtWidgets.QFormLayout(form_group)

        self.project_name_edit = QtWidgets.QLineEdit()
        form_layout.addRow("Project Name:", self.project_name_edit)

        self.project_number_edit = QtWidgets.QLineEdit()
        form_layout.addRow("Project Number:", self.project_number_edit)

        self.client_name_edit = QtWidgets.QLineEdit()
        form_layout.addRow("Client Name:", self.client_name_edit)

        self.project_address_edit = QtWidgets.QLineEdit()
        form_layout.addRow("Project Address:", self.project_address_edit)

        self.drawing_date_edit = QtWidgets.QDateEdit()
        self.drawing_date_edit.setCalendarPopup(True)
        self.drawing_date_edit.setDate(QtCore.QDate.currentDate())
        form_layout.addRow("Drawing Date:", self.drawing_date_edit)

        self.drawn_by_edit = QtWidgets.QLineEdit()
        form_layout.addRow("Drawn By:", self.drawn_by_edit)

        self.sheet_number_edit = QtWidgets.QLineEdit()
        form_layout.addRow("Sheet Number:", self.sheet_number_edit)

        self.scale_edit = QtWidgets.QLineEdit()
        self.scale_edit.setText("1\" = 10'")
        form_layout.addRow("Scale:", self.scale_edit)

        layout.addWidget(form_group)

        # Drawing standards
        standards_group = QtWidgets.QGroupBox("Drawing Standards")
        standards_layout = QtWidgets.QFormLayout(standards_group)

        self.standard_combo = QtWidgets.QComboBox()
        self.standard_combo.addItems(["NFPA 72", "NFPA 13", "Local Standards", "Other"])
        standards_layout.addRow("Standard:", self.standard_combo)

        layout.addWidget(standards_group)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.load_btn = QtWidgets.QPushButton("Load from Database")
        self.load_btn.clicked.connect(self.load_from_database)
        button_layout.addWidget(self.load_btn)

        self.save_btn = QtWidgets.QPushButton("Save to Database")
        self.save_btn.clicked.connect(self.save_to_database)
        button_layout.addWidget(self.save_btn)

        button_layout.addStretch()

        self.ok_btn = QtWidgets.QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # Load existing job info
        self.load_from_database()

    def load_from_database(self):
        """Load job information from the database."""
        try:
            con = db_loader.connect()
            self.job_info = db_loader.fetch_job_info(con)
            con.close()

            # Populate fields
            self.project_name_edit.setText(self.job_info.get("project_name", ""))
            self.project_number_edit.setText(self.job_info.get("project_number", ""))
            self.client_name_edit.setText(self.job_info.get("client_name", ""))
            self.project_address_edit.setText(self.job_info.get("project_address", ""))

            # Handle date
            date_str = self.job_info.get("drawing_date", "")
            if date_str:
                date = QtCore.QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    self.drawing_date_edit.setDate(date)

            self.drawn_by_edit.setText(self.job_info.get("drawn_by", ""))
            self.sheet_number_edit.setText(self.job_info.get("sheet_number", ""))

            # Set standard
            standard = self.job_info.get("standard", "NFPA 72")
            index = self.standard_combo.findText(standard)
            if index >= 0:
                self.standard_combo.setCurrentIndex(index)

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Load Error", f"Failed to load job information: {str(e)}"
            )

    def save_to_database(self):
        """Save job information to the database."""
        try:
            # Collect data from form
            project_name = self.project_name_edit.text()
            project_number = self.project_number_edit.text()
            client_name = self.client_name_edit.text()
            project_address = self.project_address_edit.text()
            drawing_date = self.drawing_date_edit.date().toString("yyyy-MM-dd")
            drawn_by = self.drawn_by_edit.text()
            sheet_number = self.sheet_number_edit.text()
            standard = self.standard_combo.currentText()

            # Save to database
            con = db_loader.connect()
            db_loader.save_job_info(
                con, project_name, project_address, sheet_number, drawing_date, drawn_by
            )
            con.close()

            QtWidgets.QMessageBox.information(
                self, "Save Success", "Job information saved successfully."
            )

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Save Error", f"Failed to save job information: {str(e)}"
            )

    def get_job_info(self):
        """Return the current job information."""
        return {
            "project_name": self.project_name_edit.text(),
            "project_number": self.project_number_edit.text(),
            "client_name": self.client_name_edit.text(),
            "project_address": self.project_address_edit.text(),
            "drawing_date": self.drawing_date_edit.date().toString("yyyy-MM-dd"),
            "drawn_by": self.drawn_by_edit.text(),
            "sheet_number": self.sheet_number_edit.text(),
            "standard": self.standard_combo.currentText(),
        }
