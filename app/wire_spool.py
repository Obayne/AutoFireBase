"""
Wire Spool Manager - Track wire inventory and usage
"""

import json
import os
from typing import Any

from PySide6 import QtCore, QtWidgets


class WireSpoolItem:
    """Represents a wire spool in inventory."""

    def __init__(
        self,
        spool_id: str,
        wire_type: str,
        gauge: str,
        color: str,
        total_length_ft: float,
        remaining_length_ft: float | None = None,
    ):
        self.spool_id = spool_id
        self.wire_type = wire_type
        self.gauge = gauge
        self.color = color
        self.total_length_ft = total_length_ft
        self.remaining_length_ft = (
            remaining_length_ft if remaining_length_ft is not None else total_length_ft
        )
        self.usage_history: list[dict[str, Any]] = []

    def use_wire(self, length_ft: float, project: str = "", device: str = "") -> bool:
        """Use wire from this spool. Returns True if successful."""
        if length_ft > self.remaining_length_ft:
            return False

        self.remaining_length_ft -= length_ft
        self.usage_history.append(
            {
                "timestamp": QtCore.QDateTime.currentDateTime().toString(),
                "length_ft": length_ft,
                "project": project,
                "device": device,
            }
        )
        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "spool_id": self.spool_id,
            "wire_type": self.wire_type,
            "gauge": self.gauge,
            "color": self.color,
            "total_length_ft": self.total_length_ft,
            "remaining_length_ft": self.remaining_length_ft,
            "usage_history": self.usage_history,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WireSpoolItem":
        """Create from dictionary."""
        spool = cls(
            data["spool_id"],
            data["wire_type"],
            data["gauge"],
            data["color"],
            data["total_length_ft"],
            data["remaining_length_ft"],
        )
        spool.usage_history = data.get("usage_history", [])
        return spool


class WireSpoolDialog(QtWidgets.QDialog):
    """Wire Spool Management Dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wire Spool Manager")
        self.setModal(False)
        self.resize(800, 600)

        # Initialize data
        self.wire_spools: dict[str, WireSpoolItem] = {}
        self.load_inventory()

        self._setup_ui()
        self._populate_spool_list()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()

        self.btn_add_spool = QtWidgets.QPushButton("Add Spool")
        self.btn_add_spool.clicked.connect(self._add_spool)
        toolbar.addWidget(self.btn_add_spool)

        self.btn_use_wire = QtWidgets.QPushButton("Use Wire")
        self.btn_use_wire.clicked.connect(self._use_wire)
        toolbar.addWidget(self.btn_use_wire)

        self.btn_generate_report = QtWidgets.QPushButton("Generate Report")
        self.btn_generate_report.clicked.connect(self._generate_report)
        toolbar.addWidget(self.btn_generate_report)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Search bar
        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(QtWidgets.QLabel("🔍"))
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Search spools...")
        self.search_edit.textChanged.connect(self._filter_spools)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        # Main content area
        content = QtWidgets.QSplitter(Qt.Horizontal)

        # Left panel - Spool list
        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_panel)

        self.spool_list = QtWidgets.QListWidget()
        self.spool_list.itemSelectionChanged.connect(self._on_spool_selected)
        left_layout.addWidget(QtWidgets.QLabel("Wire Spools"))
        left_layout.addWidget(self.spool_list)

        # Right panel - Spool details
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)

        self.details_group = QtWidgets.QGroupBox("Spool Details")
        details_layout = QtWidgets.QFormLayout(self.details_group)

        self.lbl_spool_id = QtWidgets.QLabel("-")
        self.lbl_wire_type = QtWidgets.QLabel("-")
        self.lbl_gauge = QtWidgets.QLabel("-")
        self.lbl_color = QtWidgets.QLabel("-")
        self.lbl_total_length = QtWidgets.QLabel("-")
        self.lbl_remaining_length = QtWidgets.QLabel("-")
        self.lbl_used_length = QtWidgets.QLabel("-")

        details_layout.addRow("Spool ID:", self.lbl_spool_id)
        details_layout.addRow("Type:", self.lbl_wire_type)
        details_layout.addRow("Gauge:", self.lbl_gauge)
        details_layout.addRow("Color:", self.lbl_color)
        details_layout.addRow("Total Length:", self.lbl_total_length)
        details_layout.addRow("Remaining:", self.lbl_remaining_length)
        details_layout.addRow("Used:", self.lbl_used_length)

        right_layout.addWidget(self.details_group)

        # Usage history
        self.usage_group = QtWidgets.QGroupBox("Usage History")
        usage_layout = QtWidgets.QVBoxLayout(self.usage_group)

        self.usage_table = QtWidgets.QTableWidget()
        self.usage_table.setColumnCount(4)
        self.usage_table.setHorizontalHeaderLabels(["Date", "Length (ft)", "Project", "Device"])
        self.usage_table.horizontalHeader().setStretchLastSection(True)
        usage_layout.addWidget(self.usage_table)

        right_layout.addWidget(self.usage_group)

        content.addWidget(left_panel)
        content.addWidget(right_panel)
        content.setSizes([300, 500])

        layout.addWidget(content)

        # Status bar
        self.status_label = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status_label)

    def _populate_spool_list(self):
        """Populate the spool list."""
        self.spool_list.clear()
        for spool_id, spool in self.wire_spools.items():
            remaining_pct = (spool.remaining_length_ft / spool.total_length_ft) * 100
            status = f" ({remaining_pct:.1f}% remaining)"
            item_text = f"{spool_id}: {spool.wire_type} {spool.gauge} {spool.color}{status}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, spool_id)
            self.spool_list.addItem(item)

    def _filter_spools(self):
        """Filter spools based on search text."""
        search_text = self.search_edit.text().lower()
        for i in range(self.spool_list.count()):
            item = self.spool_list.item(i)
            item.setHidden(search_text not in item.text().lower())

    def _on_spool_selected(self):
        """Handle spool selection."""
        current_item = self.spool_list.currentItem()
        if not current_item:
            self._clear_details()
            return

        spool_id = current_item.data(QtCore.Qt.UserRole)
        spool = self.wire_spools.get(spool_id)
        if not spool:
            self._clear_details()
            return

        # Update details
        self.lbl_spool_id.setText(spool.spool_id)
        self.lbl_wire_type.setText(spool.wire_type)
        self.lbl_gauge.setText(spool.gauge)
        self.lbl_color.setText(spool.color)
        self.lbl_total_length.setText(f"{spool.total_length_ft:.1f} ft")
        self.lbl_remaining_length.setText(f"{spool.remaining_length_ft:.1f} ft")
        used = spool.total_length_ft - spool.remaining_length_ft
        self.lbl_used_length.setText(f"{used:.1f} ft")

        # Update usage history
        self.usage_table.setRowCount(len(spool.usage_history))
        for row, usage in enumerate(spool.usage_history):
            self.usage_table.setItem(row, 0, QtWidgets.QTableWidgetItem(usage["timestamp"]))
            self.usage_table.setItem(
                row, 1, QtWidgets.QTableWidgetItem(f"{usage['length_ft']:.1f}")
            )
            self.usage_table.setItem(row, 2, QtWidgets.QTableWidgetItem(usage.get("project", "")))
            self.usage_table.setItem(row, 3, QtWidgets.QTableWidgetItem(usage.get("device", "")))

    def _clear_details(self):
        """Clear the details panel."""
        self.lbl_spool_id.setText("-")
        self.lbl_wire_type.setText("-")
        self.lbl_gauge.setText("-")
        self.lbl_color.setText("-")
        self.lbl_total_length.setText("-")
        self.lbl_remaining_length.setText("-")
        self.lbl_used_length.setText("-")
        self.usage_table.setRowCount(0)

    def _add_spool(self):
        """Add a new wire spool."""
        dialog = AddSpoolDialog(self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            spool = dialog.get_spool()
            self.wire_spools[spool.spool_id] = spool
            self._populate_spool_list()
            self.save_inventory()
            self.status_label.setText(f"Added spool {spool.spool_id}")

    def _use_wire(self):
        """Use wire from selected spool."""
        current_item = self.spool_list.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a spool first.")
            return

        spool_id = current_item.data(QtCore.Qt.UserRole)
        spool = self.wire_spools.get(spool_id)
        if not spool:
            return

        dialog = UseWireDialog(spool, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            length, project, device = dialog.get_usage()
            if spool.use_wire(length, project, device):
                self._populate_spool_list()
                self._on_spool_selected()  # Refresh details
                self.save_inventory()
                self.status_label.setText(f"Used {length:.1f} ft from {spool_id}")
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Insufficient Wire", f"Not enough wire remaining on spool {spool_id}."
                )

    def _generate_report(self):
        """Generate usage report."""
        # Calculate totals
        total_inventory = sum(spool.total_length_ft for spool in self.wire_spools.values())
        total_remaining = sum(spool.remaining_length_ft for spool in self.wire_spools.values())
        total_used = total_inventory - total_remaining

        # Generate report text
        report = f"""Wire Inventory Report
Generated: {QtCore.QDateTime.currentDateTime().toString()}

Summary:
- Total spools: {len(self.wire_spools)}
- Total wire inventory: {total_inventory:.1f} ft
- Total remaining: {total_remaining:.1f} ft
- Total used: {total_used:.1f} ft

Spool Details:
"""

        for spool_id, spool in self.wire_spools.items():
            used = spool.total_length_ft - spool.remaining_length_ft
            report += f"\n{spool_id}: {spool.wire_type} {spool.gauge} {spool.color}\n"
            report += f"  Total: {spool.total_length_ft:.1f} ft, Remaining: {spool.remaining_length_ft:.1f} ft, Used: {used:.1f} ft\n"

        # Show report dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Wire Usage Report")
        dialog.resize(600, 400)

        layout = QtWidgets.QVBoxLayout(dialog)
        text_edit = QtWidgets.QTextEdit()
        text_edit.setPlainText(report)
        layout.addWidget(text_edit)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Close
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        # Save functionality
        def save_report():
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                dialog, "Save Report", "", "Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                with open(file_path, "w") as f:
                    f.write(report)
                self.status_label.setText(f"Report saved to {file_path}")

        buttons.accepted.connect(save_report)
        layout.addWidget(buttons)

        dialog.exec()

    def load_inventory(self):
        """Load wire inventory from file."""
        try:
            inventory_file = os.path.join(
                os.path.expanduser("~"), "AutoFire", "wire_inventory.json"
            )
            if os.path.exists(inventory_file):
                with open(inventory_file) as f:
                    data = json.load(f)
                    self.wire_spools = {
                        sid: WireSpoolItem.from_dict(sdata) for sid, sdata in data.items()
                    }
        except Exception as e:
            print(f"Failed to load wire inventory: {e}")

    def save_inventory(self):
        """Save wire inventory to file."""
        try:
            inventory_file = os.path.join(
                os.path.expanduser("~"), "AutoFire", "wire_inventory.json"
            )
            os.makedirs(os.path.dirname(inventory_file), exist_ok=True)
            with open(inventory_file, "w") as f:
                data = {sid: spool.to_dict() for sid, spool in self.wire_spools.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save wire inventory: {e}")


class AddSpoolDialog(QtWidgets.QDialog):
    """Dialog for adding a new wire spool."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Wire Spool")
        self.setModal(True)

        layout = QtWidgets.QFormLayout(self)

        self.spool_id_edit = QtWidgets.QLineEdit()
        self.wire_type_combo = QtWidgets.QComboBox()
        self.wire_type_combo.addItems(
            ["THHN", "XHHW", "Romex", "Coaxial", "Fiber Optic", "Control", "Other"]
        )
        self.gauge_combo = QtWidgets.QComboBox()
        self.gauge_combo.addItems(
            [
                "14 AWG",
                "12 AWG",
                "10 AWG",
                "8 AWG",
                "6 AWG",
                "4 AWG",
                "2 AWG",
                "1/0 AWG",
                "2/0 AWG",
                "4/0 AWG",
            ]
        )
        self.color_combo = QtWidgets.QComboBox()
        self.color_combo.addItems(
            [
                "Black",
                "White",
                "Red",
                "Blue",
                "Green",
                "Yellow",
                "Orange",
                "Brown",
                "Gray",
                "Purple",
            ]
        )
        self.length_spin = QtWidgets.QDoubleSpinBox()
        self.length_spin.setRange(1, 10000)
        self.length_spin.setValue(1000)
        self.length_spin.setSuffix(" ft")

        layout.addRow("Spool ID:", self.spool_id_edit)
        layout.addRow("Wire Type:", self.wire_type_combo)
        layout.addRow("Gauge:", self.gauge_combo)
        layout.addRow("Color:", self.color_combo)
        layout.addRow("Length:", self.length_spin)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_spool(self) -> WireSpoolItem:
        """Get the spool from dialog inputs."""
        return WireSpoolItem(
            self.spool_id_edit.text(),
            self.wire_type_combo.currentText(),
            self.gauge_combo.currentText(),
            self.color_combo.currentText(),
            self.length_spin.value(),
        )


class UseWireDialog(QtWidgets.QDialog):
    """Dialog for using wire from a spool."""

    def __init__(self, spool: WireSpoolItem, parent=None):
        super().__init__(parent)
        self.spool = spool
        self.setWindowTitle(f"Use Wire from {spool.spool_id}")
        self.setModal(True)

        layout = QtWidgets.QFormLayout(self)

        self.length_spin = QtWidgets.QDoubleSpinBox()
        self.length_spin.setRange(0.1, spool.remaining_length_ft)
        self.length_spin.setValue(10)
        self.length_spin.setSuffix(" ft")

        self.project_edit = QtWidgets.QLineEdit()
        self.project_edit.setPlaceholderText("Optional project name")

        self.device_edit = QtWidgets.QLineEdit()
        self.device_edit.setPlaceholderText("Optional device/location")

        layout.addRow("Length to use:", self.length_spin)
        layout.addRow("Project:", self.project_edit)
        layout.addRow("Device:", self.device_edit)

        # Show remaining length
        remaining_label = QtWidgets.QLabel(
            f"Remaining on spool: {spool.remaining_length_ft:.1f} ft"
        )
        layout.addRow(remaining_label)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_usage(self) -> tuple:
        """Get the usage data from dialog."""
        return (self.length_spin.value(), self.project_edit.text(), self.device_edit.text())
