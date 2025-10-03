from PySide6 import QtCore, QtWidgets

# Token list contains long descriptive strings for UI clarity; silence E501 here.
# ruff: noqa: E501
# noqa: E501


class TokenSelectorDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Token")
        self.setModal(True)
        self.resize(400, 300)

        self.selected_token = None

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Select Token Type")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Token categories
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(["Devices", "Annotations", "Symbols", "Custom"])
        self.category_combo.currentTextChanged.connect(self.update_token_list)
        layout.addWidget(self.category_combo)

        # Token list
        layout.addWidget(QtWidgets.QLabel("Available Tokens:"))

        self.token_list = QtWidgets.QListWidget()
        self.token_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.token_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.token_list)

        # Token preview
        preview_group = QtWidgets.QGroupBox("Preview")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        self.preview_label = QtWidgets.QLabel()
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(100)
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)

        # Token properties
        props_group = QtWidgets.QGroupBox("Token Properties")
        props_layout = QtWidgets.QFormLayout(props_group)

        self.token_name_label = QtWidgets.QLabel()
        props_layout.addRow("Name:", self.token_name_label)

        self.token_type_label = QtWidgets.QLabel()
        props_layout.addRow("Type:", self.token_type_label)

        self.token_desc_label = QtWidgets.QLabel()
        props_layout.addRow("Description:", self.token_desc_label)

        layout.addWidget(props_group)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.select_btn = QtWidgets.QPushButton("Select")
        self.select_btn.clicked.connect(self.accept)
        self.select_btn.setDefault(True)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        # Connect selection change
        self.token_list.currentItemChanged.connect(self.update_token_preview)

        # Populate initial token list
        self.update_token_list("Devices")

        # Select first item by default
        if self.token_list.count() > 0:
            self.token_list.setCurrentRow(0)

    def update_token_list(self, category):
        """Update the token list based on the selected category."""
        self.token_list.clear()

        # Sample tokens by category - in a real application, this would come from a database or configuration
        tokens = {
            "Devices": [
                {
                    "name": "Device ID",
                    "type": "Text",
                    "description": "Unique identifier for the device",
                    "preview": "DEV-001",
                },
                {
                    "name": "Device Type",
                    "type": "Text",
                    "description": "Type of the device",
                    "preview": "Smoke Detector",
                },
                {
                    "name": "Manufacturer",
                    "type": "Text",
                    "description": "Device manufacturer",
                    "preview": "Notifier",
                },
                {
                    "name": "Model",
                    "type": "Text",
                    "description": "Device model number",
                    "preview": "FSP-851",
                },
                {
                    "name": "Address",
                    "type": "Text",
                    "description": "SLC address",
                    "preview": "15-07",
                },
                {
                    "name": "Circuit",
                    "type": "Text",
                    "description": "Circuit number",
                    "preview": "NAC-2",
                },
            ],
            "Annotations": [
                {
                    "name": "Room Number",
                    "type": "Text",
                    "description": "Room identification number",
                    "preview": "101",
                },
                {
                    "name": "Area",
                    "type": "Text",
                    "description": "Fire area designation",
                    "preview": "A-1",
                },
                {
                    "name": "Ceiling Height",
                    "type": "Text",
                    "description": "Ceiling height in feet",
                    "preview": "10'0\"",
                },
                {
                    "name": "Coverage Area",
                    "type": "Text",
                    "description": "Protected area in square feet",
                    "preview": "500 sq ft",
                },
            ],
            "Symbols": [
                {
                    "name": "North Arrow",
                    "type": "Symbol",
                    "description": "North direction indicator",
                    "preview": "↑N",
                },
                {
                    "name": "Scale Bar",
                    "type": "Symbol",
                    "description": "Drawing scale reference",
                    "preview": "|_____| 10'",
                },
                {
                    "name": "Revision Cloud",
                    "type": "Symbol",
                    "description": "Revision indicator",
                    "preview": "☁",
                },
                {
                    "name": "Detail Callout",
                    "type": "Symbol",
                    "description": "Detail reference",
                    "preview": "⌀",
                },
            ],
            "Custom": [
                {
                    "name": "Project Name",
                    "type": "Text",
                    "description": "Current project name",
                    "preview": "Office Building",
                },
                {
                    "name": "Drawing Number",
                    "type": "Text",
                    "description": "Current drawing number",
                    "preview": "A-101",
                },
                {
                    "name": "Date",
                    "type": "Text",
                    "description": "Current date",
                    "preview": "2025-01-15",
                },
                {
                    "name": "Designer",
                    "type": "Text",
                    "description": "Designer name",
                    "preview": "John Smith",
                },
            ],
        }

        category_tokens = tokens.get(category, [])
        for token in category_tokens:
            item = QtWidgets.QListWidgetItem(token["name"])
            item.setData(QtCore.Qt.ItemDataRole.UserRole, token)
            self.token_list.addItem(item)

    def update_token_preview(self, current, previous):
        """Update the token preview based on the selected token."""
        if current:
            token_data = current.data(QtCore.Qt.ItemDataRole.UserRole)
            if token_data:
                self.token_name_label.setText(token_data.get("name", ""))
                self.token_type_label.setText(token_data.get("type", ""))
                self.token_desc_label.setText(token_data.get("description", ""))
                self.preview_label.setText(token_data.get("preview", ""))

    def get_selected_token(self):
        """Return the selected token data."""
        current_item = self.token_list.currentItem()
        if current_item:
            return current_item.data(QtCore.Qt.ItemDataRole.UserRole)
        return None
