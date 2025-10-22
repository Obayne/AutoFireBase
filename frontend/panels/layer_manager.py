"""
AutoFire Layer Management System
Manages layers with visibility, locking, colors, and presets.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class Layer:
    """Represents a single layer."""

    def __init__(
        self,
        id: int,
        name: str,
        visible: bool = True,
        locked: bool = False,
        color: QColor = QColor(Qt.GlobalColor.blue),
        layer_type: str = "custom",
    ):
        self.id = id
        self.name = name
        self.visible = visible
        self.locked = locked
        self.color = color
        self.type = layer_type  # "architectural", "devices", "wiring", "coverage", etc.

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "visible": self.visible,
            "locked": self.locked,
            "color": self.color.name(),
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Layer:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            visible=data.get("visible", True),
            locked=data.get("locked", False),
            color=QColor(data.get("color", "#0000ff")),
            layer_type=data.get("type", "custom"),
        )


class LayerManager(QWidget):
    """Widget for managing layers with presets and controls."""

    # Signals
    layer_changed = Signal(int, str, object)  # layer_id, property_name, value
    layer_selected = Signal(int)  # layer_id
    preset_applied = Signal(str)  # preset_name

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layers: dict[int, Layer] = {}
        self.current_preset = "Designer"

        self._setup_ui()
        self._initialize_default_layers()
        self._apply_preset(self.current_preset)

    def _setup_ui(self) -> None:
        """Set up the layer manager UI."""
        # Apply clean dark theme styling
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 11px;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #2d2d30;
                color: #ffffff;
                min-width: 80px;
            }
            QComboBox:focus {
                border-color: #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 16px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 3px solid #ffffff;
                margin-right: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d30;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
            }
            QTableWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                gridline-color: #404040;
                selection-background-color: #0078d4;
                alternate-background-color: #252526;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #333333;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: #404040;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #555555;
                font-weight: bold;
                font-size: 11px;
            }
            QCheckBox {
                spacing: 5px;
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #555555;
                border-radius: 2px;
                background-color: #2d2d30;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
                image: url(
                    "data:image/svg+xml;base64,"
                    + "PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0i"
                    + "bm9uZSIg"
                    + "eG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNCA5"
                    + "IDIgNyA0IDUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGlu"
                    + "ZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+"
                    + ")"
                ;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 6px 12px;
                border-radius: 3px;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Preset selector - cleaner
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(8)

        preset_label = QLabel("Preset:")
        preset_label.setStyleSheet("color: #cccccc; font-weight: normal;")
        preset_layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Designer", "AHJ", "Installer"])
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(self.preset_combo)

        preset_layout.addStretch()
        layout.addLayout(preset_layout)

        # Layer table - improved styling
        self.layer_table = QTableWidget()
        self.layer_table.setColumnCount(5)
        self.layer_table.setHorizontalHeaderLabels(["Name", "Visible", "Locked", "Color", "Type"])
        self.layer_table.horizontalHeader().setStretchLastSection(True)
        self.layer_table.setAlternatingRowColors(True)
        self.layer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layer_table.setMinimumHeight(300)
        self.layer_table.itemSelectionChanged.connect(self._on_layer_selected)

        # Set column widths
        self.layer_table.setColumnWidth(0, 120)  # Name
        self.layer_table.setColumnWidth(1, 60)  # Visible
        self.layer_table.setColumnWidth(2, 60)  # Locked
        self.layer_table.setColumnWidth(3, 60)  # Color
        # Type column stretches

        layout.addWidget(self.layer_table)

        # Control buttons - cleaner layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.add_button = QPushButton("Add Layer")
        self.add_button.clicked.connect(self._add_layer)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Layer")
        self.remove_button.clicked.connect(self._remove_layer)
        button_layout.addWidget(self.remove_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _initialize_default_layers(self) -> None:
        """Initialize default layer structure."""
        default_layers = [
            Layer(1, "Architectural", True, True, QColor(Qt.GlobalColor.gray), "architectural"),
            Layer(2, "Devices - Detection", True, False, QColor(Qt.GlobalColor.red), "devices"),
            Layer(3, "Devices - Notification", True, False, QColor(Qt.GlobalColor.blue), "devices"),
            Layer(4, "Devices - Power", True, False, QColor(Qt.GlobalColor.yellow), "devices"),
            Layer(5, "Wiring - SLC", True, False, QColor(Qt.GlobalColor.green), "wiring"),
            Layer(6, "Wiring - NAC", True, False, QColor(Qt.GlobalColor.cyan), "wiring"),
            Layer(7, "Wiring - Power", True, False, QColor(Qt.GlobalColor.magenta), "wiring"),
            Layer(8, "Wiring - Control", True, False, QColor(Qt.GlobalColor.darkGreen), "wiring"),
            Layer(9, "Conduit", True, False, QColor(Qt.GlobalColor.darkGray), "conduit"),
            Layer(10, "Coverage", True, False, QColor(255, 165, 0), "coverage"),  # Orange
            Layer(11, "Annotations", True, False, QColor(Qt.GlobalColor.black), "annotations"),
        ]

        for layer in default_layers:
            self.layers[layer.id] = layer

        self._update_table()

    def _apply_preset(self, preset: str) -> None:
        """Apply a preset configuration."""
        if preset == "Designer":
            # Designer sees everything, can edit most
            for layer in self.layers.values():
                layer.visible = True
                layer.locked = layer.type == "architectural"
        elif preset == "AHJ":
            # AHJ sees compliance-related layers
            for layer in self.layers.values():
                layer.visible = layer.type in ["architectural", "devices", "coverage"]
                layer.locked = True
        elif preset == "Installer":
            # Installer sees installation layers
            for layer in self.layers.values():
                layer.visible = layer.type in ["architectural", "wiring", "conduit", "annotations"]
                layer.locked = layer.type == "architectural"

        self._update_table()
        self.preset_applied.emit(preset)

    def _update_table(self) -> None:
        """Update the table with current layer data."""
        self.layer_table.setRowCount(len(self.layers))

        for row, layer in enumerate(
            sorted(self.layers.values(), key=lambda layer_obj: layer_obj.id)
        ):
            # Name
            name_item = QTableWidgetItem(layer.name)
            name_item.setData(Qt.ItemDataRole.UserRole, layer.id)
            self.layer_table.setItem(row, 0, name_item)

            # Visible checkbox
            visible_cb = QCheckBox()
            visible_cb.setChecked(layer.visible)
            visible_cb.stateChanged.connect(
                lambda state, lid=layer.id: self._on_visibility_changed(lid, state)
            )
            self.layer_table.setCellWidget(row, 1, visible_cb)

            # Locked checkbox
            locked_cb = QCheckBox()
            locked_cb.setChecked(layer.locked)
            locked_cb.stateChanged.connect(
                lambda state, lid=layer.id: self._on_lock_changed(lid, state)
            )
            self.layer_table.setCellWidget(row, 2, locked_cb)

            # Color button
            color_button = QPushButton()
            color_button.setStyleSheet(
                f"background-color: {layer.color.name()}; border: 1px solid black;"
            )
            color_button.setFixedSize(20, 20)
            color_button.clicked.connect(lambda checked, lid=layer.id: self._on_color_clicked(lid))
            self.layer_table.setCellWidget(row, 3, color_button)

            # Type
            type_item = QTableWidgetItem(layer.type.title())
            self.layer_table.setItem(row, 4, type_item)

    def _on_preset_changed(self, preset: str) -> None:
        """Handle preset change."""
        self.current_preset = preset
        self._apply_preset(preset)

    def _on_layer_selected(self) -> None:
        """Handle layer selection."""
        current_row = self.layer_table.currentRow()
        if current_row >= 0:
            item = self.layer_table.item(current_row, 0)
            if item:
                layer_id = item.data(Qt.ItemDataRole.UserRole)
                self.layer_selected.emit(layer_id)

    def _on_visibility_changed(self, layer_id: int, state: int) -> None:
        """Handle visibility change."""
        self.layers[layer_id].visible = bool(state)
        self.layer_changed.emit(layer_id, "visible", bool(state))

    def _on_lock_changed(self, layer_id: int, state: int) -> None:
        """Handle lock change."""
        self.layers[layer_id].locked = bool(state)
        self.layer_changed.emit(layer_id, "locked", bool(state))

    def _on_color_clicked(self, layer_id: int) -> None:
        """Handle color selection."""
        layer = self.layers[layer_id]
        color = QColorDialog.getColor(layer.color, self, f"Choose color for {layer.name}")
        if color.isValid():
            layer.color = color
            self.layer_changed.emit(layer_id, "color", color)
            self._update_table()

    def _add_layer(self) -> None:
        """Add a new custom layer."""
        next_id = max(self.layers.keys()) + 1 if self.layers else 1
        layer = Layer(
            next_id, f"Custom Layer {next_id}", True, False, QColor(Qt.GlobalColor.white), "custom"
        )
        self.layers[next_id] = layer
        self._update_table()

    def _remove_layer(self) -> None:
        """Remove selected layer."""
        current_row = self.layer_table.currentRow()
        if current_row >= 0:
            item = self.layer_table.item(current_row, 0)
            if item:
                layer_id = item.data(Qt.ItemDataRole.UserRole)
                if layer_id in self.layers and self.layers[layer_id].type != "architectural":
                    del self.layers[layer_id]
                    self._update_table()

    def get_layer(self, layer_id: int) -> Layer | None:
        """Get layer by ID."""
        return self.layers.get(layer_id)

    def get_visible_layers(self) -> list[Layer]:
        """Get all visible layers."""
        return [layer for layer in self.layers.values() if layer.visible]

    def get_layers_by_type(self, layer_type: str) -> list[Layer]:
        """Get layers by type."""
        return [layer for layer in self.layers.values() if layer.type == layer_type]
