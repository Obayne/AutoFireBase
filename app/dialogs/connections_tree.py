from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt


class ConnectionsTree(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Connections", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # Main widget
        self.main_widget = QtWidgets.QWidget()
        self.setWidget(self.main_widget)

        layout = QtWidgets.QVBoxLayout(self.main_widget)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()
        self.add_circuit_btn = QtWidgets.QPushButton("Add Circuit")
        self.add_circuit_btn.clicked.connect(self.add_circuit)
        self.remove_circuit_btn = QtWidgets.QPushButton("Remove Circuit")
        self.remove_circuit_btn.clicked.connect(self.remove_circuit)
        toolbar.addWidget(self.add_circuit_btn)
        toolbar.addWidget(self.remove_circuit_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Tree view for connections
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Device", "Circuit", "Address", "Status"])
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.tree)

        # Status bar
        self.status_bar = QtWidgets.QHBoxLayout()
        self.device_count_label = QtWidgets.QLabel("Devices: 0")
        self.circuit_count_label = QtWidgets.QLabel("Circuits: 0")
        self.status_bar.addWidget(self.device_count_label)
        self.status_bar.addWidget(self.circuit_count_label)
        self.status_bar.addStretch()
        layout.addLayout(self.status_bar)

        # Initialize data
        self.circuits = {}
        self.devices = {}
        self.update_status()

    def add_panel(self, name, device_item, panel_type):
        """Add a panel to the connections tree."""
        panel_item = QtWidgets.QTreeWidgetItem([name, "Panel", "-", "Online"])
        panel_item.setIcon(0, QtGui.QIcon())  # Add appropriate icon
        panel_item.setData(
            0, QtCore.Qt.ItemDataRole.UserRole, {"type": "panel", "device_item": device_item}
        )
        self.tree.addTopLevelItem(panel_item)
        self.devices[name] = {"item": panel_item, "device_item": device_item, "type": "panel"}
        self.update_status()

    def add_circuit(self):
        """Add a new circuit to the selected panel."""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.information(self, "Add Circuit", "Please select a panel first.")
            return

        panel_item = selected_items[0]
        # Find the panel item (traverse up if needed)
        while (
            panel_item
            and panel_item.data(0, QtCore.Qt.ItemDataRole.UserRole).get("type") != "panel"
        ):
            panel_item = panel_item.parent()

        if not panel_item:
            QtWidgets.QMessageBox.information(self, "Add Circuit", "Please select a panel.")
            return

        circuit_name, ok = QtWidgets.QInputDialog.getText(self, "Add Circuit", "Circuit Name:")
        if ok and circuit_name:
            circuit_item = QtWidgets.QTreeWidgetItem([circuit_name, circuit_name, "-", "Active"])
            circuit_item.setIcon(0, QtGui.QIcon())  # Add appropriate icon
            circuit_item.setData(
                0, QtCore.Qt.ItemDataRole.UserRole, {"type": "circuit", "name": circuit_name}
            )
            panel_item.addChild(circuit_item)
            self.circuits[circuit_name] = {"item": circuit_item, "devices": []}
            self.update_status()

    def remove_circuit(self):
        """Remove the selected circuit."""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.information(
                self, "Remove Circuit", "Please select a circuit to remove."
            )
            return

        circuit_item = selected_items[0]
        data = circuit_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if data.get("type") != "circuit":
            QtWidgets.QMessageBox.information(self, "Remove Circuit", "Please select a circuit.")
            return

        circuit_name = data.get("name")
        reply = QtWidgets.QMessageBox.question(
            self,
            "Remove Circuit",
            f"Are you sure you want to remove circuit '{circuit_name}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # Remove from parent
            parent = circuit_item.parent()
            if parent:
                parent.removeChild(circuit_item)

            # Remove from circuits dict
            if circuit_name in self.circuits:
                del self.circuits[circuit_name]

            self.update_status()

    def show_context_menu(self, position):
        """Show context menu for tree items."""
        item = self.tree.itemAt(position)
        if not item:
            return

        menu = QtWidgets.QMenu()
        data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        item_type = data.get("type")

        if item_type == "panel":
            add_circuit_action = menu.addAction("Add Circuit")
            add_circuit_action.triggered.connect(self.add_circuit)
        elif item_type == "circuit":
            remove_circuit_action = menu.addAction("Remove Circuit")
            remove_circuit_action.triggered.connect(self.remove_circuit)
        elif item_type == "device":
            remove_device_action = menu.addAction("Remove from Circuit")
            remove_device_action.triggered.connect(lambda: self.remove_device_from_circuit(item))

        menu.exec(self.tree.viewport().mapToGlobal(position))

    def remove_device_from_circuit(self, device_item):
        """Remove a device from its circuit."""
        data = device_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        circuit_name = data.get("circuit")

        # Remove from circuit's device list
        if circuit_name in self.circuits:
            if device_item in self.circuits[circuit_name]["devices"]:
                self.circuits[circuit_name]["devices"].remove(device_item)

        # Remove from tree
        parent = device_item.parent()
        if parent:
            parent.removeChild(device_item)

        self.update_status()

    def get_connections(self):
        """Return connection data for serialization."""
        connections = {"circuits": {}, "devices": {}}

        # Collect circuit data
        for circuit_name, circuit_data in self.circuits.items():
            connections["circuits"][circuit_name] = {"devices": []}
            # Collect devices in this circuit
            for device_item in circuit_data["devices"]:
                device_data = device_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
                connections["circuits"][circuit_name]["devices"].append(
                    {
                        "name": device_item.text(0),
                        "address": device_item.text(2),
                        "device_id": device_data.get("device_id", ""),
                    }
                )

        # Collect device data
        for device_name, device_data in self.devices.items():
            connections["devices"][device_name] = {"type": device_data["type"]}

        return connections

    def load_connections(self, connections_data, device_map):
        """Load connection data from serialized data."""
        # Clear existing data
        self.tree.clear()
        self.circuits.clear()
        self.devices.clear()

        # Load devices
        for device_name, device_info in connections_data.get("devices", {}).items():
            if device_name in device_map:
                device_item = device_map[device_name]
                self.devices[device_name] = {
                    "item": None,  # Will be set when added to tree
                    "device_item": device_item,
                    "type": device_info["type"],
                }

        # Load circuits
        for circuit_name, circuit_info in connections_data.get("circuits", {}).items():
            circuit_item = QtWidgets.QTreeWidgetItem([circuit_name, circuit_name, "-", "Active"])
            circuit_item.setData(
                0, QtCore.Qt.ItemDataRole.UserRole, {"type": "circuit", "name": circuit_name}
            )
            self.tree.addTopLevelItem(circuit_item)
            self.circuits[circuit_name] = {"item": circuit_item, "devices": []}

            # Load devices in circuit
            for device_data in circuit_info.get("devices", []):
                device_id = device_data.get("device_id")
                if device_id in device_map:
                    device_item = device_map[device_id]
                    address = device_data.get("address", "")
                    device_tree_item = QtWidgets.QTreeWidgetItem(
                        [device_data.get("name", ""), circuit_name, address, "Active"]
                    )
                    device_tree_item.setData(
                        0,
                        QtCore.Qt.ItemDataRole.UserRole,
                        {"type": "device", "device_id": device_id, "circuit": circuit_name},
                    )
                    circuit_item.addChild(device_tree_item)
                    self.circuits[circuit_name]["devices"].append(device_tree_item)

        self.update_status()

    def update_status(self):
        """Update the status bar with current counts."""
        device_count = len(self.devices)
        circuit_count = len(self.circuits)
        self.device_count_label.setText(f"Devices: {device_count}")
        self.circuit_count_label.setText(f"Circuits: {circuit_count}")
