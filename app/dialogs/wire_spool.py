from PySide6 import QtCore, QtWidgets


class WireSpoolDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wire Spool Selection")
        self.setModal(True)
        self.resize(500, 400)

        self.selected_wire = None

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Select Wire Type")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Wire type selection
        layout.addWidget(QtWidgets.QLabel("Available Wire Types:"))

        self.wire_list = QtWidgets.QListWidget()
        self.wire_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.populate_wire_list()
        self.wire_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.wire_list)

        # Wire properties
        props_group = QtWidgets.QGroupBox("Wire Properties")
        props_layout = QtWidgets.QFormLayout(props_group)

        self.gauge_label = QtWidgets.QLabel()
        props_layout.addRow("Gauge:", self.gauge_label)

        self.material_label = QtWidgets.QLabel()
        props_layout.addRow("Material:", self.material_label)

        self.insulation_label = QtWidgets.QLabel()
        props_layout.addRow("Insulation:", self.insulation_label)

        self.color_label = QtWidgets.QLabel()
        props_layout.addRow("Color:", self.color_label)

        self.length_label = QtWidgets.QLabel()
        props_layout.addRow("Length (ft):", self.length_label)

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
        self.wire_list.currentItemChanged.connect(self.update_wire_properties)

        # Select first item by default
        if self.wire_list.count() > 0:
            self.wire_list.setCurrentRow(0)

    def populate_wire_list(self):
        # Sample wire types - in a real application, this would come from a database
        wire_types = [
            {
                "manufacturer": "Belden",
                "type": "18 AWG",
                "gauge": "18 AWG",
                "material": "Copper",
                "insulation": "PVC",
                "color": "Red",
                "length": "1000",
            },
            {
                "manufacturer": "Belden",
                "type": "16 AWG",
                "gauge": "16 AWG",
                "material": "Copper",
                "insulation": "PVC",
                "color": "Black",
                "length": "1000",
            },
            {
                "manufacturer": "Alpha Wire",
                "type": "14 AWG",
                "gauge": "14 AWG",
                "material": "Copper",
                "insulation": "Teflon",
                "color": "Blue",
                "length": "500",
            },
            {
                "manufacturer": "Alpha Wire",
                "type": "12 AWG",
                "gauge": "12 AWG",
                "material": "Copper",
                "insulation": "PVC",
                "color": "White",
                "length": "500",
            },
            {
                "manufacturer": "General Cable",
                "type": "10 AWG",
                "gauge": "10 AWG",
                "material": "Copper",
                "insulation": "XLPE",
                "color": "Green",
                "length": "1000",
            },
        ]

        for wire in wire_types:
            item_text = f"{wire['manufacturer']} {wire['type']}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, wire)
            self.wire_list.addItem(item)

    def update_wire_properties(self, current, previous):
        if current:
            wire_data = current.data(QtCore.Qt.ItemDataRole.UserRole)
            if wire_data:
                self.gauge_label.setText(wire_data.get("gauge", ""))
                self.material_label.setText(wire_data.get("material", ""))
                self.insulation_label.setText(wire_data.get("insulation", ""))
                self.color_label.setText(wire_data.get("color", ""))
                self.length_label.setText(wire_data.get("length", ""))

    def get_selected_wire(self):
        current_item = self.wire_list.currentItem()
        if current_item:
            return current_item.data(QtCore.Qt.ItemDataRole.UserRole)
        return None
