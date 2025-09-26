import sqlite3

from PySide6 import QtCore, QtGui, QtWidgets

import db.loader as db_loader


class LayerManagerDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Layer Manager")
        self.setModal(True)
        self.resize(600, 400)

        self.main_window = parent
        self.layers = []

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Layer Manager")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Layer list
        layout.addWidget(QtWidgets.QLabel("Layers:"))

        self.layer_table = QtWidgets.QTableWidget()
        self.layer_table.setColumnCount(5)
        self.layer_table.setHorizontalHeaderLabels(["Name", "Color", "Visible", "Locked", "Print"])
        self.layer_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.layer_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        layout.addWidget(self.layer_table)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.add_layer_btn = QtWidgets.QPushButton("Add Layer")
        self.add_layer_btn.clicked.connect(self.add_layer)
        button_layout.addWidget(self.add_layer_btn)

        self.remove_layer_btn = QtWidgets.QPushButton("Remove Layer")
        self.remove_layer_btn.clicked.connect(self.remove_layer)
        button_layout.addWidget(self.remove_layer_btn)

        self.color_btn = QtWidgets.QPushButton("Change Color")
        self.color_btn.clicked.connect(self.change_color)
        button_layout.addWidget(self.color_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        # OK/Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Load layers
        self.load_layers()
        self.update_table()

    def load_layers(self):
        """Load layers from the database."""
        try:
            con = db_loader.connect()
            self.layers = db_loader.fetch_layers(con)
            con.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load layers: {str(e)}")
            self.layers = []

    def update_table(self):
        """Update the table with layer data."""
        self.layer_table.setRowCount(len(self.layers))

        for i, layer in enumerate(self.layers):
            # Name
            name_item = QtWidgets.QTableWidgetItem(layer.get("name", ""))
            name_item.setFlags(name_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
            self.layer_table.setItem(i, 0, name_item)

            # Color
            color_item = QtWidgets.QTableWidgetItem()
            color = QtGui.QColor(layer.get("color", "#FFFFFF"))
            color_item.setBackground(QtGui.QBrush(color))
            color_item.setFlags(color_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            self.layer_table.setItem(i, 1, color_item)

            # Visible
            visible_widget = QtWidgets.QWidget()
            visible_layout = QtWidgets.QHBoxLayout(visible_widget)
            visible_layout.setContentsMargins(4, 0, 4, 0)
            visible_checkbox = QtWidgets.QCheckBox()
            visible_checkbox.setChecked(layer.get("visible", True))
            visible_checkbox.stateChanged.connect(
                lambda state, idx=i: self.toggle_layer_property(idx, "visible", state)
            )
            visible_layout.addWidget(visible_checkbox)
            visible_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.layer_table.setCellWidget(i, 2, visible_widget)

            # Locked
            locked_widget = QtWidgets.QWidget()
            locked_layout = QtWidgets.QHBoxLayout(locked_widget)
            locked_layout.setContentsMargins(4, 0, 4, 0)
            locked_checkbox = QtWidgets.QCheckBox()
            locked_checkbox.setChecked(layer.get("locked", False))
            locked_checkbox.stateChanged.connect(
                lambda state, idx=i: self.toggle_layer_property(idx, "locked", state)
            )
            locked_layout.addWidget(locked_checkbox)
            locked_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.layer_table.setCellWidget(i, 3, locked_widget)

            # Print
            print_widget = QtWidgets.QWidget()
            print_layout = QtWidgets.QHBoxLayout(print_widget)
            print_layout.setContentsMargins(4, 0, 4, 0)
            print_checkbox = QtWidgets.QCheckBox()
            print_checkbox.setChecked(layer.get("print", True))
            print_checkbox.stateChanged.connect(
                lambda state, idx=i: self.toggle_layer_property(idx, "print", state)
            )
            print_layout.addWidget(print_checkbox)
            print_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.layer_table.setCellWidget(i, 4, print_widget)

    def toggle_layer_property(self, index, property_name, state):
        """Toggle a layer property."""
        if 0 <= index < len(self.layers):
            # Convert Qt.CheckState to boolean
            value = state == QtCore.Qt.CheckState.Checked.value
            self.layers[index][property_name] = value

    def add_layer(self):
        """Add a new layer."""
        layer_name, ok = QtWidgets.QInputDialog.getText(self, "Add Layer", "Layer Name:")
        if ok and layer_name:
            # Check if layer name already exists
            if any(layer.get("name", "") == layer_name for layer in self.layers):
                QtWidgets.QMessageBox.warning(
                    self, "Warning", f"Layer '{layer_name}' already exists."
                )
                return

            new_layer = {
                "id": len(self.layers) + 1,
                "name": layer_name,
                "color": "#FFFFFF",
                "visible": True,
                "locked": False,
                "print": True,
            }
            self.layers.append(new_layer)
            self.update_table()

    def remove_layer(self):
        """Remove the selected layer."""
        selected_row = self.layer_table.currentRow()
        if selected_row >= 0 and selected_row < len(self.layers):
            layer_name = self.layers[selected_row].get("name", "")
            reply = QtWidgets.QMessageBox.question(
                self,
                "Remove Layer",
                f"Are you sure you want to remove layer '{layer_name}'?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            )

            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.layers.pop(selected_row)
                self.update_table()
        else:
            QtWidgets.QMessageBox.information(
                self, "Remove Layer", "Please select a layer to remove."
            )

    def change_color(self):
        """Change the color of the selected layer."""
        selected_row = self.layer_table.currentRow()
        if selected_row >= 0 and selected_row < len(self.layers):
            current_color = QtGui.QColor(self.layers[selected_row].get("color", "#FFFFFF"))
            color = QtWidgets.QColorDialog.getColor(current_color, self, "Select Layer Color")
            if color.isValid():
                self.layers[selected_row]["color"] = color.name()
                self.update_table()
        else:
            QtWidgets.QMessageBox.information(
                self, "Change Color", "Please select a layer to change its color."
            )

    def accept(self):
        """Save changes and close the dialog."""
        try:
            # Update layer names from table
            for i in range(self.layer_table.rowCount()):
                if i < len(self.layers):
                    name_item = self.layer_table.item(i, 0)
                    if name_item:
                        self.layers[i]["name"] = name_item.text()

            # Save to database
            con = db_loader.connect()
            self.update_layers_in_db(con, self.layers)
            con.close()

            # Update main window if it exists
            if self.main_window:
                self.main_window.layers = self.layers
                self.main_window.refresh_devices_on_canvas()

            super().accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save layers: {str(e)}")

    def update_layers_in_db(self, con: sqlite3.Connection, layers: list):
        """Update layers in the database."""
        cur = con.cursor()

        # First, get existing layer IDs
        cur.execute("SELECT id FROM layers")
        existing_ids = {row[0] for row in cur.fetchall()}

        # Update or insert layers
        for layer in layers:
            layer_id = layer.get("id")
            if layer_id and layer_id in existing_ids:
                # Update existing layer
                cur.execute(
                    """
                    UPDATE layers 
                    SET name=?, color=?, visible=?, locked=?, print=?
                    WHERE id=?
                """,
                    (
                        layer.get("name", ""),
                        layer.get("color", "#FFFFFF"),
                        layer.get("visible", True),
                        layer.get("locked", False),
                        layer.get("print", True),
                        layer_id,
                    ),
                )
            else:
                # Insert new layer
                cur.execute(
                    """
                    INSERT INTO layers (name, color, visible, locked, print)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        layer.get("name", ""),
                        layer.get("color", "#FFFFFF"),
                        layer.get("visible", True),
                        layer.get("locked", False),
                        layer.get("print", True),
                    ),
                )

        con.commit()
