"""
Fire alarm layer management system.
Handles separation of fire alarm layers from architectural layers,
with proper CAD layer organization and display control.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QColor, QPen, QBrush
import sqlite3


class LayerType(Enum):
    """Fire alarm layer types."""
    FIRE_ALARM = "fire_alarm"
    ARCHITECTURAL = "architectural" 
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    PLUMBING = "plumbing"
    STRUCTURAL = "structural"
    ANNOTATION = "annotation"


@dataclass
class CADLayer:
    """Represents a CAD layer with display properties."""
    name: str
    layer_type: LayerType
    color: QColor
    line_weight: int = 1
    line_type: str = "Continuous"
    visible: bool = True
    printable: bool = True
    locked: bool = False
    description: str = ""
    display_order: int = 0
    
    def __post_init__(self):
        if isinstance(self.color, str):
            self.color = QColor(self.color)


class FireAlarmLayerManager:
    """Manages fire alarm specific layers and layer organization."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.con = db_connection
        self.con.row_factory = sqlite3.Row
        self.current_layers: Dict[str, CADLayer] = {}
        self._load_standard_layers()
        
    def _load_standard_layers(self):
        """Load standard fire alarm layers from database.""" 
        cur = self.con.cursor()
        
        cur.execute("""
            SELECT layer_name, layer_type, color_rgb, line_weight, 
                   visible, printable, description
            FROM fire_alarm_layers
            ORDER BY layer_name
        """)
        
        for row in cur.fetchall():
            layer = CADLayer(
                name=row['layer_name'],
                layer_type=LayerType(row['layer_type']),
                color=QColor(row['color_rgb']),
                line_weight=row['line_weight'],
                visible=bool(row['visible']),
                printable=bool(row['printable']),
                description=row['description']
            )
            self.current_layers[layer.name] = layer
            
    def get_fire_alarm_layers(self) -> Dict[str, CADLayer]:
        """Get all fire alarm specific layers."""
        return {name: layer for name, layer in self.current_layers.items() 
                if layer.layer_type == LayerType.FIRE_ALARM}
        
    def get_layers_by_type(self, layer_type: LayerType) -> Dict[str, CADLayer]:
        """Get all layers of specified type."""
        return {name: layer for name, layer in self.current_layers.items()
                if layer.layer_type == layer_type}
                
    def create_layer(self, name: str, layer_type: LayerType, 
                    color: QColor, description: str = "") -> CADLayer:
        """Create a new layer."""
        layer = CADLayer(
            name=name,
            layer_type=layer_type, 
            color=color,
            description=description
        )
        
        self.current_layers[name] = layer
        self._save_layer_to_db(layer)
        return layer
        
    def delete_layer(self, layer_name: str) -> bool:
        """Delete a layer."""
        if layer_name in self.current_layers:
            del self.current_layers[layer_name]
            
            # Remove from database
            cur = self.con.cursor()
            cur.execute("DELETE FROM fire_alarm_layers WHERE layer_name = ?", (layer_name,))
            self.con.commit()
            return True
        return False
        
    def set_layer_visibility(self, layer_name: str, visible: bool):
        """Set layer visibility."""
        if layer_name in self.current_layers:
            self.current_layers[layer_name].visible = visible
            self._update_layer_in_db(layer_name, {'visible': visible})
            
    def set_layer_printable(self, layer_name: str, printable: bool):
        """Set layer printable status."""
        if layer_name in self.current_layers:
            self.current_layers[layer_name].printable = printable
            self._update_layer_in_db(layer_name, {'printable': printable})
            
    def set_layer_color(self, layer_name: str, color: QColor):
        """Set layer color."""
        if layer_name in self.current_layers:
            self.current_layers[layer_name].color = color
            self._update_layer_in_db(layer_name, {'color_rgb': color.name()})
            
    def get_device_layer(self, device_type: str) -> str:
        """Get appropriate layer name for device type."""
        device_layer_mapping = {
            'FACP': 'FA-PANELS',
            'Detector': 'FA-DEVICES',
            'Notification': 'FA-DEVICES', 
            'Initiating': 'FA-DEVICES',
            'Module': 'FA-DEVICES',
        }
        return device_layer_mapping.get(device_type, 'FA-DEVICES')
        
    def get_connection_layer(self, connection_type: str) -> str:
        """Get appropriate layer for connection/wire type."""
        connection_layer_mapping = {
            'SLC': 'FA-WIRING',
            'NAC': 'FA-WIRING',
            'IDC': 'FA-WIRING',
            'Power': 'E-POWER',
        }
        return connection_layer_mapping.get(connection_type, 'FA-WIRING')
        
    def freeze_architectural_layers(self):
        """Lock all architectural layers to prevent modification."""
        arch_layers = self.get_layers_by_type(LayerType.ARCHITECTURAL)
        for layer_name, layer in arch_layers.items():
            layer.locked = True
            self._update_layer_in_db(layer_name, {'locked': True})
            
    def show_only_fire_alarm_layers(self):
        """Hide all non-fire-alarm layers."""
        for layer_name, layer in self.current_layers.items():
            visible = layer.layer_type == LayerType.FIRE_ALARM
            layer.visible = visible
            self._update_layer_in_db(layer_name, {'visible': visible})
            
    def show_all_layers(self):
        """Show all layers."""
        for layer_name, layer in self.current_layers.items():
            layer.visible = True
            self._update_layer_in_db(layer_name, {'visible': True})
            
    def get_layer_display_properties(self, layer_name: str) -> Optional[Dict[str, Any]]:
        """Get display properties for a layer."""
        if layer_name not in self.current_layers:
            return None
            
        layer = self.current_layers[layer_name]
        return {
            'color': layer.color,
            'line_weight': layer.line_weight,
            'line_type': layer.line_type,
            'visible': layer.visible,
            'printable': layer.printable,
            'locked': layer.locked
        }
        
    def _save_layer_to_db(self, layer: CADLayer):
        """Save layer to database."""
        cur = self.con.cursor()
        
        cur.execute("""
            INSERT OR REPLACE INTO fire_alarm_layers
            (layer_name, layer_type, color_rgb, line_weight, visible, printable, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            layer.name, layer.layer_type.value, layer.color.name(), 
            layer.line_weight, layer.visible, layer.printable, layer.description
        ))
        self.con.commit()
        
    def _update_layer_in_db(self, layer_name: str, updates: Dict[str, Any]):
        """Update layer properties in database."""
        if not updates:
            return
            
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
            
        values.append(layer_name)
        
        cur = self.con.cursor()
        cur.execute(f"""
            UPDATE fire_alarm_layers 
            SET {', '.join(set_clauses)}
            WHERE layer_name = ?
        """, values)
        self.con.commit()


class LayerTableModel(QAbstractTableModel):
    """Table model for displaying layers in UI."""
    
    def __init__(self, layer_manager: FireAlarmLayerManager, parent=None):
        super().__init__(parent)
        self.layer_manager = layer_manager
        self.headers = ["Layer", "Type", "Color", "Visible", "Printable", "Description"]
        self.layers = list(layer_manager.current_layers.values())
        
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.layers)
        
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        return len(self.headers)
        
    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
            
        layer = self.layers[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:  # Layer name
                return layer.name
            elif col == 1:  # Type
                return layer.layer_type.value.replace('_', ' ').title()
            elif col == 2:  # Color
                return layer.color.name()
            elif col == 3:  # Visible
                return "Yes" if layer.visible else "No"
            elif col == 4:  # Printable
                return "Yes" if layer.printable else "No"
            elif col == 5:  # Description
                return layer.description
                
        elif role == Qt.ItemDataRole.BackgroundRole and col == 2:
            # Show color in background
            return QBrush(layer.color)
            
        elif role == Qt.ItemDataRole.CheckStateRole:
            if col == 3:  # Visible checkbox
                return Qt.CheckState.Checked if layer.visible else Qt.CheckState.Unchecked
            elif col == 4:  # Printable checkbox
                return Qt.CheckState.Checked if layer.printable else Qt.CheckState.Unchecked
                
        return None
        
    def headerData(self, section: int, orientation: Qt.Orientation, 
                  role: int = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None
        
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
            
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        
        # Make visible and printable columns checkable
        if index.column() in [3, 4]:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
            
        return flags
        
    def setData(self, index: QModelIndex | QPersistentModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False
            
        layer = self.layers[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.CheckStateRole:
            if col == 3:  # Visible
                visible = value == Qt.CheckState.Checked
                self.layer_manager.set_layer_visibility(layer.name, visible)
                self.dataChanged.emit(index, index)
                return True
            elif col == 4:  # Printable
                printable = value == Qt.CheckState.Checked
                self.layer_manager.set_layer_printable(layer.name, printable)
                self.dataChanged.emit(index, index)
                return True
                
        return False
        
    def refresh(self):
        """Refresh model data."""
        self.beginResetModel()
        self.layers = list(self.layer_manager.current_layers.values())
        self.endResetModel()


class LayerManagerWidget(QtWidgets.QWidget):
    """Widget for managing CAD layers."""
    
    layer_visibility_changed = QtCore.Signal(str, bool)  # layer_name, visible
    layer_selected = QtCore.Signal(str)  # layer_name
    
    def __init__(self, layer_manager: FireAlarmLayerManager, parent=None):
        super().__init__(parent)
        self.layer_manager = layer_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the widget UI."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Layer type filter
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(QtWidgets.QLabel("Filter:"))
        
        self.type_filter = QtWidgets.QComboBox()
        self.type_filter.addItem("All Layers")
        for layer_type in LayerType:
            self.type_filter.addItem(layer_type.value.replace('_', ' ').title())
        self.type_filter.currentTextChanged.connect(self.filter_layers)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Layer table
        self.table_model = LayerTableModel(self.layer_manager)
        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.selectionModel().currentRowChanged.connect(self.on_layer_selected)
        
        # Resize columns
        header = self.table_view.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(4):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            
        layout.addWidget(self.table_view)
        
        # Action buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.new_layer_btn = QtWidgets.QPushButton("New Layer")
        self.new_layer_btn.clicked.connect(self.create_new_layer)
        button_layout.addWidget(self.new_layer_btn)
        
        self.delete_layer_btn = QtWidgets.QPushButton("Delete Layer")
        self.delete_layer_btn.clicked.connect(self.delete_selected_layer)
        button_layout.addWidget(self.delete_layer_btn)
        
        button_layout.addStretch()
        
        self.show_fa_only_btn = QtWidgets.QPushButton("Fire Alarm Only")
        self.show_fa_only_btn.clicked.connect(self.layer_manager.show_only_fire_alarm_layers)
        self.show_fa_only_btn.clicked.connect(self.refresh_table)
        button_layout.addWidget(self.show_fa_only_btn)
        
        self.show_all_btn = QtWidgets.QPushButton("Show All")
        self.show_all_btn.clicked.connect(self.layer_manager.show_all_layers)
        self.show_all_btn.clicked.connect(self.refresh_table)
        button_layout.addWidget(self.show_all_btn)
        
        layout.addLayout(button_layout)
        
    def filter_layers(self, filter_text: str):
        """Filter layers by type."""
        # This would be implemented to filter the table view
        pass
        
    def on_layer_selected(self, current: QModelIndex, previous: QModelIndex):
        """Handle layer selection."""
        if current.isValid():
            layer_name = self.table_model.layers[current.row()].name
            self.layer_selected.emit(layer_name)
            
    def create_new_layer(self):
        """Create a new layer."""
        dialog = NewLayerDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name, layer_type, color, description = dialog.get_layer_info()
            self.layer_manager.create_layer(name, layer_type, color, description)
            self.refresh_table()
            
    def delete_selected_layer(self):
        """Delete the selected layer."""
        current = self.table_view.currentIndex()
        if current.isValid():
            layer_name = self.table_model.layers[current.row()].name
            
            reply = QtWidgets.QMessageBox.question(
                self, "Delete Layer",
                f"Are you sure you want to delete layer '{layer_name}'?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.layer_manager.delete_layer(layer_name)
                self.refresh_table()
                
    def refresh_table(self):
        """Refresh the layer table."""
        self.table_model.refresh()


class NewLayerDialog(QtWidgets.QDialog):
    """Dialog for creating a new layer."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Layer")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up dialog UI."""
        layout = QtWidgets.QFormLayout(self)
        
        self.name_edit = QtWidgets.QLineEdit()
        layout.addRow("Layer Name:", self.name_edit)
        
        self.type_combo = QtWidgets.QComboBox()
        for layer_type in LayerType:
            self.type_combo.addItem(layer_type.value.replace('_', ' ').title(), layer_type)
        layout.addRow("Layer Type:", self.type_combo)
        
        self.color_button = QtWidgets.QPushButton()
        self.color = QColor(255, 0, 0)  # Default red
        self.color_button.setStyleSheet(f"background-color: {self.color.name()}")
        self.color_button.clicked.connect(self.choose_color)
        layout.addRow("Color:", self.color_button)
        
        self.description_edit = QtWidgets.QLineEdit()
        layout.addRow("Description:", self.description_edit)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("OK")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addRow(button_layout)
        
    def choose_color(self):
        """Choose layer color."""
        color = QtWidgets.QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
            
    def get_layer_info(self) -> Tuple[str, LayerType, QColor, str]:
        """Get the layer information."""
        return (
            self.name_edit.text(),
            self.type_combo.currentData(),
            self.color,
            self.description_edit.text()
        )