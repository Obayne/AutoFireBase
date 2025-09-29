"""
Layer Manager Dialog - Manage CAD layers with advanced features
"""

from typing import Any

from PySide6 import QtWidgets
from PySide6.QtCore import Qt


class LayerManagerDialog(QtWidgets.QDialog):
    """Advanced layer manager with flatten, merge, and organization features."""

    def __init__(self, model_space_window, parent=None):
        super().__init__(parent)
        self.model_space_window = model_space_window
        self.layers_data = self._load_layers_data()

        self.setWindowTitle("Layer Manager")
        self.setModal(True)
        self.resize(600, 500)

        self._setup_ui()
        self._populate_layers()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Layer list
        layer_group = QtWidgets.QGroupBox("Layers")
        layer_layout = QtWidgets.QVBoxLayout(layer_group)

        # Layer tree
        self.layer_tree = QtWidgets.QTreeWidget()
        self.layer_tree.setHeaderLabels(["Layer", "Visible", "Locked", "Objects"])
        self.layer_tree.setColumnWidth(0, 200)
        self.layer_tree.setColumnWidth(1, 60)
        self.layer_tree.setColumnWidth(2, 60)
        self.layer_tree.setColumnWidth(3, 80)
        self.layer_tree.itemChanged.connect(self._on_layer_changed)
        layer_layout.addWidget(self.layer_tree)

        layout.addWidget(layer_group)

        # Control buttons
        controls_layout = QtWidgets.QHBoxLayout()

        self.btn_new_layer = QtWidgets.QPushButton("New Layer")
        self.btn_new_layer.clicked.connect(self._new_layer)
        controls_layout.addWidget(self.btn_new_layer)

        self.btn_delete_layer = QtWidgets.QPushButton("Delete")
        self.btn_delete_layer.clicked.connect(self._delete_layer)
        controls_layout.addWidget(self.btn_delete_layer)

        self.btn_rename_layer = QtWidgets.QPushButton("Rename")
        self.btn_rename_layer.clicked.connect(self._rename_layer)
        controls_layout.addWidget(self.btn_rename_layer)

        controls_layout.addStretch()

        self.btn_flatten_all = QtWidgets.QPushButton("Flatten All")
        self.btn_flatten_all.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """
        )
        self.btn_flatten_all.clicked.connect(self._flatten_all_layers)
        controls_layout.addWidget(self.btn_flatten_all)

        layout.addLayout(controls_layout)

        # Advanced operations
        advanced_group = QtWidgets.QGroupBox("Advanced Operations")
        advanced_layout = QtWidgets.QHBoxLayout(advanced_group)

        self.btn_merge_visible = QtWidgets.QPushButton("Merge Visible")
        self.btn_merge_visible.clicked.connect(self._merge_visible_layers)
        advanced_layout.addWidget(self.btn_merge_visible)

        self.btn_duplicate_layer = QtWidgets.QPushButton("Duplicate")
        self.btn_duplicate_layer.clicked.connect(self._duplicate_layer)
        advanced_layout.addWidget(self.btn_duplicate_layer)

        self.btn_isolate_layer = QtWidgets.QPushButton("Isolate")
        self.btn_isolate_layer.clicked.connect(self._isolate_layer)
        advanced_layout.addWidget(self.btn_isolate_layer)

        self.btn_show_all = QtWidgets.QPushButton("Show All")
        self.btn_show_all.clicked.connect(self._show_all_layers)
        advanced_layout.addWidget(self.btn_show_all)

        layout.addWidget(advanced_group)

        # Bottom buttons
        bottom_layout = QtWidgets.QHBoxLayout()

        self.btn_apply = QtWidgets.QPushButton("Apply")
        self.btn_apply.clicked.connect(self._apply_changes)
        bottom_layout.addWidget(self.btn_apply)

        bottom_layout.addStretch()

        self.btn_close = QtWidgets.QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        bottom_layout.addWidget(self.btn_close)

        layout.addLayout(bottom_layout)

    def _load_layers_data(self) -> dict[str, Any]:
        """Load current layers data from model space."""
        layers = {}

        # Get current layers from model space
        for layer_info in self.model_space_window.layers:
            layer_id = layer_info["id"]
            layer_name = layer_info["name"]

            # Count objects in this layer
            object_count = self._count_objects_in_layer(layer_id)

            layers[layer_id] = {
                "name": layer_name,
                "visible": layer_info.get("visible", True),
                "locked": layer_info.get("locked", False),
                "objects": object_count,
            }

        return layers

    def _count_objects_in_layer(self, layer_id: int) -> int:
        """Count objects in a specific layer."""
        count = 0

        # Count devices in this layer
        for item in self.model_space_window.devices_group.childItems():
            if hasattr(item, "layer_id") and item.layer_id == layer_id:
                count += 1

        # Count wires in this layer
        for item in self.model_space_window.layer_wires.childItems():
            if hasattr(item, "layer_id") and item.layer_id == layer_id:
                count += 1

        # Count other objects
        for item in self.model_space_window.layer_sketch.childItems():
            if hasattr(item, "layer_id") and item.layer_id == layer_id:
                count += 1

        return count

    def _populate_layers(self):
        """Populate the layer tree with current layers."""
        self.layer_tree.clear()

        for layer_id, layer_data in self.layers_data.items():
            item = QtWidgets.QTreeWidgetItem()

            # Layer name
            item.setText(0, layer_data["name"])
            item.setData(0, Qt.UserRole, layer_id)

            # Visible checkbox
            visible_cb = QtWidgets.QCheckBox()
            visible_cb.setChecked(layer_data["visible"])
            visible_cb.stateChanged.connect(
                lambda state, lid=layer_id: self._toggle_layer_visibility(lid, state)
            )
            self.layer_tree.setItemWidget(item, 1, visible_cb)

            # Locked checkbox
            locked_cb = QtWidgets.QCheckBox()
            locked_cb.setChecked(layer_data["locked"])
            locked_cb.stateChanged.connect(
                lambda state, lid=layer_id: self._toggle_layer_lock(lid, state)
            )
            self.layer_tree.setItemWidget(item, 2, locked_cb)

            # Object count
            item.setText(3, str(layer_data["objects"]))

            self.layer_tree.addTopLevelItem(item)

    def _on_layer_changed(self, item, column):
        """Handle layer item changes."""
        if column == 0:  # Name changed
            layer_id = item.data(0, Qt.UserRole)
            new_name = item.text(0)
            if layer_id in self.layers_data:
                self.layers_data[layer_id]["name"] = new_name

    def _toggle_layer_visibility(self, layer_id: int, visible: bool):
        """Toggle layer visibility."""
        if layer_id in self.layers_data:
            self.layers_data[layer_id]["visible"] = visible

    def _toggle_layer_lock(self, layer_id: int, locked: bool):
        """Toggle layer lock."""
        if layer_id in self.layers_data:
            self.layers_data[layer_id]["locked"] = locked

    def _new_layer(self):
        """Create a new layer."""
        name, ok = QtWidgets.QInputDialog.getText(self, "New Layer", "Layer name:")
        if ok and name:
            # Find next available ID
            max_id = max(self.layers_data.keys()) if self.layers_data else 0
            new_id = max_id + 1

            self.layers_data[new_id] = {
                "name": name,
                "visible": True,
                "locked": False,
                "objects": 0,
            }

            self._populate_layers()

    def _delete_layer(self):
        """Delete selected layer."""
        current_item = self.layer_tree.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a layer to delete.")
            return

        layer_id = current_item.data(0, Qt.UserRole)
        layer_name = self.layers_data[layer_id]["name"]

        # Don't allow deleting the default layer
        if layer_id == 1:
            QtWidgets.QMessageBox.warning(self, "Cannot Delete", "Cannot delete the default layer.")
            return

        # Check if layer has objects
        if self.layers_data[layer_id]["objects"] > 0:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Confirm Delete",
                f"Layer '{layer_name}' contains {self.layers_data[layer_id]['objects']} objects. Delete anyway?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            )
            if reply != QtWidgets.QMessageBox.Yes:
                return

        del self.layers_data[layer_id]
        self._populate_layers()

    def _rename_layer(self):
        """Rename selected layer."""
        current_item = self.layer_tree.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a layer to rename.")
            return

        layer_id = current_item.data(0, Qt.UserRole)
        current_name = self.layers_data[layer_id]["name"]

        name, ok = QtWidgets.QInputDialog.getText(
            self, "Rename Layer", "New name:", text=current_name
        )
        if ok and name and name != current_name:
            self.layers_data[layer_id]["name"] = name
            self._populate_layers()

    def _flatten_all_layers(self):
        """Flatten all layers into the default layer."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Flatten",
            "This will move all objects from other layers into the default layer. Continue?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )

        if reply == QtWidgets.QMessageBox.Yes:
            # Move all objects to default layer
            self._move_all_objects_to_layer(1)

            # Update layer data
            for layer_id in list(self.layers_data.keys()):
                if layer_id != 1:
                    self.layers_data[1]["objects"] += self.layers_data[layer_id]["objects"]
                    del self.layers_data[layer_id]

            self._populate_layers()
            QtWidgets.QMessageBox.information(
                self, "Success", "All layers have been flattened into the default layer."
            )

    def _merge_visible_layers(self):
        """Merge all visible layers into the active layer."""
        # Find active layer (first visible layer)
        active_layer = None
        layers_to_merge = []

        for layer_id, layer_data in self.layers_data.items():
            if layer_data["visible"]:
                if active_layer is None:
                    active_layer = layer_id
                else:
                    layers_to_merge.append(layer_id)

        if not active_layer or not layers_to_merge:
            QtWidgets.QMessageBox.information(
                self, "No Operation", "Need at least 2 visible layers to merge."
            )
            return

        # Move objects from other visible layers to active layer
        for layer_id in layers_to_merge:
            self._move_objects_to_layer(layer_id, active_layer)
            self.layers_data[active_layer]["objects"] += self.layers_data[layer_id]["objects"]
            del self.layers_data[layer_id]

        self._populate_layers()
        QtWidgets.QMessageBox.information(
            self,
            "Success",
            f"Merged {len(layers_to_merge)} layers into '{self.layers_data[active_layer]['name']}'.",
        )

    def _duplicate_layer(self):
        """Duplicate selected layer."""
        current_item = self.layer_tree.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(
                self, "No Selection", "Please select a layer to duplicate."
            )
            return

        layer_id = current_item.data(0, Qt.UserRole)
        original_data = self.layers_data[layer_id]

        name, ok = QtWidgets.QInputDialog.getText(
            self, "Duplicate Layer", "New layer name:", text=f"{original_data['name']} Copy"
        )
        if ok and name:
            max_id = max(self.layers_data.keys())
            new_id = max_id + 1

            self.layers_data[new_id] = {
                "name": name,
                "visible": original_data["visible"],
                "locked": False,  # Don't lock duplicates
                "objects": 0,  # Start empty
            }

            self._populate_layers()

    def _isolate_layer(self):
        """Hide all layers except selected."""
        current_item = self.layer_tree.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a layer to isolate.")
            return

        layer_id = current_item.data(0, Qt.UserRole)

        for lid, layer_data in self.layers_data.items():
            layer_data["visible"] = lid == layer_id

        self._populate_layers()

    def _show_all_layers(self):
        """Show all layers."""
        for layer_data in self.layers_data.values():
            layer_data["visible"] = True

        self._populate_layers()

    def _move_all_objects_to_layer(self, target_layer_id: int):
        """Move all objects to target layer."""
        # Move devices
        for item in self.model_space_window.devices_group.childItems():
            if hasattr(item, "layer_id"):
                item.layer_id = target_layer_id

        # Move wires
        for item in self.model_space_window.layer_wires.childItems():
            if hasattr(item, "layer_id"):
                item.layer_id = target_layer_id

        # Move sketch objects
        for item in self.model_space_window.layer_sketch.childItems():
            if hasattr(item, "layer_id"):
                item.layer_id = target_layer_id

    def _move_objects_to_layer(self, from_layer_id: int, to_layer_id: int):
        """Move objects from one layer to another."""
        # Move devices
        for item in self.model_space_window.devices_group.childItems():
            if hasattr(item, "layer_id") and item.layer_id == from_layer_id:
                item.layer_id = to_layer_id

        # Move wires
        for item in self.model_space_window.layer_wires.childItems():
            if hasattr(item, "layer_id") and item.layer_id == from_layer_id:
                item.layer_id = to_layer_id

        # Move sketch objects
        for item in self.model_space_window.layer_sketch.childItems():
            if hasattr(item, "layer_id") and item.layer_id == from_layer_id:
                item.layer_id = to_layer_id

    def _apply_changes(self):
        """Apply layer changes to the model space."""
        # Update model space layers
        self.model_space_window.layers = []
        for layer_id, layer_data in self.layers_data.items():
            self.model_space_window.layers.append(
                {
                    "id": layer_id,
                    "name": layer_data["name"],
                    "visible": layer_data["visible"],
                    "locked": layer_data["locked"],
                }
            )

        # Update layer visibility in scene
        self._update_layer_visibility()

        QtWidgets.QMessageBox.information(
            self, "Applied", "Layer changes have been applied to the model."
        )

    def _update_layer_visibility(self):
        """Update visibility of objects based on layer settings."""
        for layer_info in self.model_space_window.layers:
            layer_id = layer_info["id"]
            visible = layer_info["visible"]

            # Update devices
            for item in self.model_space_window.devices_group.childItems():
                if hasattr(item, "layer_id") and item.layer_id == layer_id:
                    item.setVisible(visible)

            # Update wires
            for item in self.model_space_window.layer_wires.childItems():
                if hasattr(item, "layer_id") and item.layer_id == layer_id:
                    item.setVisible(visible)

            # Update sketch objects
            for item in self.model_space_window.layer_sketch.childItems():
                if hasattr(item, "layer_id") and item.layer_id == layer_id:
                    item.setVisible(visible)
