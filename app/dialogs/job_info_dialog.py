from PySide6 import QtWidgets, QtCore
from db import loader as db_loader

class JobInfoDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Job Information")
        self.setModal(True)
        self.resize(400, 300)

        self.parent = parent

        layout = QtWidgets.QFormLayout(self)

        self.project_name_edit = QtWidgets.QLineEdit()
        self.project_address_edit = QtWidgets.QLineEdit()
        self.sheet_number_edit = QtWidgets.QLineEdit()
        self.drawing_date_edit = QtWidgets.QLineEdit()
        self.drawn_by_edit = QtWidgets.QLineEdit()

        layout.addRow("Project Name:", self.project_name_edit)
        layout.addRow("Project Address:", self.project_address_edit)
        layout.addRow("Sheet Number:", self.sheet_number_edit)
        layout.addRow("Drawing Date:", self.drawing_date_edit)
        layout.addRow("Drawn By:", self.drawn_by_edit)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.load_job_info()

    def load_job_info(self):
        try:
            con = db_loader.connect()
            job_info = db_loader.fetch_job_info(con)
            con.close()

            self.project_name_edit.setText(job_info.get('project_name', ''))
            self.project_address_edit.setText(job_info.get('project_address', ''))
            self.sheet_number_edit.setText(job_info.get('sheet_number', ''))
            self.drawing_date_edit.setText(job_info.get('drawing_date', ''))
            self.drawn_by_edit.setText(job_info.get('drawn_by', ''))
        except Exception as e:
            print(f"Error loading job info: {e}")

    def accept(self):
        try:
            con = db_loader.connect()
            db_loader.save_job_info(con,
                                    self.project_name_edit.text(),
                                    self.project_address_edit.text(),
                                    self.sheet_number_edit.text(),
                                    self.drawing_date_edit.text(),
                                    self.drawn_by_edit.text())
            con.close()
            # Optionally, trigger a refresh of title block if it's visible
            if self.parent and hasattr(self.parent, 'title_block') and self.parent.title_block:
                self.parent.title_block.set_meta(db_loader.fetch_job_info(db_loader.connect()))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Save Error", f"Failed to save job information: {e}")
            return

        super().accept()
