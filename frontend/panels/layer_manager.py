"""
FlameCAD Professional Layer Management System
Manages layers with visibility, locking, colors, and professional presets for fire alarm CAD.
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

# Import our professional design system
try:
    from frontend.design_system import AutoFireColor, AutoFireStyleSheet, AutoFireFont
    DESIGN_SYSTEM_AVAILABLE = True
except ImportError:
    # Fallback for development/testing
    DESIGN_SYSTEM_AVAILABLE = False
    class AutoFireColor:
        PRIMARY = "#C41E3A"
        SECONDARY = "#8B0000"
        ACCENT = "#FF6B35"
        
    class AutoFireStyleSheet:
        @staticmethod
        def group_box(): return ""
        @staticmethod 
        def button_primary(): return ""
        @staticmethod
        def input_field(): return ""


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
        """Set up the professional layer manager UI with FlameCAD styling."""
        # Apply professional FlameCAD styling
        if DESIGN_SYSTEM_AVAILABLE:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {AutoFireColor.SURFACE_PRIMARY if hasattr(AutoFireColor, 'SURFACE_PRIMARY') else '#f8f9fa'};
                    color: {AutoFireColor.TEXT_PRIMARY if hasattr(AutoFireColor, 'TEXT_PRIMARY') else '#333'};
                    font-size: 12px;
                    font-family: 'Segoe UI', 'Roboto', sans-serif;
                }}
                QLabel {{
                    color: {AutoFireColor.TEXT_PRIMARY if hasattr(AutoFireColor, 'TEXT_PRIMARY') else '#333'};
                    font-weight: 600;
                    font-size: 13px;
                }}
                QComboBox {{
                    padding: 8px 12px;
                    border: 2px solid {AutoFireColor.BORDER_PRIMARY if hasattr(AutoFireColor, 'BORDER_PRIMARY') else '#ddd'};
                    border-radius: 6px;
                    background-color: {AutoFireColor.SURFACE_SECONDARY if hasattr(AutoFireColor, 'SURFACE_SECONDARY') else '#fff'};
                    color: {AutoFireColor.TEXT_PRIMARY if hasattr(AutoFireColor, 'TEXT_PRIMARY') else '#333'};
                    min-width: 120px;
                    font-weight: 500;
                }}
                QComboBox:focus {{
                    border-color: {AutoFireColor.ACCENT};
                    background-color: {AutoFireColor.SURFACE_PRIMARY if hasattr(AutoFireColor, 'SURFACE_PRIMARY') else '#fff'};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                    background-color: {AutoFireColor.ACCENT};
                    border-top-right-radius: 4px;
                    border-bottom-right-radius: 4px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid white;
                    margin: 2px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: {AutoFireColor.SURFACE_SECONDARY if hasattr(AutoFireColor, 'SURFACE_SECONDARY') else '#fff'};
                    color: {AutoFireColor.TEXT_PRIMARY if hasattr(AutoFireColor, 'TEXT_PRIMARY') else '#333'};
                    border: 2px solid {AutoFireColor.ACCENT};
                    border-radius: 6px;
                    selection-background-color: {AutoFireColor.ACCENT};
                    selection-color: white;
                    padding: 4px;
                }}
                QTableWidget {{
                    background-color: {AutoFireColor.SURFACE_PRIMARY if hasattr(AutoFireColor, 'SURFACE_PRIMARY') else '#fff'};
                    color: {AutoFireColor.TEXT_PRIMARY if hasattr(AutoFireColor, 'TEXT_PRIMARY') else '#333'};
                    border: 2px solid {AutoFireColor.BORDER_PRIMARY if hasattr(AutoFireColor, 'BORDER_PRIMARY') else '#ddd'};
                    border-radius: 8px;
                    gridline-color: {AutoFireColor.BORDER_PRIMARY if hasattr(AutoFireColor, 'BORDER_PRIMARY') else '#eee'};
                    selection-background-color: {AutoFireColor.ACCENT};
                    selection-color: white;
                    alternate-background-color: {AutoFireColor.SURFACE_SECONDARY if hasattr(AutoFireColor, 'SURFACE_SECONDARY') else '#f9f9f9'};
                    font-size: 12px;
                }}
                QTableWidget::item {{
                    padding: 10px 8px;
                    border-bottom: 1px solid {AutoFireColor.BORDER_PRIMARY if hasattr(AutoFireColor, 'BORDER_PRIMARY') else '#eee'};
                    border-right: 1px solid {AutoFireColor.BORDER_PRIMARY if hasattr(AutoFireColor, 'BORDER_PRIMARY') else '#eee'};
                }}
                QTableWidget::item:selected {{
                    background-color: {AutoFireColor.ACCENT};
                    color: white;
                    font-weight: 600;
                }}
                QTableWidget::item:hover {{
                    background-color: {AutoFireColor.BUTTON_HOVER if hasattr(AutoFireColor, 'BUTTON_HOVER') else '#f0f0f0'};
                }}
                QHeaderView::section {{
                    background-color: {AutoFireColor.PRIMARY};
                    color: white;
                    padding: 12px 8px;
                    border: 1px solid {AutoFireColor.SECONDARY};
                    font-weight: bold;
                    font-size: 13px;
                }}
                QHeaderView::section:hover {{
                    background-color: {AutoFireColor.SECONDARY};
                }}
                QPushButton {{
                    background-color: {AutoFireColor.ACCENT};
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {AutoFireColor.SECONDARY};
                }}
                QPushButton:pressed {{
                    background-color: {AutoFireColor.PRIMARY};
                }}
                QPushButton:disabled {{
                    background-color: {AutoFireColor.BORDER_PRIMARY if hasattr(AutoFireColor, 'BORDER_PRIMARY') else '#ccc'};
                    color: {AutoFireColor.TEXT_MUTED if hasattr(AutoFireColor, 'TEXT_MUTED') else '#999'};
                }}
                QCheckBox {{
                    color: {AutoFireColor.TEXT_PRIMARY if hasattr(AutoFireColor, 'TEXT_PRIMARY') else '#333'};
                    spacing: 8px;
                    font-weight: 500;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border-radius: 3px;
                    border: 2px solid {AutoFireColor.BORDER_PRIMARY if hasattr(AutoFireColor, 'BORDER_PRIMARY') else '#ddd'};
                    background-color: {AutoFireColor.SURFACE_SECONDARY if hasattr(AutoFireColor, 'SURFACE_SECONDARY') else '#fff'};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {AutoFireColor.ACCENT};
                    border-color: {AutoFireColor.ACCENT};
                }}
                QCheckBox::indicator:checked:hover {{
                    background-color: {AutoFireColor.SECONDARY};
                }}
            """)
        else:
            # Fallback professional styling
            self.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    color: #333;
                    font-size: 12px;
                    font-family: 'Segoe UI', 'Roboto', sans-serif;
                }
                QTableWidget {
                    background-color: #fff;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    selection-background-color: #FF6B35;
                    alternate-background-color: #f9f9f9;
                }
                QHeaderView::section {
                    background-color: #C41E3A;
                    color: white;
                    padding: 12px 8px;
                    border: 1px solid #8B0000;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #FF6B35;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 600;
                }
            """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Professional preset selector with FlameCAD branding
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(12)

        preset_label = QLabel("🔥 Layer Preset:")
        if DESIGN_SYSTEM_AVAILABLE:
            preset_label.setStyleSheet(f"""
                color: {AutoFireColor.TEXT_PRIMARY if hasattr(AutoFireColor, 'TEXT_PRIMARY') else '#333'};
                font-weight: 700;
                font-size: 14px;
                padding: 5px 0;
            """)
        else:
            preset_label.setStyleSheet("color: #333; font-weight: bold; font-size: 14px; padding: 5px 0;")
        preset_layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["🎨 Designer View", "🏛️ AHJ Inspector", "🔧 Field Installer"])
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(self.preset_combo)

        preset_layout.addStretch()
        layout.addLayout(preset_layout)

        # Professional layer table with enhanced features
        self.layer_table = QTableWidget()
        self.layer_table.setColumnCount(5)
        self.layer_table.setHorizontalHeaderLabels(["Layer Name", "👁️ Visible", "🔒 Locked", "🎨 Color", "📁 Type"])
        self.layer_table.horizontalHeader().setStretchLastSection(True)
        self.layer_table.setAlternatingRowColors(True)
        self.layer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.layer_table.setMinimumHeight(350)
        self.layer_table.itemSelectionChanged.connect(self._on_layer_selected)

        # Enhanced column widths for professional layout
        self.layer_table.setColumnWidth(0, 150)  # Layer Name
        self.layer_table.setColumnWidth(1, 80)   # Visible
        self.layer_table.setColumnWidth(2, 80)   # Locked 
        self.layer_table.setColumnWidth(3, 80)   # Color
        # Type column stretches for full width

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
