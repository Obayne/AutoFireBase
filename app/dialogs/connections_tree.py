from PySide6 import QtWidgets, QtCore

class ConnectionsTree(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Connections", parent)
        self.setAllowedAreas(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea | QtCore.Qt.DockWidgetArea.RightDockWidgetArea)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Item", "Details", "Circuit Type"])
        self.tree.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_context_menu)
        self.setWidget(self.tree)

        self.add_panel("FACP-1") # Example

    def add_panel(self, panel_name, panel_device_item=None, circuit_type="N/A"):
        panel_item = QtWidgets.QTreeWidgetItem(self.tree, [panel_name, "Fire Alarm Control Panel", circuit_type])
        panel_item.setExpanded(True)
        if panel_device_item:
            panel_item.setData(0, QtCore.Qt.UserRole, panel_device_item.id) # Store device ID
            panel_item.setData(1, QtCore.Qt.UserRole, panel_device_item) # Store device reference

    def add_device_to_panel(self, panel_name, device_name, device_details, device_item=None):
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.text(0) == panel_name:
                device_tree_item = QtWidgets.QTreeWidgetItem(item, [device_name, device_details])
                if device_item:
                    device_tree_item.setData(0, QtCore.Qt.UserRole, device_item.id) # Store device ID
                    device_tree_item.setData(1, QtCore.Qt.UserRole, device_item) # Store device reference
                return

    def open_context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return

        item = self.tree.itemFromIndex(index)
        device_item = item.data(1, QtCore.Qt.UserRole) # Get the stored DeviceItem reference

        menu = QtWidgets.QMenu(self)

        if device_item:
            go_to_action = menu.addAction("Go to Device")
            select_action = menu.addAction("Select Device")
            view_props_action = menu.addAction("View Properties")
        elif item.parent() is None: # It's a panel item
            edit_circuit_action = menu.addAction("Edit Circuit Properties")

        action = menu.exec(self.tree.viewport().mapToGlobal(position))

        if device_item:
            if action == go_to_action:
                self.parent.view.centerOn(device_item) # Center the view on the device
            elif action == select_action:
                self.parent.view.scene().clearSelection()
                device_item.setSelected(True)
            elif action == view_props_action:
                # Assuming parent (MainWindow) has a way to show properties of a selected item
                self.parent.show_properties_for_item(device_item)
        elif item.parent() is None: # It's a panel item
            if action == edit_circuit_action:
                panel_device_item = item.data(1, QtCore.Qt.UserRole) # Get the stored DeviceItem reference
                circuit_data = {
                    "circuit_type": item.text(2), # Get circuit type from the tree item
                    "capacity": 0, # Placeholder
                    "cable_length": 0.0 # Placeholder
                }
                dialog = CircuitPropertiesDialog(self.parent, circuit_data, panel_device_item.id)
                if dialog.exec() == QtWidgets.QDialog.Accepted:
                    updated_data = dialog.get_circuit_properties()
                    print(f"Updated circuit properties: {updated_data}") # For debugging

    def get_connections(self):
        connections = []
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            panel_item = root.child(i)
            panel_device_id = panel_item.data(0, QtCore.Qt.UserRole)
            
            devices_in_panel = []
            for j in range(panel_item.childCount()):
                device_item = panel_item.child(j)
                device_id = device_item.data(0, QtCore.Qt.UserRole)
                devices_in_panel.append({"id": device_id, "name": device_item.text(0), "details": device_item.text(1)})
            
            connections.append({"panel_id": panel_device_id, "panel_name": panel_item.text(0), "devices": devices_in_panel})
        return connections

    def load_connections(self, connections, device_map): # device_map is now required
        self.tree.clear()
        for conn in connections:
            panel_device_item = device_map.get(conn['panel_id'])
            
            # Fetch circuit data from DB
            circuit_data = None
            if panel_device_item:
                try:
                    con = db_loader.connect()
                    circuit_data = db_loader.fetch_circuit(con, panel_device_item.id)
                    con.close()
                except Exception as e:
                    print(f"Error fetching circuit data for panel {panel_device_item.id}: {e}")

            circuit_type = circuit_data['circuit_type'] if circuit_data else "N/A"
            self.add_panel(conn['panel_name'], panel_device_item, circuit_type)
            for dev_data in conn['devices']:
                device_item = device_map.get(dev_data['id'])
                self.add_device_to_panel(conn['panel_name'], dev_data['name'], dev_data['details'], device_item)

    def remove_panel(self):
        """Remove the selected panel from the list."""
        selected_item = self.panel_list.currentItem()
        if selected_item:
            row = self.panel_list.row(selected_item)
            self.panel_list.takeItem(row)
            del self.panels[row]

    def remove_device(self, device_item):
        """Remove a device from the connections tree."""
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            panel_item = root.child(i)
            for j in range(panel_item.childCount()):
                tree_device_item = panel_item.child(j)
                if tree_device_item.data(1, QtCore.Qt.UserRole) == device_item:
                    panel_item.removeChild(tree_device_item)
                    return
