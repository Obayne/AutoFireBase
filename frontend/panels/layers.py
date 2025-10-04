"""
Layers Panel - Advanced layer management for CAD workspace
"""

from PySide6 import QtCore, QtGui, QtWidgets


class LayerItem:
    """Represents a CAD layer with properties."""

    def __init__(
        self, id: int, name: str, visible: bool = True, locked: bool = False, color: str = "#000000"
    ):
        self.id = id
        self.name = name
        self.visible = visible
        self.locked = locked
        self.color = color
        self.opacity = 1.0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "visible": self.visible,
            "locked": self.locked,
            "color": self.color,
            "opacity": self.opacity,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LayerItem":
        """Create from dictionary."""
        return cls(
            data["id"],
            data["name"],
            data.get("visible", True),
            data.get("locked", False),
            data.get("color", "#000000"),
        )


class LayersPanel(QtWidgets.QDockWidget):
    """Dockable layers management panel."""

    layer_changed = QtCore.Signal(int, str, object)  # layer_id, property_name, value
    layer_selected = QtCore.Signal(int)  # layer_id

    def __init__(self, parent=None):
        super().__init__("Layers", parent)
        self.layers: dict[int, LayerItem] = {}
        self.active_layer_id: int | None = None

        self.setup_ui()
        self.create_default_layers()

    def setup_ui(self):
        """Setup the user interface."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()

        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.clicked.connect(self.add_layer)
        toolbar.addWidget(self.add_button)

        self.remove_button = QtWidgets.QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_layer)
        toolbar.addWidget(self.remove_button)

        self.rename_button = QtWidgets.QPushButton("Rename")
        self.rename_button.clicked.connect(self.rename_layer)
        toolbar.addWidget(self.rename_button)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Layers tree
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Layer", "Visible", "Locked"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setSelectionMode(QtWidgets.QTreeWidget.SelectionMode.SingleSelection)
        self.tree.itemChanged.connect(self.on_item_changed)
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)

        # Set column widths
        self.tree.setColumnWidth(0, 120)
        self.tree.setColumnWidth(1, 60)
        self.tree.setColumnWidth(2, 60)

        layout.addWidget(self.tree)

        # Layer properties
        props_group = QtWidgets.QGroupBox("Properties")
        props_layout = QtWidgets.QVBoxLayout(props_group)

        # Color picker
        color_layout = QtWidgets.QHBoxLayout()
        color_layout.addWidget(QtWidgets.QLabel("Color:"))
        self.color_button = QtWidgets.QPushButton()
        self.color_button.setFixedSize(24, 24)
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        props_layout.addLayout(color_layout)

        # Opacity slider
        opacity_layout = QtWidgets.QHBoxLayout()
        opacity_layout.addWidget(QtWidgets.QLabel("Opacity:"))
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QtWidgets.QLabel("100%")
        opacity_layout.addWidget(self.opacity_label)
        props_layout.addLayout(opacity_layout)

        layout.addWidget(props_group)

        self.setWidget(widget)
        self.setMinimumWidth(250)

    def create_default_layers(self):
        """Create default layers."""
        self.add_layer_item(LayerItem(1, "Devices", True, False, "#FF6B6B"))
        self.add_layer_item(LayerItem(2, "Wiring", True, False, "#4ECDC4"))
        self.add_layer_item(LayerItem(3, "Annotations", True, False, "#45B7D1"))
        self.add_layer_item(LayerItem(4, "Background", True, True, "#95A5A6"))

        # Set default active layer
        self.set_active_layer(1)

    def add_layer_item(self, layer: LayerItem):
        """Add a layer item to the tree."""
        self.layers[layer.id] = layer

        item = QtWidgets.QTreeWidgetItem(self.tree)
        item.setData(0, QtCore.Qt.ItemDataRole.UserRole, layer.id)

        # Name column
        item.setText(0, layer.name)
        item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)

        # Visible column (checkbox)
        item.setCheckState(
            1, QtCore.Qt.CheckState.Checked if layer.visible else QtCore.Qt.CheckState.Unchecked
        )

        # Locked column (checkbox)
        item.setCheckState(
            2, QtCore.Qt.CheckState.Checked if layer.locked else QtCore.Qt.CheckState.Unchecked
        )

        # Set color indicator
        self.update_item_color(item, layer.color)

    def update_item_color(self, item: QtWidgets.QTreeWidgetItem, color: str):
        """Update the color indicator for a tree item."""
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtGui.QColor(color))
        item.setIcon(0, QtGui.QIcon(pixmap))

    def add_layer(self):
        """Add a new layer."""
        name, ok = QtWidgets.QInputDialog.getText(
            self, "Add Layer", "Layer name:", text=f"Layer {len(self.layers) + 1}"
        )
        if ok and name:
            layer_id = max(self.layers.keys()) + 1 if self.layers else 1
            layer = LayerItem(layer_id, name, True, False, "#000000")
            self.add_layer_item(layer)

    def remove_layer(self):
        """Remove the selected layer."""
        current = self.tree.currentItem()
        if current:
            layer_id = current.data(0, QtCore.Qt.ItemDataRole.UserRole)
            if layer_id in self.layers:
                # Don't allow removing the last layer
                if len(self.layers) <= 1:
                    QtWidgets.QMessageBox.warning(
                        self, "Cannot Remove", "Cannot remove the last layer."
                    )
                    return

                # Confirm deletion
                reply = QtWidgets.QMessageBox.question(
                    self,
                    "Remove Layer",
                    f"Remove layer '{self.layers[layer_id].name}'?",
                    QtWidgets.QMessageBox.StandardButton.Yes
                    | QtWidgets.QMessageBox.StandardButton.No,
                )

                if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                    del self.layers[layer_id]
                    self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(current))

                    # Set a new active layer if we removed the active one
                    if self.active_layer_id == layer_id:
                        remaining_ids = list(self.layers.keys())
                        if remaining_ids:
                            self.set_active_layer(remaining_ids[0])

    def rename_layer(self):
        """Rename the selected layer."""
        current = self.tree.currentItem()
        if current:
            self.tree.editItem(current, 0)

    def set_active_layer(self, layer_id: int):
        """Set the active layer."""
        if layer_id in self.layers:
            self.active_layer_id = layer_id

            # Update UI to show active layer
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)
                if item:  # Type guard for linter
                    item_layer_id = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
                    font = item.font(0)
                    font.setBold(item_layer_id == layer_id)
                    item.setFont(0, font)

            self.layer_selected.emit(layer_id)

    def get_active_layer(self) -> LayerItem | None:
        """Get the currently active layer."""
        return self.layers.get(self.active_layer_id) if self.active_layer_id else None

    def on_item_changed(self, item: QtWidgets.QTreeWidgetItem, column: int):
        """Handle item changes."""
        layer_id = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if layer_id not in self.layers:
            return

        layer = self.layers[layer_id]

        if column == 0:  # Name changed
            new_name = item.text(0)
            if new_name and new_name != layer.name:
                layer.name = new_name
                self.layer_changed.emit(layer_id, "name", new_name)

        elif column == 1:  # Visibility changed
            visible = item.checkState(1) == QtCore.Qt.CheckState.Checked
            layer.visible = visible
            self.layer_changed.emit(layer_id, "visible", visible)

        elif column == 2:  # Locked changed
            locked = item.checkState(2) == QtCore.Qt.CheckState.Checked
            layer.locked = locked
            self.layer_changed.emit(layer_id, "locked", locked)

    def on_selection_changed(self):
        """Handle selection changes."""
        current = self.tree.currentItem()
        if current:
            layer_id = current.data(0, QtCore.Qt.ItemDataRole.UserRole)
            self.set_active_layer(layer_id)

            # Update properties panel
            layer = self.layers.get(layer_id)
            if layer:
                self.update_properties_panel(layer)

    def update_properties_panel(self, layer: LayerItem):
        """Update the properties panel for the selected layer."""
        # Update color button
        pixmap = QtGui.QPixmap(20, 20)
        pixmap.fill(QtGui.QColor(layer.color))
        self.color_button.setIcon(QtGui.QIcon(pixmap))

        # Update opacity slider
        opacity_percent = int(layer.opacity * 100)
        self.opacity_slider.setValue(opacity_percent)
        self.opacity_label.setText(f"{opacity_percent}%")

    def choose_color(self):
        """Choose a color for the current layer."""
        current = self.tree.currentItem()
        if current:
            layer_id = current.data(0, QtCore.Qt.ItemDataRole.UserRole)
            layer = self.layers.get(layer_id)
            if layer:
                color = QtWidgets.QColorDialog.getColor(
                    QtGui.QColor(layer.color), self, "Choose Layer Color"
                )
                if color.isValid():
                    layer.color = color.name()
                    self.update_item_color(current, layer.color)
                    self.update_properties_panel(layer)
                    self.layer_changed.emit(layer_id, "color", layer.color)

    def on_opacity_changed(self, value: int):
        """Handle opacity slider changes."""
        current = self.tree.currentItem()
        if current:
            layer_id = current.data(0, QtCore.Qt.ItemDataRole.UserRole)
            layer = self.layers.get(layer_id)
            if layer:
                layer.opacity = value / 100.0
                self.opacity_label.setText(f"{value}%")
                self.layer_changed.emit(layer_id, "opacity", layer.opacity)

    def get_layers_data(self) -> list[dict]:
        """Get layers data for serialization."""
        return [layer.to_dict() for layer in self.layers.values()]

    def load_layers_data(self, data: list[dict]):
        """Load layers data from serialization."""
        # Clear existing layers
        self.layers.clear()
        self.tree.clear()

        # Load new layers
        for layer_data in data:
            layer = LayerItem.from_dict(layer_data)
            self.add_layer_item(layer)

        # Set active layer (first one if none specified)
        if self.layers:
            active_id = data[0]["id"] if data else list(self.layers.keys())[0]
            self.set_active_layer(active_id)
