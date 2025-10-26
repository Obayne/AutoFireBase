from __future__ import annotations

from typing import Any

from PySide6 import QtWidgets

from backend.circuits import summarize_panel_circuits


class CircuitsEditor(QtWidgets.QWidget):
    """Minimal circuits editor: displays computed metrics per circuit.

    For v1: read-only table with a Recompute button.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._device_items: list[Any] = []
        self._wire_items: list[Any] = []

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        top_bar = QtWidgets.QHBoxLayout()
        self.recompute_btn = QtWidgets.QPushButton("Recompute")
        self.recompute_btn.clicked.connect(self.recompute)
        top_bar.addWidget(self.recompute_btn)
        top_bar.addStretch(1)
        layout.addLayout(top_bar)

        self.table = QtWidgets.QTableWidget(0, 9, self)
        self.table.setHorizontalHeaderLabels(
            [
                "Panel",
                "Circuit",
                "Type",
                "Devices",
                "Length (ft)",
                "AWG",
                "Current (A)",
                "VD %",
                "Battery (Ah)",
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def set_data(self, device_items: list[Any], wire_items: list[Any]) -> None:
        self._device_items = device_items or []
        self._wire_items = wire_items or []
        self.recompute()

    def recompute(self) -> None:
        rows = summarize_panel_circuits(self._device_items, self._wire_items)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(row.panel)))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(str(row.circuit_id)))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(str(row.circuit_type)))
            self.table.setItem(r, 3, QtWidgets.QTableWidgetItem(str(row.device_count)))
            self.table.setItem(r, 4, QtWidgets.QTableWidgetItem(f"{row.length_ft:.2f}"))
            self.table.setItem(r, 5, QtWidgets.QTableWidgetItem(str(row.gauge)))
            self.table.setItem(r, 6, QtWidgets.QTableWidgetItem(f"{row.current_a:.3f}"))
            self.table.setItem(r, 7, QtWidgets.QTableWidgetItem(f"{row.drop_percent:.2f}"))
            self.table.setItem(r, 8, QtWidgets.QTableWidgetItem(f"{row.battery_ah:.2f}"))
