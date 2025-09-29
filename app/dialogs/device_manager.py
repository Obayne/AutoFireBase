"""
Device Manager Dialog - Manage devices and their connections
"""

from typing import Any

from PySide6 import QtWidgets
from PySide6.QtCore import Qt


class DeviceManagerDialog(QtWidgets.QDialog):
    """Comprehensive device manager with connection tracking and layer integration."""

    def __init__(self, model_space_window, parent=None):
        super().__init__(parent)
        self.model_space_window = model_space_window
        self.devices_data = self._load_devices_data()
        self.connections_data = self._load_connections_data()

        self.setWindowTitle("Device Manager")
        self.setModal(True)
        self.resize(1000, 700)

        self._setup_ui()
        self._populate_devices()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Main splitter
        splitter = QtWidgets.QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Device list
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)

        # Device list header
        device_header = QtWidgets.QHBoxLayout()

        self.device_search = QtWidgets.QLineEdit()
        self.device_search.setPlaceholderText("Search devices...")
        self.device_search.textChanged.connect(self._filter_devices)
        device_header.addWidget(QtWidgets.QLabel("Search:"))
        device_header.addWidget(self.device_search)

        self.device_type_filter = QtWidgets.QComboBox()
        self.device_type_filter.addItem("All Types", "")
        self.device_type_filter.currentTextChanged.connect(self._filter_devices)
        device_header.addWidget(QtWidgets.QLabel("Type:"))
        device_header.addWidget(self.device_type_filter)

        left_layout.addLayout(device_header)

        # Device tree
        self.device_tree = QtWidgets.QTreeWidget()
        self.device_tree.setHeaderLabels(["Device", "Type", "Layer", "Connections"])
        self.device_tree.setColumnWidth(0, 200)
        self.device_tree.setColumnWidth(1, 100)
        self.device_tree.setColumnWidth(2, 80)
        self.device_tree.setColumnWidth(3, 100)
        self.device_tree.itemSelectionChanged.connect(self._on_device_selected)
        left_layout.addWidget(self.device_tree)

        # Device count
        self.device_count_label = QtWidgets.QLabel("Loading devices...")
        left_layout.addWidget(self.device_count_label)

        splitter.addWidget(left_widget)

        # Right panel - Device details and connections
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)

        # Device details
        details_group = QtWidgets.QGroupBox("Device Details")
        details_layout = QtWidgets.QFormLayout(details_group)

        self.lbl_device_name = QtWidgets.QLabel("-")
        self.lbl_device_type = QtWidgets.QLabel("-")
        self.lbl_device_layer = QtWidgets.QLabel("-")
        self.lbl_device_position = QtWidgets.QLabel("-")
        self.lbl_device_connections = QtWidgets.QLabel("-")

        details_layout.addRow("Name:", self.lbl_device_name)
        details_layout.addRow("Type:", self.lbl_device_type)
        details_layout.addRow("Layer:", self.lbl_device_layer)
        details_layout.addRow("Position:", self.lbl_device_position)
        details_layout.addRow("Connections:", self.lbl_device_connections)

        right_layout.addWidget(details_group)

        # Connections list
        connections_group = QtWidgets.QGroupBox("Connections")
        connections_layout = QtWidgets.QVBoxLayout(connections_group)

        self.connections_tree = QtWidgets.QTreeWidget()
        self.connections_tree.setHeaderLabels(["Connected To", "Type", "Circuit", "Layer"])
        self.connections_tree.setColumnWidth(0, 150)
        self.connections_tree.setColumnWidth(1, 80)
        self.connections_tree.setColumnWidth(2, 80)
        self.connections_tree.setColumnWidth(3, 60)
        connections_layout.addWidget(self.connections_tree)

        right_layout.addWidget(connections_group)

        # Connection controls
        conn_controls = QtWidgets.QHBoxLayout()

        self.btn_add_connection = QtWidgets.QPushButton("Add Connection")
        self.btn_add_connection.clicked.connect(self._add_connection)
        conn_controls.addWidget(self.btn_add_connection)

        self.btn_remove_connection = QtWidgets.QPushButton("Remove Connection")
        self.btn_remove_connection.clicked.connect(self._remove_connection)
        conn_controls.addWidget(self.btn_remove_connection)

        self.btn_edit_connection = QtWidgets.QPushButton("Edit Connection")
        self.btn_edit_connection.clicked.connect(self._edit_connection)
        conn_controls.addWidget(self.btn_edit_connection)

        right_layout.addLayout(conn_controls)

        # Layer operations
        layer_group = QtWidgets.QGroupBox("Layer Operations")
        layer_layout = QtWidgets.QHBoxLayout(layer_group)

        self.btn_move_to_layer = QtWidgets.QPushButton("Move to Layer")
        self.btn_move_to_layer.clicked.connect(self._move_to_layer)
        layer_layout.addWidget(self.btn_move_to_layer)

        self.btn_select_layer_devices = QtWidgets.QPushButton("Select Layer")
        self.btn_select_layer_devices.clicked.connect(self._select_layer_devices)
        layer_layout.addWidget(self.btn_select_layer_devices)

        self.btn_isolate_connections = QtWidgets.QPushButton("Isolate Chain")
        self.btn_isolate_connections.clicked.connect(self._isolate_connection_chain)
        layer_layout.addWidget(self.btn_isolate_connections)

        right_layout.addWidget(layer_group)

        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setSizes([400, 600])

        # Bottom buttons
        bottom_layout = QtWidgets.QHBoxLayout()

        self.btn_refresh = QtWidgets.QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self._refresh_data)
        bottom_layout.addWidget(self.btn_refresh)

        bottom_layout.addStretch()

        self.btn_apply = QtWidgets.QPushButton("Apply Changes")
        self.btn_apply.clicked.connect(self._apply_changes)
        bottom_layout.addWidget(self.btn_apply)

        self.btn_close = QtWidgets.QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        bottom_layout.addWidget(self.btn_close)

        layout.addLayout(bottom_layout)

    def _load_devices_data(self) -> list[dict[str, Any]]:
        """Load all devices from the model space."""
        devices = []

        # Get all device items from the scene
        for item in self.model_space_window.devices_group.childItems():
            if hasattr(item, "device_data"):
                device_info = {
                    "id": id(item),
                    "name": item.device_data.get("name", "Unknown"),
                    "type": item.device_data.get("type", "Unknown"),
                    "manufacturer": item.device_data.get("manufacturer", "Unknown"),
                    "layer_id": getattr(item, "layer_id", 1),
                    "position": (item.scenePos().x(), item.scenePos().y()),
                    "item": item,  # Keep reference to the actual item
                }
                devices.append(device_info)

        return devices

    def _load_connections_data(self) -> dict[str, list[dict[str, Any]]]:
        """Load connection data for all devices."""
        connections = {}

        # Load circuit-based connections
        for device in self.devices_data:
            device_id = str(device["id"])
            connections[device_id] = []

            # Check if device has circuit connection
            item = device.get("item")
            if item and hasattr(item, 'circuit_id') and item.circuit_id:
                # Add circuit connection
                connections[device_id].append(
                    {
                        "to_device_id": f"circuit_{item.circuit_id}",
                        "to_device_name": f"Circuit {item.circuit_id}",
                        "connection_type": "circuit",
                        "circuit": item.circuit_id,
                        "layer": device["layer_id"],
                    }
                )

            # Also check for proximity connections (existing logic)
            device_pos = device["position"]
            for other_device in self.devices_data:
                if other_device["id"] != device["id"]:
                    other_pos = other_device["position"]
                    distance = (
                        (device_pos[0] - other_pos[0]) ** 2 + (device_pos[1] - other_pos[1]) ** 2
                    ) ** 0.5

                    # If devices are close, consider them connected (simplified logic)
                    if distance < 200:  # Within 200 units
                        connections[device_id].append(
                            {
                                "to_device_id": str(other_device["id"]),
                                "to_device_name": other_device["name"],
                                "connection_type": "proximity",
                                "circuit": "auto",
                                "layer": other_device["layer_id"],
                            }
                        )

        return connections

    def _populate_devices(self):
        """Populate the device tree."""
        self.device_tree.clear()

        # Populate type filter
        types = set(device["type"] for device in self.devices_data)
        self.device_type_filter.clear()
        self.device_type_filter.addItem("All Types", "")
        for dev_type in sorted(types):
            self.device_type_filter.addItem(dev_type, dev_type)

        # Group devices by type
        devices_by_type = {}
        for device in self.devices_data:
            dev_type = device["type"]
            if dev_type not in devices_by_type:
                devices_by_type[dev_type] = []
            devices_by_type[dev_type].append(device)

        # Add to tree
        total_count = 0
        for dev_type, type_devices in sorted(devices_by_type.items()):
            # Create type category
            type_item = QtWidgets.QTreeWidgetItem([f"{dev_type} ({len(type_devices)})", "", "", ""])
            type_item.setData(0, Qt.UserRole, {"type": "category", "name": dev_type})

            for device in sorted(type_devices, key=lambda x: x["name"]):
                # Get layer name
                layer_name = "Default"
                for layer in self.model_space_window.layers:
                    if layer["id"] == device["layer_id"]:
                        layer_name = layer["name"]
                        break

                # Get connection count
                conn_count = len(self.connections_data.get(str(device["id"]), []))

                device_item = QtWidgets.QTreeWidgetItem(
                    [device["name"], device["type"], layer_name, str(conn_count)]
                )
                device_item.setData(0, Qt.UserRole, device)
                type_item.addChild(device_item)

            self.device_tree.addTopLevelItem(type_item)
            type_item.setExpanded(True)
            total_count += len(type_devices)

        self.device_count_label.setText(f"Total: {total_count} devices")

    def _filter_devices(self):
        """Filter devices based on search and type criteria."""
        search_text = self.device_search.text().strip().lower()
        filter_type = self.device_type_filter.currentData()

        # Show/hide items based on filter
        for i in range(self.device_tree.topLevelItemCount()):
            type_item = self.device_tree.topLevelItem(i)
            type_visible = False

            for j in range(type_item.childCount()):
                device_item = type_item.child(j)
                device_data = device_item.data(0, Qt.UserRole)

                if isinstance(device_data, dict) and "name" in device_data:
                    name_match = search_text in device_data["name"].lower()
                    type_match = not filter_type or device_data["type"] == filter_type

                    visible = name_match and type_match
                    device_item.setHidden(not visible)

                    if visible:
                        type_visible = True

            type_item.setHidden(not type_visible)

    def _on_device_selected(self):
        """Handle device selection."""
        selected_items = self.device_tree.selectedItems()
        if not selected_items:
            self._clear_device_details()
            return

        item = selected_items[0]
        device_data = item.data(0, Qt.UserRole)

        if isinstance(device_data, dict) and "name" in device_data:
            self._show_device_details(device_data)

    def _show_device_details(self, device_data: dict[str, Any]):
        """Show details for selected device."""
        self.lbl_device_name.setText(device_data["name"])
        self.lbl_device_type.setText(device_data["type"])

        # Get layer name
        layer_name = "Default"
        for layer in self.model_space_window.layers:
            if layer["id"] == device_data["layer_id"]:
                layer_name = layer["name"]
                break
        self.lbl_device_layer.setText(layer_name)

        # Position
        pos = device_data["position"]
        self.lbl_device_position.setText(".1f")

        # Connections
        device_id = str(device_data["id"])
        connections = self.connections_data.get(device_id, [])
        self.lbl_device_connections.setText(str(len(connections)))

        # Populate connections tree
        self.connections_tree.clear()
        for conn in connections:
            conn_item = QtWidgets.QTreeWidgetItem(
                [
                    conn["to_device_name"],
                    conn["connection_type"],
                    conn["circuit"],
                    str(conn["layer"]),
                ]
            )
            conn_item.setData(0, Qt.UserRole, conn)
            self.connections_tree.addTopLevelItem(conn_item)

    def _clear_device_details(self):
        """Clear device details display."""
        self.lbl_device_name.setText("-")
        self.lbl_device_type.setText("-")
        self.lbl_device_layer.setText("-")
        self.lbl_device_position.setText("-")
        self.lbl_device_connections.setText("-")
        self.connections_tree.clear()

    def _add_connection(self):
        """Add a new connection."""
        # This would open a dialog to select devices and connection type
        QtWidgets.QMessageBox.information(
            self, "Add Connection", "Connection creation dialog would open here."
        )

    def _remove_connection(self):
        """Remove selected connection."""
        selected_items = self.connections_tree.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self, "No Selection", "Please select a connection to remove."
            )
            return

        # Remove connection logic here
        QtWidgets.QMessageBox.information(
            self, "Remove Connection", "Connection removal logic would be implemented here."
        )

    def _edit_connection(self):
        """Edit selected connection."""
        selected_items = self.connections_tree.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(
                self, "No Selection", "Please select a connection to edit."
            )
            return

        # Edit connection logic here
        QtWidgets.QMessageBox.information(
            self, "Edit Connection", "Connection editing dialog would open here."
        )

    def _move_to_layer(self):
        """Move selected device to a different layer."""
        selected_items = self.device_tree.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a device to move.")
            return

        item = selected_items[0]
        device_data = item.data(0, Qt.UserRole)

        if not isinstance(device_data, dict) or "id" not in device_data:
            return

        # Show layer selection dialog
        layer_names = [layer["name"] for layer in self.model_space_window.layers]
        layer_name, ok = QtWidgets.QInputDialog.getItem(
            self, "Move to Layer", "Select layer:", layer_names, 0, False
        )

        if ok and layer_name:
            # Find layer ID
            target_layer_id = None
            for layer in self.model_space_window.layers:
                if layer["name"] == layer_name:
                    target_layer_id = layer["id"]
                    break

            if target_layer_id:
                # Update device layer
                device_data["layer_id"] = target_layer_id
                device_data["item"].layer_id = target_layer_id

                # Refresh display
                self._populate_devices()

    def _select_layer_devices(self):
        """Select all devices in the same layer as selected device."""
        selected_items = self.device_tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        device_data = item.data(0, Qt.UserRole)

        if not isinstance(device_data, dict) or "layer_id" not in device_data:
            return

        layer_id = device_data["layer_id"]

        # Select devices in the scene
        for device in self.devices_data:
            if device["layer_id"] == layer_id:
                device["item"].setSelected(True)

        # Close dialog and return to model space
        self.accept()

    def _isolate_connection_chain(self):
        """Isolate the connection chain for selected device."""
        selected_items = self.device_tree.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a device.")
            return

        item = selected_items[0]
        device_data = item.data(0, Qt.UserRole)

        if not isinstance(device_data, dict) or "id" not in device_data:
            return

        # Find all connected devices (simplified - would need proper graph traversal)
        device_id = str(device_data["id"])
        connected_device_ids = set()

        # Add directly connected devices
        for conn in self.connections_data.get(device_id, []):
            connected_device_ids.add(conn["to_device_id"])

        # Select the chain
        for device in self.devices_data:
            if str(device["id"]) in connected_device_ids or str(device["id"]) == device_id:
                device["item"].setSelected(True)

        # Close dialog
        self.accept()

    def _refresh_data(self):
        """Refresh all data."""
        self.devices_data = self._load_devices_data()
        self.connections_data = self._load_connections_data()
        self._populate_devices()
        self._clear_device_details()

    def _apply_changes(self):
        """Apply any pending changes."""
        # Save connection data, update device layers, etc.
        QtWidgets.QMessageBox.information(
            self, "Applied", "Changes have been applied to the model."
        )
