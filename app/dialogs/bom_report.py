from PySide6 import QtWidgets, QtCore

class BomReportDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bill of Materials Report")
        self.setModal(True)
        self.resize(800, 600)

        self.parent = parent # MainWindow instance

        layout = QtWidgets.QVBoxLayout(self)

        self.bom_table = QtWidgets.QTableWidget()
        self.bom_table.setColumnCount(4)
        self.bom_table.setHorizontalHeaderLabels(["Part Number", "Manufacturer", "Description", "Quantity"])
        self.bom_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.bom_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.bom_table)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.generate_bom()

    def generate_bom(self):
        bom_data = {}

        # Iterate through all devices on the canvas
        for item in self.parent.layer_devices.childItems():
            if isinstance(item, self.parent.DeviceItem):
                part_number = item.part_number
                manufacturer = item.manufacturer
                name = item.name

                if part_number not in bom_data:
                    bom_data[part_number] = {
                        "manufacturer": manufacturer,
                        "description": name,
                        "quantity": 0
                    }
                bom_data[part_number]["quantity"] += 1

        # Populate the table
        self.bom_table.setRowCount(len(bom_data))
        for row, (part_number, data) in enumerate(bom_data.items()):
            self.bom_table.setItem(row, 0, QtWidgets.QTableWidgetItem(part_number))
            self.bom_table.setItem(row, 1, QtWidgets.QTableWidgetItem(data["manufacturer"]))
            self.bom_table.setItem(row, 2, QtWidgets.QTableWidgetItem(data["description"]))
            self.bom_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(data["quantity"])))

        self.bom_table.resizeColumnsToContents()
