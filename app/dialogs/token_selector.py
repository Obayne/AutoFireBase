from PySide6 import QtWidgets, QtCore

class TokenSelectorDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, device=None):
        super().__init__(parent)
        self.setWindowTitle("Select Token")
        self.setModal(True)
        self.resize(300, 400)
        self.device = device
        self.selected_token = None

        layout = QtWidgets.QVBoxLayout(self)

        self.token_list = QtWidgets.QListWidget()
        layout.addWidget(self.token_list)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.populate_tokens()

    def populate_tokens(self):
        # For now, a hardcoded list of common tokens
        # In the future, this will dynamically populate based on device properties
        tokens = [
            "{name}",
            "{symbol}",
            "{part_number}",
            "{manufacturer}",
            "{device_type}",
            "{system_category}",
            "{layer_name}",
            "{slc_address}",
            "{circuit_id}",
            "{zone}",
            "{max_current_ma}",
            "{voltage_v}",
            "{addressable}",
            "{candela_options}"
        ]
        self.token_list.addItems(tokens)

    def accept(self):
        selected_item = self.token_list.currentItem()
        if selected_item:
            self.selected_token = selected_item.text()
        super().accept()

    def get_selected_token(self):
        return self.selected_token
