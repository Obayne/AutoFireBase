from PySide6 import QtWidgets
from db import loader as db_loader

class WireSpoolDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wire Spool")
        self.setModal(True)
        self.resize(400, 300)

        layout = QtWidgets.QVBoxLayout(self)

        self.wire_list = QtWidgets.QListWidget()
        layout.addWidget(self.wire_list)

        self.populate_wires()

        # Add OK and Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_wire(self):
        selected_item = self.wire_list.currentItem()
        if selected_item:
            row = self.wire_list.row(selected_item)
            return self.wires[row]
        return None

    def populate_wires(self):
        try:
            con = db_loader.connect()
            self.wires = db_loader.fetch_wires(con)
            con.close()

            for wire in self.wires:
                item_text = f"{wire['manufacturer']} {wire['type']} {wire['gauge']} {wire['color']}"
                self.wire_list.addItem(item_text)
        except Exception as e:
            print(f"Error populating wires: {e}")
