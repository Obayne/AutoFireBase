from PySide6 import QtCore, QtGui, QtWidgets
from typing import List, Dict, Any

class FACPPanel:
    """Represents a Fire Alarm Control Panel with its accessories."""
    
    def __init__(self, model: str, manufacturer: str):
        self.model = model
        self.manufacturer = manufacturer
        self.accessories = []
        self.max_devices = 0
        self.max_circuits = 0
        self.panel_type = "Conventional"  # or "Addressable"
        
    def add_accessory(self, accessory: Dict[str, Any]):
        """Add an accessory to the panel."""
        self.accessories.append(accessory)
        
    def set_capacity(self, max_devices: int, max_circuits: int):
        """Set the panel capacity."""
        self.max_devices = max_devices
        self.max_circuits = max_circuits

class FACPWizardDialog(QtWidgets.QDialog):
    """Wizard dialog for FACP panel placement with accessory selection."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FACP Panel Placement Wizard")
        self.setModal(True)
        self.resize(600, 500)
        
        self.panel = None
        self.panels = []
        self.accessory_options = self._get_accessory_options()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Header
        header_label = QtWidgets.QLabel("FACP Panel Placement Wizard")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header_label)
        
        # Panel selection
        panel_group = QtWidgets.QGroupBox("Panel Selection")
        panel_layout = QtWidgets.QFormLayout(panel_group)
        
        self.manufacturer_combo = QtWidgets.QComboBox()
        self.manufacturer_combo.addItems(["System Sensor", "Notifier", "Honeywell", "Gentex", "Other"])
        self.manufacturer_combo.currentTextChanged.connect(self._on_manufacturer_changed)
        panel_layout.addRow("Manufacturer:", self.manufacturer_combo)
        
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.addItems(["FS2000", "FS3000", "FS6000"])
        panel_layout.addRow("Model:", self.model_combo)
        
        self.panel_type_combo = QtWidgets.QComboBox()
        self.panel_type_combo.addItems(["Conventional", "Addressable"])
        panel_layout.addRow("Panel Type:", self.panel_type_combo)
        
        layout.addWidget(panel_group)
        
        # Accessories selection
        accessories_group = QtWidgets.QGroupBox("Accessories")
        accessories_layout = QtWidgets.QVBoxLayout(accessories_group)
        
        # Accessories list with checkboxes
        self.accessories_list = QtWidgets.QListWidget()
        self.accessories_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        
        for accessory in self.accessory_options:
            item = QtWidgets.QListWidgetItem()
            widget = self._create_accessory_widget(accessory)
            item.setSizeHint(widget.sizeHint())
            self.accessories_list.addItem(item)
            self.accessories_list.setItemWidget(item, widget)
            
        accessories_layout.addWidget(self.accessories_list)
        layout.addWidget(accessories_group)
        
        # Capacity information
        capacity_group = QtWidgets.QGroupBox("Panel Capacity")
        capacity_layout = QtWidgets.QFormLayout(capacity_group)
        
        self.max_devices_spin = QtWidgets.QSpinBox()
        self.max_devices_spin.setRange(0, 1000)
        self.max_devices_spin.setValue(200)
        capacity_layout.addRow("Maximum Devices:", self.max_devices_spin)
        
        self.max_circuits_spin = QtWidgets.QSpinBox()
        self.max_circuits_spin.setRange(0, 50)
        self.max_circuits_spin.setValue(10)
        capacity_layout.addRow("Maximum Circuits:", self.max_circuits_spin)
        
        layout.addWidget(capacity_group)

        # Panel list
        panel_list_group = QtWidgets.QGroupBox("Configured Panels")
        panel_list_layout = QtWidgets.QVBoxLayout(panel_list_group)
        self.panel_list = QtWidgets.QListWidget()
        panel_list_layout.addWidget(self.panel_list)

        panel_buttons_layout = QtWidgets.QHBoxLayout()
        self.add_panel_button = QtWidgets.QPushButton("Add Panel")
        self.add_panel_button.clicked.connect(self.add_panel)
        self.remove_panel_button = QtWidgets.QPushButton("Remove Panel")
        self.remove_panel_button.clicked.connect(self.remove_panel)
        panel_buttons_layout.addWidget(self.add_panel_button)
        panel_buttons_layout.addWidget(self.remove_panel_button)
        panel_list_layout.addLayout(panel_buttons_layout)

        layout.addWidget(panel_list_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.ok_button = QtWidgets.QPushButton("Place Panel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
    def _get_accessory_options(self) -> List[Dict[str, Any]]:
        """Get available accessory options."""
        return [
            {"name": "Remote Annunciator", "description": "Remote display for system status", "selected": False},
            {"name": "Battery Charger", "description": "Backup battery charging module", "selected": False},
            {"name": "Network Card", "description": "Ethernet connectivity module", "selected": False},
            {"name": "RS-485 Module", "description": "Serial communication module", "selected": False},
            {"name": "Relay Module", "description": "Programmable relay outputs", "selected": False},
            {"name": "Printer Module", "description": "Event printer interface", "selected": False},
            {"name": "Power Supply", "description": "Additional power supply module", "selected": False},
            {"name": "Expander Board", "description": "Additional zone expander", "selected": False}
        ]
        
    def _create_accessory_widget(self, accessory: Dict[str, Any]) -> QtWidgets.QWidget:
        """Create a widget for an accessory option."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        checkbox = QtWidgets.QCheckBox(accessory["name"])
        checkbox.setChecked(accessory["selected"])
        checkbox.setProperty("accessory_data", accessory)
        layout.addWidget(checkbox)
        
        description = QtWidgets.QLabel(accessory["description"])
        description.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(description)
        layout.addStretch()
        
        return widget
        
    def _on_manufacturer_changed(self, manufacturer: str):
        """Handle manufacturer selection change."""
        # Update model options based on manufacturer
        self.model_combo.clear()
        if manufacturer == "System Sensor":
            self.model_combo.addItems(["FS2000", "FS3000", "FS6000"])
        elif manufacturer == "Notifier":
            self.model_combo.addItems(["ONYX", "ALG", "MX"])
        elif manufacturer == "Honeywell":
            self.model_combo.addItems(["XLS", "GMS", "AMF"])
        else:
            self.model_combo.addItems(["Generic Model 1", "Generic Model 2"])
            
    def get_panel_configuration(self) -> FACPPanel:
        """Get the configured FACP panel."""
        manufacturer = self.manufacturer_combo.currentText()
        model = self.model_combo.currentText()
        
        panel = FACPPanel(model, manufacturer)
        panel.panel_type = self.panel_type_combo.currentText()
        panel.set_capacity(self.max_devices_spin.value(), self.max_circuits_spin.value())
        
        # Add selected accessories
        for i in range(self.accessories_list.count()):
            item = self.accessories_list.item(i)
            widget = self.accessories_list.itemWidget(item)
            checkbox = widget.findChild(QtWidgets.QCheckBox)
            if checkbox and checkbox.isChecked():
                accessory_data = checkbox.property("accessory_data")
                panel.add_accessory(accessory_data)
                
        return panel

    def add_panel(self):
        """Add a new panel to the list of configured panels."""
        panel = self.get_panel_configuration()
        self.panels.append(panel)
        self.panel_list.addItem(f"{panel.manufacturer} {panel.model}")

    def remove_panel(self):
        """Remove the selected panel from the list."""
        selected_item = self.panel_list.currentItem()
        if selected_item:
            row = self.panel_list.row(selected_item)
            self.panel_list.takeItem(row)
            del self.panels[row]

    def get_panel_configurations(self) -> List[FACPPanel]:
        """Get the list of configured FACP panels."""
        return self.panels
        
    def accept(self):
        """Handle dialog acceptance."""
        # If no panels have been added, add the current configuration
        if not self.panels:
            self.add_panel()

        # Validate inputs
        if not self.manufacturer_combo.currentText() or not self.model_combo.currentText():
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please select a manufacturer and model.")
            return
            
        super().accept()