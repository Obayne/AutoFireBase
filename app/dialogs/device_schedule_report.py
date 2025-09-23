from PySide6 import QtWidgets, QtCore

class DeviceScheduleReportDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Device Schedule Report")
        self.setModal(True)
        self.resize(1000, 800)

        self.parent = parent # MainWindow instance

        layout = QtWidgets.QVBoxLayout(self)

        self.schedule_table = QtWidgets.QTableWidget()
        self.schedule_table.setColumnCount(8)
        self.schedule_table.setHorizontalHeaderLabels(["Name", "Symbol", "Type", "Manufacturer", "Part Number", "SLC Address", "Circuit ID", "Zone"])
        self.schedule_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.schedule_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.schedule_table)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.generate_schedule()

    def generate_schedule(self):
        schedule_data = []

        # Iterate through all devices on the canvas
        for item in self.parent.layer_devices.childItems():
            if isinstance(item, self.parent.DeviceItem):
                schedule_data.append({
                    "name": item.name,
                    "symbol": item.symbol,
                    "type": item.device_type,
                    "manufacturer": item.manufacturer,
                    "part_number": item.part_number,
                    "slc_address": item.slc_address if item.slc_address is not None else "N/A",
                    "circuit_id": item.circuit_id if item.circuit_id is not None else "N/A",
                    "zone": item.zone if item.zone else "N/A"
                })

        # Populate the table
        self.schedule_table.setRowCount(len(schedule_data))
        for row, device in enumerate(schedule_data):
            self.schedule_table.setItem(row, 0, QtWidgets.QTableWidgetItem(device["name"]))
            self.schedule_table.setItem(row, 1, QtWidgets.QTableWidgetItem(device["symbol"]))
            self.schedule_table.setItem(row, 2, QtWidgets.QTableWidgetItem(device["type"]))
            self.schedule_table.setItem(row, 3, QtWidgets.QTableWidgetItem(device["manufacturer"]))
            self.schedule_table.setItem(row, 4, QtWidgets.QTableWidgetItem(device["part_number"]))
            self.schedule_table.setItem(row, 5, QtWidgets.QTableWidgetItem(str(device["slc_address"])))
            self.schedule_table.setItem(row, 6, QtWidgets.QTableWidgetItem(str(device["circuit_id"])))
            self.schedule_table.setItem(row, 7, QtWidgets.QTableWidgetItem(device["zone"]))

        self.schedule_table.resizeColumnsToContents()
