import os
import sqlite3

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class WireSpoolDialog(QDialog):
    """Dialog for managing wire spools and tracking usage."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wire Spool Manager")
        self.setModal(True)
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        # Active spools section
        active_group = QGroupBox("Active Wire Spools")
        active_layout = QVBoxLayout(active_group)

        # Spool list with usage
        self.spool_list = QListWidget()
        self._populate_active_spools()
        active_layout.addWidget(self.spool_list)

        layout.addWidget(active_group)

        # Spool details section
        details_group = QGroupBox("Spool Details")
        details_layout = QVBoxLayout(details_group)

        self.details_table = QTableWidget()
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels(["Property", "Value", "Unit", "Status"])
        self.details_table.horizontalHeader().setStretchLastSection(True)
        details_layout.addWidget(self.details_table)

        layout.addWidget(details_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.btn_add_spool = QPushButton("Add Spool")
        self.btn_add_spool.clicked.connect(self._add_spool)
        button_layout.addWidget(self.btn_add_spool)

        self.btn_edit_spool = QPushButton("Edit Spool")
        self.btn_edit_spool.clicked.connect(self._edit_spool)
        button_layout.addWidget(self.btn_edit_spool)

        self.btn_remove_spool = QPushButton("Remove Spool")
        self.btn_remove_spool.clicked.connect(self._remove_spool)
        button_layout.addWidget(self.btn_remove_spool)

        button_layout.addStretch()

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        button_layout.addWidget(self.btn_close)

        layout.addLayout(button_layout)

        # Connect signals
        self.spool_list.currentItemChanged.connect(self._show_spool_details)

        # Store selected wire
        self.selected_wire = None

    def _populate_active_spools(self):
        """Populate the list of active wire spools."""
        # Load wire data from database
        try:
            db_path = os.path.join(os.path.expanduser("~"), "AutoFire", "catalog.db")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Get all wires
                cursor.execute(
                    """
                    SELECT w.name, w.gauge, w.color, wt.code AS type,
                           w.ohms_per_1000ft, w.max_current_a
                    FROM wires w
                    LEFT JOIN wire_types wt ON wt.id=w.type_id
                    ORDER BY w.gauge, w.name
                """
                )

                wires = cursor.fetchall()
                conn.close()

                for wire in wires:
                    name, gauge, color, wire_type, ohms, max_current = wire
                    # Mock usage data for now - in real implementation this would come from project data
                    total_length = 1000 if gauge == 14 else 2000 if gauge == 16 else 1500
                    used_length = int(total_length * 0.25)  # Mock 25% usage

                    usage_pct = int((used_length / total_length) * 100)
                    item_text = f"{name} - {usage_pct}% used ({used_length}/{total_length} ft)"

                    item = QListWidgetItem(item_text)
                    wire_data = {
                        "name": name,
                        "gauge": gauge,
                        "color": color,
                        "type": wire_type,
                        "ohms_per_1000ft": ohms,
                        "max_current_a": max_current,
                        "length": total_length,
                        "used": used_length,
                    }
                    item.setData(256, wire_data)  # Qt.UserRole
                    self.spool_list.addItem(item)
            else:
                # Fallback to mock data if database doesn't exist
                self._populate_mock_spools()
        except Exception as e:
            print(f"Error loading wire data: {e}")
            self._populate_mock_spools()

    def _populate_mock_spools(self):
        """Fallback mock data when database is not available."""
        spools = [
            {
                "name": "14 AWG Red",
                "gauge": 14,
                "color": "Red",
                "length": 1000,
                "used": 250,
                "type": "NAC",
            },
            {
                "name": "16 AWG Black",
                "gauge": 16,
                "color": "Black",
                "length": 2000,
                "used": 800,
                "type": "SLC",
            },
            {
                "name": "18 AWG Blue",
                "gauge": 18,
                "color": "Blue",
                "length": 1500,
                "used": 1200,
                "type": "Power",
            },
        ]

        for spool in spools:
            usage_pct = int((spool["used"] / spool["length"]) * 100)
            item_text = (
                f"{spool['name']} - {usage_pct}% used ({spool['used']}/{spool['length']} ft)"
            )
            item = QListWidgetItem(item_text)
            item.setData(256, spool)  # Qt.UserRole
            self.spool_list.addItem(item)

    def _show_spool_details(self, current, previous):
        """Show details for the selected spool."""
        if not current:
            self.details_table.setRowCount(0)
            return

        spool = current.data(256)  # Qt.UserRole
        self.details_table.setRowCount(6)

        details = [
            ("Name", spool["name"], "", "Active"),
            ("Gauge", str(spool["gauge"]), "AWG", "OK"),
            ("Color", spool["color"], "", "OK"),
            ("Total Length", str(spool["length"]), "ft", "OK"),
            ("Used Length", str(spool["used"]), "ft", "OK"),
            (
                "Remaining",
                str(spool["length"] - spool["used"]),
                "ft",
                "Low" if spool["length"] - spool["used"] < 100 else "OK",
            ),
        ]

        for row, (prop, value, unit, status) in enumerate(details):
            self.details_table.setItem(row, 0, QTableWidgetItem(prop))
            self.details_table.setItem(row, 1, QTableWidgetItem(value))
            self.details_table.setItem(row, 2, QTableWidgetItem(unit))
            status_item = QTableWidgetItem(status)
            if status == "Low":
                status_item.setBackground(QColor(255, 0, 0))  # Red
            self.details_table.setItem(row, 3, status_item)

        self.details_table.resizeColumnsToContents()

    def get_selected_wire(self):
        """Get the currently selected wire spool data."""
        current = self.spool_list.currentItem()
        if current:
            return current.data(256)  # Qt.UserRole
        return None

    def _add_spool(self):
        """Add a new wire spool."""
        # TODO: Implement add spool dialog
        pass

    def _edit_spool(self):
        """Edit the selected spool."""
        # TODO: Implement edit spool dialog
        pass

    def _remove_spool(self):
        """Remove the selected spool."""
        current = self.spool_list.currentItem()
        if current:
            row = self.spool_list.row(current)
            self.spool_list.takeItem(row)
