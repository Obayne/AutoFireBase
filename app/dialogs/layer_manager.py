from PySide6 import QtWidgets, QtCore
from db import loader as db_loader

class LayerManagerDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Layer Manager")
        self.setModal(True)
        self.resize(800, 600)

        self.parent = parent

        layout = QtWidgets.QVBoxLayout(self)

        self.layer_table = QtWidgets.QTableWidget()
        self.layer_table.setColumnCount(13)
        self.layer_table.setHorizontalHeaderLabels(["Name", "Color", "Visible", "Locked", "Show Name", "Show Part #", "Show SLC Addr", "Show Circuit ID", "Show Zone", "Show Max Current", "Show Voltage", "Show Addressable", "Show Candela Options", "Active"])
        self.layer_table.itemChanged.connect(self.update_layer_in_db)
        layout.addWidget(self.layer_table)

        button_layout = QtWidgets.QHBoxLayout()
        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.clicked.connect(self.add_layer)
        self.remove_button = QtWidgets.QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_layer)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        # Add OK and Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.populate_layers()

    def populate_layers(self):
        self.layer_table.setRowCount(0)
        try:
            con = db_loader.connect()
            self.layers = db_loader.fetch_layers(con)
            con.close()

            for row, layer in enumerate(self.layers):
                self.layer_table.insertRow(row)
                
                # Name (editable)
                name_item = QtWidgets.QTableWidgetItem(layer['name'])
                name_item.setFlags(name_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                name_item.setData(QtCore.Qt.UserRole, layer['id']) # Store layer ID
                self.layer_table.setItem(row, 0, name_item)
                
                # Color (button to open color picker)
                color_button = QtWidgets.QPushButton("")
                color_button.setStyleSheet(f"background-color: {layer['color']}; border: 1px solid #555;")
                color_button.clicked.connect(lambda checked, row=row: self.pick_color(row))
                self.layer_table.setCellWidget(row, 1, color_button)
                
                # Visible (checkable)
                visible_item = QtWidgets.QTableWidgetItem()
                visible_item.setFlags(visible_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                visible_item.setCheckState(QtCore.Qt.CheckState.Checked if layer['visible'] else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 2, visible_item)
                
                # Locked (checkable)
                locked_item = QtWidgets.QTableWidgetItem()
                locked_item.setFlags(locked_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                locked_item.setCheckState(QtCore.Qt.CheckState.Checked if layer['locked'] else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 3, locked_item)
                
                # Show Name (checkable)
                show_name_item = QtWidgets.QTableWidgetItem()
                show_name_item.setFlags(show_name_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                show_name_item.setCheckState(QtCore.Qt.CheckState.Checked if layer['show_name'] else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 4, show_name_item)
                
                # Show Part # (checkable)
                show_part_number_item = QtWidgets.QTableWidgetItem()
                show_part_number_item.setFlags(show_part_number_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                show_part_number_item.setCheckState(QtCore.Qt.CheckState.Checked if layer['show_part_number'] else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 5, show_part_number_item)

                # Show SLC Address (checkable)
                show_slc_address_item = QtWidgets.QTableWidgetItem()
                show_slc_address_item.setFlags(show_slc_address_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                show_slc_address_item.setCheckState(QtCore.Qt.CheckState.Checked if layer.get('show_slc_address', True) else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 6, show_slc_address_item)

                # Show Circuit ID (checkable)
                show_circuit_id_item = QtWidgets.QTableWidgetItem()
                show_circuit_id_item.setFlags(show_circuit_id_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                show_circuit_id_item.setCheckState(QtCore.Qt.CheckState.Checked if layer.get('show_circuit_id', True) else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 7, show_circuit_id_item)

                # Show Zone (checkable)
                show_zone_item = QtWidgets.QTableWidgetItem()
                show_zone_item.setFlags(show_zone_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                show_zone_item.setCheckState(QtCore.Qt.CheckState.Checked if layer.get('show_zone', True) else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 8, show_zone_item)

                # Show Max Current (checkable)
                show_max_current_ma_item = QtWidgets.QTableWidgetItem()
                show_max_current_ma_item.setFlags(show_max_current_ma_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                show_max_current_ma_item.setCheckState(QtCore.Qt.CheckState.Checked if layer.get('show_max_current_ma', True) else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 9, show_max_current_ma_item)

                # Show Voltage (checkable)
                show_voltage_v_item = QtWidgets.QTableWidgetItem()
                show_voltage_v_item.setFlags(show_voltage_v_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                show_voltage_v_item.setCheckState(QtCore.Qt.CheckState.Checked if layer.get('show_voltage_v', True) else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 10, show_voltage_v_item)

                # Show Addressable (checkable)
                show_addressable_item = QtWidgets.QTableWidgetItem()
                show_addressable_item.setFlags(show_addressable_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                show_addressable_item.setCheckState(QtCore.Qt.CheckState.Checked if layer.get('show_addressable', True) else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 11, show_addressable_item)

                # Show Candela Options (checkable)
                show_candela_options_item = QtWidgets.QTableWidgetItem()
                show_candela_options_item.setFlags(show_candela_options_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                show_candela_options_item.setCheckState(QtCore.Qt.CheckState.Checked if layer.get('show_candela_options', True) else QtCore.Qt.CheckState.Unchecked)
                self.layer_table.setItem(row, 12, show_candela_options_item)

                # Active (radio button)
                active_radio = QtWidgets.QRadioButton()
                active_radio.setChecked(layer['id'] == self.parent.active_layer_id)
                active_radio.toggled.connect(lambda checked, layer_id=layer['id']: self.set_active_layer(layer_id, checked))
                self.layer_table.setCellWidget(row, 13, active_radio)

        except Exception as e:
            print(f"Error populating layers: {e}")

    def update_layer_in_db(self, item):
        row = item.row()
        col = item.column()
        layer_id = self.layer_table.item(row, 0).data(QtCore.Qt.UserRole)

        try:
            con = db_loader.connect()
            cur = con.cursor()
            
            if col == 0: # Name
                cur.execute("UPDATE layers SET name = ? WHERE id = ?", (item.text(), layer_id))
            elif col == 2: # Visible
                cur.execute("UPDATE layers SET visible = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            elif col == 3: # Locked
                cur.execute("UPDATE layers SET locked = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            elif col == 4: # Show Name
                cur.execute("UPDATE layers SET show_name = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            elif col == 5: # Show Part #
                cur.execute("UPDATE layers SET show_part_number = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            elif col == 6: # Show SLC Address
                cur.execute("UPDATE layers SET show_slc_address = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            elif col == 7: # Show Circuit ID
                cur.execute("UPDATE layers SET show_circuit_id = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            elif col == 8: # Show Zone
                cur.execute("UPDATE layers SET show_zone = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            elif col == 9: # Show Max Current
                cur.execute("UPDATE layers SET show_max_current_ma = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            elif col == 10: # Show Voltage
                cur.execute("UPDATE layers SET show_voltage_v = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            elif col == 11: # Show Addressable
                cur.execute("UPDATE layers SET show_addressable = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            elif col == 12: # Show Candela Options
                cur.execute("UPDATE layers SET show_candela_options = ? WHERE id = ?", (item.checkState() == QtCore.Qt.CheckState.Checked, layer_id))
            
            con.commit()
            con.close()
            
            # Trigger a refresh of devices on canvas if layer properties changed
            self.parent.refresh_devices_on_canvas()

        except Exception as e:
            print(f"Error updating layer in DB: {e}")

    def pick_color(self, row):
        layer_id = self.layer_table.item(row, 0).data(QtCore.Qt.UserRole)
        current_color = self.layer_table.cellWidget(row, 1).palette().button().color()
        color = QtWidgets.QColorDialog.getColor(current_color, self)
        if color.isValid():
            try:
                con = db_loader.connect()
                cur = con.cursor()
                cur.execute("UPDATE layers SET color = ? WHERE id = ?", (color.name(), layer_id))
                con.commit()
                con.close()
                self.populate_layers()
                self.parent.refresh_devices_on_canvas()
            except Exception as e:
                print(f"Error updating layer color in DB: {e}")

    def remove_layer(self):
        current_row = self.layer_table.currentRow()
        if current_row >= 0:
            layer_name = self.layer_table.item(current_row, 0).text()
            layer_id = self.layer_table.item(current_row, 0).data(QtCore.Qt.UserRole)
            reply = QtWidgets.QMessageBox.question(self, "Remove Layer", f"Are you sure you want to remove the layer '{layer_name}'?")
            if reply == QtWidgets.QMessageBox.Yes:
                try:
                    con = db_loader.connect()
                    cur = con.cursor()
                    cur.execute("DELETE FROM layers WHERE id = ?", (layer_id,))
                    con.commit()
                    con.close()
                    self.populate_layers()
                except Exception as e:

    def set_active_layer(self, layer_id, checked):
        if checked:
            self.parent.prefs["active_layer_id"] = layer_id
            db_loader.save_prefs(self.parent.prefs)
            self.parent.refresh_devices_on_canvas()
            print(f"Active layer set to: {layer_id}")
