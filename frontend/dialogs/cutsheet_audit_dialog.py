from __future__ import annotations

import csv

from PySide6 import QtCore, QtWidgets


class CutsheetAuditDialog(QtWidgets.QDialog):
    """Dialog to display cutsheet audit results and allow per-item downloads.

    Expects rows in the form: [name, manufacturer, part_number, local_path, url, missing]
    """

    def __init__(self, parent=None, rows: list[list[str]] = None, device_docs_module=None):
        super().__init__(parent)
        self.setWindowTitle("Cutsheet Audit")
        self.resize(900, 480)
        self.rows = rows or []
        self.device_docs = device_docs_module

        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                "Name",
                "Manufacturer",
                "Part Number",
                "Local Path",
                "URL",
                "Missing",
            ]
        )
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        self._populate_table()

        self.save_btn = QtWidgets.QPushButton("Save CSV")
        self.download_btn = QtWidgets.QPushButton("Download Selected")
        self.close_btn = QtWidgets.QPushButton("Close")

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.table)
        main_layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self._save_csv)
        self.download_btn.clicked.connect(self._download_selected)
        self.close_btn.clicked.connect(self.accept)

    def _populate_table(self):
        self.table.setRowCount(len(self.rows))
        for r, row in enumerate(self.rows):
            for c, val in enumerate(row[:6]):
                it = QtWidgets.QTableWidgetItem(val)
                self.table.setItem(r, c, it)

    def _save_csv(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Audit CSV",
            "artifacts/cutsheet_audit.csv",
            "CSV Files (*.csv);;All Files (*)",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["name", "manufacturer", "part_number", "local_path", "url", "missing"])
                for row in self.rows:
                    w.writerow(row)
            QtWidgets.QMessageBox.information(self, "Saved", f"Audit saved to: {path}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Save Failed", str(e))

    def _download_selected(self):
        if not self.device_docs:
            QtWidgets.QMessageBox.warning(self, "Unavailable", "Download facility not available.")
            return

        sel = self.table.selectionModel().selectedRows()
        if not sel:
            QtWidgets.QMessageBox.information(
                self, "No Selection", "Select one or more rows to download."
            )
            return

        downloaded = 0
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            for model_index in sel:
                r = model_index.row()
                url_item = self.table.item(r, 4)
                local_item = self.table.item(r, 3)
                if not url_item:
                    continue
                url = url_item.text().strip()
                if not url:
                    continue
                try:
                    got = self.device_docs.download_doc(url)
                    if got:
                        downloaded += 1
                        # update local path cell and model-row storage
                        local_item_text = got
                        if local_item:
                            local_item.setText(local_item_text)
                        # also update internal rows list
                        self.rows[r][3] = local_item_text
                except Exception:
                    # continue on failure
                    pass
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        QtWidgets.QMessageBox.information(
            self, "Download Complete", f"Downloaded {downloaded} documents."
        )
