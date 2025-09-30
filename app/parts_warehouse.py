"""
Parts Warehouse - Manage fire alarm parts and components inventory
"""

import json
import os
from typing import Any

from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PartItem:
    """Represents a part in the warehouse inventory."""

    def __init__(
        self,
        part_number: str,
        name: str,
        category: str,
        description: str = "",
        unit_cost: float = 0.0,
        quantity: int = 0,
        min_quantity: int = 0,
    ):
        self.part_number = part_number
        self.name = name
        self.category = category
        self.description = description
        self.unit_cost = unit_cost
        self.quantity = quantity
        self.min_quantity = min_quantity
        self.supplier = ""
        self.location = ""
        self.last_updated = QDateTime.currentDateTime().toString()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "part_number": self.part_number,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "unit_cost": self.unit_cost,
            "quantity": self.quantity,
            "min_quantity": self.min_quantity,
            "supplier": self.supplier,
            "location": self.location,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PartItem":
        """Create from dictionary."""
        part = cls(
            data["part_number"],
            data["name"],
            data["category"],
            data.get("description", ""),
            data.get("unit_cost", 0.0),
            data.get("quantity", 0),
            data.get("min_quantity", 0),
        )
        part.supplier = data.get("supplier", "")
        part.location = data.get("location", "")
        part.last_updated = data.get("last_updated", part.last_updated)
        return part

    def is_low_stock(self) -> bool:
        """Check if part is low on stock."""
        return self.quantity <= self.min_quantity

    def total_value(self) -> float:
        """Calculate total value of inventory."""
        return self.unit_cost * self.quantity


class PartsWarehouseDialog(QDialog):
    """Parts Warehouse Management Dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parts Warehouse")
        self.setModal(False)
        self.resize(1000, 600)

        # Initialize data
        self.parts: dict[str, PartItem] = {}
        self.load_inventory()

        self._setup_ui()
        self._populate_parts_list()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        self.btn_add_part = QPushButton("Add Part")
        self.btn_add_part.clicked.connect(self._add_part)
        toolbar.addWidget(self.btn_add_part)

        self.btn_edit_part = QPushButton("Edit Part")
        self.btn_edit_part.clicked.connect(self._edit_part)
        toolbar.addWidget(self.btn_edit_part)

        self.btn_delete_part = QPushButton("Delete Part")
        self.btn_delete_part.clicked.connect(self._delete_part)
        toolbar.addWidget(self.btn_delete_part)

        self.btn_adjust_stock = QPushButton("Adjust Stock")
        self.btn_adjust_stock.clicked.connect(self._adjust_stock)
        toolbar.addWidget(self.btn_adjust_stock)

        self.btn_generate_report = QPushButton("Generate Report")
        self.btn_generate_report.clicked.connect(self._generate_report)
        toolbar.addWidget(self.btn_generate_report)

        toolbar.addStretch()

        # Low stock indicator
        self.low_stock_label = QLabel()
        self.low_stock_label.setStyleSheet("color: red; font-weight: bold;")
        toolbar.addWidget(self.low_stock_label)

        layout.addLayout(toolbar)

        # Search and filter
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("🔍"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search parts...")
        self.search_edit.textChanged.connect(self._filter_parts)
        filter_layout.addWidget(self.search_edit)

        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", "")
        self.category_filter.currentTextChanged.connect(self._filter_parts)
        filter_layout.addWidget(self.category_filter)

        self.show_low_stock_only = QCheckBox("Low Stock Only")
        self.show_low_stock_only.toggled.connect(self._filter_parts)
        filter_layout.addWidget(self.show_low_stock_only)

        layout.addLayout(filter_layout)

        # Main content
        content = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Parts list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.parts_list = QTableWidget()
        self.parts_list.setColumnCount(6)
        self.parts_list.setHorizontalHeaderLabels(
            ["Part Number", "Name", "Category", "Quantity", "Unit Cost", "Total Value"]
        )
        self.parts_list.horizontalHeader().setStretchLastSection(True)
        self.parts_list.setAlternatingRowColors(True)
        self.parts_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.parts_list.itemSelectionChanged.connect(self._on_part_selected)

        left_layout.addWidget(QLabel("Parts Inventory"))
        left_layout.addWidget(self.parts_list)

        # Summary
        summary_layout = QHBoxLayout()
        self.total_parts_label = QLabel("Total Parts: 0")
        self.total_value_label = QLabel("Total Value: $0.00")
        self.low_stock_count_label = QLabel("Low Stock: 0")

        summary_layout.addWidget(self.total_parts_label)
        summary_layout.addWidget(self.total_value_label)
        summary_layout.addWidget(self.low_stock_count_label)
        summary_layout.addStretch()

        left_layout.addLayout(summary_layout)

        # Right panel - Part details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        details_group = QGroupBox("Part Details")
        details_layout = QFormLayout(details_group)

        self.lbl_part_number = QLabel("-")
        self.lbl_name = QLabel("-")
        self.lbl_category = QLabel("-")
        self.lbl_description = QLabel("-")
        self.lbl_quantity = QLabel("-")
        self.lbl_min_quantity = QLabel("-")
        self.lbl_unit_cost = QLabel("-")
        self.lbl_total_value = QLabel("-")
        self.lbl_supplier = QLabel("-")
        self.lbl_location = QLabel("-")
        self.lbl_last_updated = QLabel("-")

        details_layout.addRow("Part Number:", self.lbl_part_number)
        details_layout.addRow("Name:", self.lbl_name)
        details_layout.addRow("Category:", self.lbl_category)
        details_layout.addRow("Description:", self.lbl_description)
        details_layout.addRow("Quantity:", self.lbl_quantity)
        details_layout.addRow("Min Quantity:", self.lbl_min_quantity)
        details_layout.addRow("Unit Cost:", self.lbl_unit_cost)
        details_layout.addRow("Total Value:", self.lbl_total_value)
        details_layout.addRow("Supplier:", self.lbl_supplier)
        details_layout.addRow("Location:", self.lbl_location)
        details_layout.addRow("Last Updated:", self.lbl_last_updated)

        right_layout.addWidget(details_group)

        # Stock history (placeholder for future enhancement)
        history_group = QGroupBox("Stock History")
        history_layout = QVBoxLayout(history_group)

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setPlainText("Stock history tracking coming soon...")
        history_layout.addWidget(self.history_text)

        right_layout.addWidget(history_group)

        content.addWidget(left_panel)
        content.addWidget(right_panel)
        content.setSizes([600, 400])

        layout.addWidget(content)

        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def _populate_parts_list(self):
        """Populate the parts table."""
        self.parts_list.setRowCount(len(self.parts))

        # Get categories for filter
        categories = set()
        for part in self.parts.values():
            categories.add(part.category)

        self.category_filter.clear()
        self.category_filter.addItem("All Categories", "")
        for category in sorted(categories):
            self.category_filter.addItem(category, category)

        # Populate table
        for row, (part_number, part) in enumerate(self.parts.items()):
            self.parts_list.setItem(row, 0, QTableWidgetItem(part.part_number))
            self.parts_list.setItem(row, 1, QTableWidgetItem(part.name))
            self.parts_list.setItem(row, 2, QTableWidgetItem(part.category))
            self.parts_list.setItem(row, 3, QTableWidgetItem(str(part.quantity)))
            self.parts_list.setItem(row, 4, QTableWidgetItem(f"${part.unit_cost:.2f}"))
            self.parts_list.setItem(row, 5, QTableWidgetItem(f"${part.total_value():.2f}"))

            # Highlight low stock items
            if part.is_low_stock():
                for col in range(6):
                    item = self.parts_list.item(row, col)
                    if item:
                        item.setBackground(QColor(255, 200, 200))  # Light red

        self.parts_list.resizeColumnsToContents()
        self._update_summary()

    def _filter_parts(self):
        """Filter parts based on search and category."""
        search_text = self.search_edit.text().lower()
        category_filter = self.category_filter.currentData()
        low_stock_only = self.show_low_stock_only.isChecked()

        for row in range(self.parts_list.rowCount()):
            part_number_item = self.parts_list.item(row, 0)
            if not part_number_item:
                continue

            part_number = part_number_item.text()
            part = self.parts.get(part_number)
            if not part:
                continue

            # Apply filters
            matches_search = (
                search_text in part_number.lower()
                or search_text in part.name.lower()
                or search_text in part.description.lower()
            )

            matches_category = not category_filter or part.category == category_filter
            matches_low_stock = not low_stock_only or part.is_low_stock()

            visible = matches_search and matches_category and matches_low_stock

            self.parts_list.setRowHidden(row, not visible)

    def _on_part_selected(self):
        """Handle part selection."""
        current_row = self.parts_list.currentRow()
        if current_row < 0:
            self._clear_details()
            return

        part_number_item = self.parts_list.item(current_row, 0)
        if not part_number_item:
            self._clear_details()
            return

        part_number = part_number_item.text()
        part = self.parts.get(part_number)
        if not part:
            self._clear_details()
            return

        # Update details
        self.lbl_part_number.setText(part.part_number)
        self.lbl_name.setText(part.name)
        self.lbl_category.setText(part.category)
        self.lbl_description.setText(part.description or "No description")
        self.lbl_quantity.setText(str(part.quantity))
        self.lbl_min_quantity.setText(str(part.min_quantity))
        self.lbl_unit_cost.setText(f"${part.unit_cost:.2f}")
        self.lbl_total_value.setText(f"${part.total_value():.2f}")
        self.lbl_supplier.setText(part.supplier or "Not specified")
        self.lbl_location.setText(part.location or "Not specified")
        self.lbl_last_updated.setText(part.last_updated)

    def _clear_details(self):
        """Clear the details panel."""
        labels = [
            self.lbl_part_number,
            self.lbl_name,
            self.lbl_category,
            self.lbl_description,
            self.lbl_quantity,
            self.lbl_min_quantity,
            self.lbl_unit_cost,
            self.lbl_total_value,
            self.lbl_supplier,
            self.lbl_location,
            self.lbl_last_updated,
        ]
        for label in labels:
            label.setText("-")

    def _update_summary(self):
        """Update summary statistics."""
        total_parts = len(self.parts)
        total_value = sum(part.total_value() for part in self.parts.values())
        low_stock_count = sum(1 for part in self.parts.values() if part.is_low_stock())

        self.total_parts_label.setText(f"Total Parts: {total_parts}")
        self.total_value_label.setText(f"Total Value: ${total_value:.2f}")
        self.low_stock_count_label.setText(f"Low Stock: {low_stock_count}")

        # Update low stock indicator
        if low_stock_count > 0:
            self.low_stock_label.setText(f"⚠️ {low_stock_count} items low on stock")
            self.low_stock_label.show()
        else:
            self.low_stock_label.hide()

    def _add_part(self):
        """Add a new part."""
        dialog = PartDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            part = dialog.get_part()
            self.parts[part.part_number] = part
            self._populate_parts_list()
            self.save_inventory()
            self.status_label.setText(f"Added part: {part.name}")

    def _edit_part(self):
        """Edit selected part."""
        current_row = self.parts_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a part to edit.")
            return

        part_number_item = self.parts_list.item(current_row, 0)
        if not part_number_item:
            return

        part_number = part_number_item.text()
        part = self.parts.get(part_number)
        if not part:
            return

        dialog = PartDialog(self, part)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_part = dialog.get_part()
            self.parts[part_number] = updated_part
            self._populate_parts_list()
            self.save_inventory()
            self.status_label.setText(f"Updated part: {updated_part.name}")

    def _delete_part(self):
        """Delete selected part."""
        current_row = self.parts_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a part to delete.")
            return

        part_number_item = self.parts_list.item(current_row, 0)
        if not part_number_item:
            return

        part_number = part_number_item.text()
        part = self.parts.get(part_number)
        if not part:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete part '{part.name}' ({part_number})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.parts[part_number]
            self._populate_parts_list()
            self.save_inventory()
            self.status_label.setText(f"Deleted part: {part.name}")

    def _adjust_stock(self):
        """Adjust stock quantity for selected part."""
        current_row = self.parts_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a part to adjust stock.")
            return

        part_number_item = self.parts_list.item(current_row, 0)
        if not part_number_item:
            return

        part_number = part_number_item.text()
        part = self.parts.get(part_number)
        if not part:
            return

        dialog = StockAdjustmentDialog(part, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_quantity = dialog.get_new_quantity()
            part.quantity = new_quantity
            part.last_updated = QDateTime.currentDateTime().toString()
            self._populate_parts_list()
            self.save_inventory()
            self.status_label.setText(f"Updated stock for {part.name}: {new_quantity}")

    def _generate_report(self):
        """Generate inventory report."""
        report = f"""Parts Warehouse Inventory Report
Generated: {QtCore.QDateTime.currentDateTime().toString()}

Summary:
- Total Parts: {len(self.parts)}
- Total Value: ${sum(part.total_value() for part in self.parts.values()):.2f}
- Low Stock Items: {sum(1 for part in self.parts.values() if part.is_low_stock())}

Parts by Category:
"""

        categories = {}
        for part in self.parts.values():
            if part.category not in categories:
                categories[part.category] = []
            categories[part.category].append(part)

        for category, parts in sorted(categories.items()):
            report += f"\n{category} ({len(parts)} items):\n"
            for part in sorted(parts, key=lambda p: p.part_number):
                status = " ⚠️ LOW STOCK" if part.is_low_stock() else ""
                report += f"  {part.part_number}: {part.name} - Qty: {part.quantity}, Value: ${part.total_value():.2f}{status}\n"

        # Show report
        dialog = QDialog(self)
        dialog.setWindowTitle("Inventory Report")
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setPlainText(report)
        layout.addWidget(text_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        def save_report():
            file_path, _ = QFileDialog.getSaveFileName(
                dialog, "Save Report", "", "Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                with open(file_path, "w") as f:
                    f.write(report)

        buttons.accepted.connect(save_report)
        layout.addWidget(buttons)

        dialog.exec()

    def load_inventory(self):
        """Load parts inventory from file."""
        try:
            inventory_file = os.path.join(
                os.path.expanduser("~"), "AutoFire", "parts_inventory.json"
            )
            if os.path.exists(inventory_file):
                with open(inventory_file) as f:
                    data = json.load(f)
                    self.parts = {pid: PartItem.from_dict(pdata) for pid, pdata in data.items()}
        except Exception as e:
            print(f"Failed to load parts inventory: {e}")

    def save_inventory(self):
        """Save parts inventory to file."""
        try:
            inventory_file = os.path.join(
                os.path.expanduser("~"), "AutoFire", "parts_inventory.json"
            )
            os.makedirs(os.path.dirname(inventory_file), exist_ok=True)
            with open(inventory_file, "w") as f:
                data = {pid: part.to_dict() for pid, part in self.parts.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save parts inventory: {e}")


class PartDialog(QDialog):
    """Dialog for adding/editing a part."""

    def __init__(self, parent=None, part: PartItem | None = None):
        super().__init__(parent)
        self.part = part
        self.setWindowTitle("Add Part" if not part else "Edit Part")
        self.setModal(True)

        layout = QFormLayout(self)

        self.part_number_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.category_combo = QComboBox()
        self.category_combo.addItems(
            [
                "Smoke Detectors",
                "Heat Detectors",
                "Pull Stations",
                "Notification",
                "Control Panels",
                "Power Supplies",
                "Cable/Wire",
                "Connectors",
                "Mounting Hardware",
                "Other",
            ]
        )
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.unit_cost_spin = QDoubleSpinBox()
        self.unit_cost_spin.setRange(0, 10000)
        self.unit_cost_spin.setPrefix("$")
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(0, 10000)
        self.min_quantity_spin = QSpinBox()
        self.min_quantity_spin.setRange(0, 1000)
        self.supplier_edit = QLineEdit()
        self.location_edit = QLineEdit()

        layout.addRow("Part Number:", self.part_number_edit)
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Category:", self.category_combo)
        layout.addRow("Description:", self.description_edit)
        layout.addRow("Unit Cost:", self.unit_cost_spin)
        layout.addRow("Quantity:", self.quantity_spin)
        layout.addRow("Min Quantity:", self.min_quantity_spin)
        layout.addRow("Supplier:", self.supplier_edit)
        layout.addRow("Location:", self.location_edit)

        if part:
            self.part_number_edit.setText(part.part_number)
            self.part_number_edit.setEnabled(False)  # Don't allow changing part number
            self.name_edit.setText(part.name)
            self.category_combo.setCurrentText(part.category)
            self.description_edit.setPlainText(part.description)
            self.unit_cost_spin.setValue(part.unit_cost)
            self.quantity_spin.setValue(part.quantity)
            self.min_quantity_spin.setValue(part.min_quantity)
            self.supplier_edit.setText(part.supplier)
            self.location_edit.setText(part.location)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_part(self) -> PartItem:
        """Get part data from dialog."""
        return PartItem(
            self.part_number_edit.text(),
            self.name_edit.text(),
            self.category_combo.currentText(),
            self.description_edit.toPlainText(),
            self.unit_cost_spin.value(),
            self.quantity_spin.value(),
            self.min_quantity_spin.value(),
        )


class StockAdjustmentDialog(QDialog):
    """Dialog for adjusting stock quantity."""

    def __init__(self, part: PartItem, parent=None):
        super().__init__(parent)
        self.part = part
        self.setWindowTitle(f"Adjust Stock - {part.name}")
        self.setModal(True)

        layout = QFormLayout(self)

        self.current_qty_label = QLabel(str(part.quantity))
        self.new_qty_spin = QSpinBox()
        self.new_qty_spin.setRange(0, 10000)
        self.new_qty_spin.setValue(part.quantity)

        self.adjustment_type = QComboBox()
        self.adjustment_type.addItems(["Set Quantity", "Add to Stock", "Remove from Stock"])

        self.adjustment_amount = QSpinBox()
        self.adjustment_amount.setRange(-10000, 10000)
        self.adjustment_amount.setValue(0)

        layout.addRow("Current Quantity:", self.current_qty_label)
        layout.addRow("Adjustment Type:", self.adjustment_type)
        layout.addRow("Adjustment Amount:", self.adjustment_amount)
        layout.addRow("New Quantity:", self.new_qty_spin)

        # Connect signals
        self.adjustment_type.currentTextChanged.connect(self._update_new_quantity)
        self.adjustment_amount.valueChanged.connect(self._update_new_quantity)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _update_new_quantity(self):
        """Update the new quantity based on adjustment."""
        adjustment_type = self.adjustment_type.currentText()
        amount = self.adjustment_amount.value()

        if adjustment_type == "Set Quantity":
            new_qty = amount
        elif adjustment_type == "Add to Stock":
            new_qty = self.part.quantity + amount
        else:  # Remove from Stock
            new_qty = max(0, self.part.quantity + amount)  # Prevent negative

        self.new_qty_spin.setValue(new_qty)

    def get_new_quantity(self) -> int:
        """Get the new quantity."""
        return self.new_qty_spin.value()
