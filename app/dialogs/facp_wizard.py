from PySide6 import QtWidgets


class FACPPanel:
    def __init__(
        self, model, manufacturer, panel_type, max_devices, max_circuits, accessories=None
    ):
        self.model = model
        self.manufacturer = manufacturer
        self.panel_type = panel_type
        self.max_devices = max_devices
        self.max_circuits = max_circuits
        self.accessories = accessories or []


class FACPWizardDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FACP System Configuration Wizard")
        self.setModal(True)
        self.resize(600, 500)

        self.panels = []

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("FACP System Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Panel list
        self.panel_list = QtWidgets.QListWidget()
        self.panel_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(QtWidgets.QLabel("Configured Panels:"))
        layout.addWidget(self.panel_list)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.add_panel_btn = QtWidgets.QPushButton("Add Panel")
        self.add_panel_btn.clicked.connect(self.add_panel)
        self.edit_panel_btn = QtWidgets.QPushButton("Edit Panel")
        self.edit_panel_btn.clicked.connect(self.edit_panel)
        self.remove_panel_btn = QtWidgets.QPushButton("Remove Panel")
        self.remove_panel_btn.clicked.connect(self.remove_panel)
        self.clear_btn = QtWidgets.QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_panels)

        button_layout.addWidget(self.add_panel_btn)
        button_layout.addWidget(self.edit_panel_btn)
        button_layout.addWidget(self.remove_panel_btn)
        button_layout.addWidget(self.clear_btn)
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

    def add_panel(self):
        dialog = PanelConfigDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            panel = dialog.get_panel()
            self.panels.append(panel)
            self.update_panel_list()

    def edit_panel(self):
        current_row = self.panel_list.currentRow()
        if current_row >= 0 and current_row < len(self.panels):
            dialog = PanelConfigDialog(self, self.panels[current_row])
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                self.panels[current_row] = dialog.get_panel()
                self.update_panel_list()

    def remove_panel(self):
        current_row = self.panel_list.currentRow()
        if current_row >= 0 and current_row < len(self.panels):
            self.panels.pop(current_row)
            self.update_panel_list()

    def clear_panels(self):
        self.panels.clear()
        self.update_panel_list()

    def update_panel_list(self):
        self.panel_list.clear()
        for panel in self.panels:
            item_text = f"{panel.manufacturer} {panel.model} ({panel.panel_type})"
            self.panel_list.addItem(item_text)

    def get_panel_configurations(self):
        return self.panels

    def exec(self):
        self.update_panel_list()
        return super().exec()


class PanelConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, panel=None):
        super().__init__(parent)
        self.setWindowTitle("Configure FACP Panel" if not panel else "Edit FACP Panel")
        self.setModal(True)
        self.resize(400, 300)

        self.panel = panel

        layout = QtWidgets.QVBoxLayout(self)

        # Form
        form_layout = QtWidgets.QFormLayout()

        self.manufacturer_combo = QtWidgets.QComboBox()
        self.manufacturer_combo.addItems(["Notifier", "Honeywell", "Siemens", "Other"])
        form_layout.addRow("Manufacturer:", self.manufacturer_combo)

        self.model_edit = QtWidgets.QLineEdit()
        form_layout.addRow("Model:", self.model_edit)

        self.panel_type_combo = QtWidgets.QComboBox()
        self.panel_type_combo.addItems(["Conventional", "Addressable", "Hybrid"])
        form_layout.addRow("Panel Type:", self.panel_type_combo)

        self.max_devices_spin = QtWidgets.QSpinBox()
        self.max_devices_spin.setRange(1, 1000)
        self.max_devices_spin.setValue(200)
        form_layout.addRow("Max Devices:", self.max_devices_spin)

        self.max_circuits_spin = QtWidgets.QSpinBox()
        self.max_circuits_spin.setRange(1, 50)
        self.max_circuits_spin.setValue(10)
        form_layout.addRow("Max Circuits:", self.max_circuits_spin)

        layout.addLayout(form_layout)

        # Accessories
        layout.addWidget(QtWidgets.QLabel("Accessories:"))
        self.accessories_list = QtWidgets.QListWidget()
        layout.addWidget(self.accessories_list)

        # Accessories buttons
        accessories_layout = QtWidgets.QHBoxLayout()
        self.add_accessory_btn = QtWidgets.QPushButton("Add Accessory")
        self.add_accessory_btn.clicked.connect(self.add_accessory)
        self.remove_accessory_btn = QtWidgets.QPushButton("Remove Accessory")
        self.remove_accessory_btn.clicked.connect(self.remove_accessory)
        accessories_layout.addWidget(self.add_accessory_btn)
        accessories_layout.addWidget(self.remove_accessory_btn)
        accessories_layout.addStretch()
        layout.addLayout(accessories_layout)

        # OK/Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Populate fields if editing
        if self.panel:
            self.manufacturer_combo.setCurrentText(self.panel.manufacturer)
            self.model_edit.setText(self.panel.model)
            self.panel_type_combo.setCurrentText(self.panel.panel_type)
            self.max_devices_spin.setValue(self.panel.max_devices)
            self.max_circuits_spin.setValue(self.panel.max_circuits)
            for accessory in self.panel.accessories:
                self.accessories_list.addItem(accessory)

    def add_accessory(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Add Accessory", "Accessory Name:")
        if ok and text:
            self.accessories_list.addItem(text)

    def remove_accessory(self):
        current_row = self.accessories_list.currentRow()
        if current_row >= 0:
            self.accessories_list.takeItem(current_row)

    def get_panel(self):
        accessories = []
        for i in range(self.accessories_list.count()):
            accessories.append(self.accessories_list.item(i).text())

        return FACPPanel(
            model=self.model_edit.text(),
            manufacturer=self.manufacturer_combo.currentText(),
            panel_type=self.panel_type_combo.currentText(),
            max_devices=self.max_devices_spin.value(),
            max_circuits=self.max_circuits_spin.value(),
            accessories=accessories,
        )
