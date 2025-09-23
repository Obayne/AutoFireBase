from PySide6 import QtWidgets, QtCore

class CircuitPropertiesDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, circuit_data=None, panel_id=None):
        super().__init__(parent)
        self.setWindowTitle("Circuit Properties")
        self.setModal(True)
        self.resize(400, 300)

        self.circuit_data = circuit_data or {}
        self.circuit_data['panel_id'] = panel_id

        # Fetch existing circuit data from DB
        try:
            con = db_loader.connect()
            existing_circuit = db_loader.fetch_circuit(con, self.circuit_data['panel_id'])
            con.close()
            if existing_circuit:
                self.circuit_data.update(existing_circuit)
        except Exception as e:
            print(f"Error fetching existing circuit data: {e}")

        layout = QtWidgets.QFormLayout(self)

        self.circuit_type_label = QtWidgets.QLabel(f"Circuit Type: {self.circuit_data.get('circuit_type', 'N/A')}")
        layout.addRow(self.circuit_type_label)

        self.capacity_spin = QtWidgets.QSpinBox()
        self.capacity_spin.setRange(0, 1000)
        self.capacity_spin.setValue(self.circuit_data.get('capacity', 0))
        layout.addRow("Capacity:", self.capacity_spin)

        self.cable_length_spin = QtWidgets.QDoubleSpinBox()
        self.cable_length_spin.setRange(0.0, 10000.0)
        self.cable_length_spin.setDecimals(2)
        self.cable_length_spin.setValue(self.circuit_data.get('cable_length', 0.0))
        layout.addRow("Additional Cable Length (ft):", self.cable_length_spin)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        # Save to database
        try:
            con = db_loader.connect()
            db_loader.save_circuit(con, self.circuit_data['panel_id'], self.circuit_data['circuit_type'],
                                   self.capacity_spin.value(), self.cable_length_spin.value())
            con.close()
            self.parent.refresh_connections_tree() # Refresh the tree in MainWindow
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Save Error", f"Failed to save circuit properties: {e}")
            return # Don't accept if save fails

        super().accept()
