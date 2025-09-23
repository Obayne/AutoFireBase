"""
Wire connection drawing tool for connecting fire alarm devices to FACP panels.
Handles visual wire drawing, SLC addressing, and connection management.
"""

from typing import List, Optional, Tuple, Dict, Any
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsPathItem
import math


class WireConnection:
    """Represents a wire connection between two devices."""
    
    def __init__(self, from_device, to_device, connection_type: str = "SLC"):
        self.from_device = from_device
        self.to_device = to_device
        self.connection_type = connection_type
        self.wire_path: List[QPointF] = []
        self.length_feet: float = 0.0
        self.slc_address: Optional[int] = None
        self.circuit_id: Optional[int] = None
        self.graphics_item: Optional[WireGraphicsItem] = None
        self.connection_id: Optional[int] = None  # Database ID for the connection
        
    def calculate_length(self, px_per_ft: float = 12.0) -> float:
        """Calculate wire length based on path."""
        if len(self.wire_path) < 2:
            return 0.0
            
        total_length = 0.0
        for i in range(1, len(self.wire_path)):
            p1 = self.wire_path[i-1]
            p2 = self.wire_path[i]
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            length_px = math.sqrt(dx*dx + dy*dy)
            total_length += length_px / px_per_ft
            
        self.length_feet = total_length
        return total_length
        
    def set_addressing_info(self, circuit_id: int, address: int, connection_id: Optional[int] = None):
        """Set addressing information for this connection."""
        self.circuit_id = circuit_id
        self.slc_address = address
        self.connection_id = connection_id
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert connection to dictionary for serialization."""
        return {
            "from_device": str(id(self.from_device)),  # Use ID for reference
            "to_device": str(id(self.to_device)),      # Use ID for reference
            "connection_type": self.connection_type,
            "wire_path": [(p.x(), p.y()) for p in self.wire_path],
            "length_feet": self.length_feet,
            "slc_address": self.slc_address,
            "circuit_id": self.circuit_id,
            "connection_id": self.connection_id
        }


class WireGraphicsItem(QGraphicsPathItem):
    """Graphics item for displaying wire connections."""
    
    def __init__(self, connection: WireConnection, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.setZValue(-1)  # Behind devices
        self._setup_appearance()
        self._update_path()
        
    def _setup_appearance(self):
        """Set up wire visual appearance."""
        if self.connection.connection_type == "SLC":
            pen = QPen(QColor(255, 0, 0), 2, Qt.PenStyle.SolidLine)  # Red for SLC
        elif self.connection.connection_type == "NAC":
            pen = QPen(QColor(0, 0, 255), 2, Qt.PenStyle.SolidLine)  # Blue for NAC
        else:
            pen = QPen(QColor(0, 150, 0), 2, Qt.PenStyle.SolidLine)  # Green for other
            
        self.setPen(pen)
        
    def _update_path(self):
        """Update the wire path graphics."""
        if len(self.connection.wire_path) < 2:
            return
            
        path = QPainterPath()
        path.moveTo(self.connection.wire_path[0])
        
        for point in self.connection.wire_path[1:]:
            path.lineTo(point)
            
        self.setPath(path)
        
    def update_connection(self, connection: WireConnection):
        """Update the wire connection and redraw."""
        self.connection = connection
        self._setup_appearance()
        self._update_path()


class WireDrawingTool(QtCore.QObject):
    """Tool for drawing wire connections between devices."""
    
    # Signals
    connection_created = QtCore.Signal(object)  # WireConnection
    connection_updated = QtCore.Signal(object)  # WireConnection
    addressing_requested = QtCore.Signal(object, object)  # from_device, to_device
    
    def __init__(self, graphics_view, slc_system=None):
        super().__init__()
        self.graphics_view = graphics_view
        self.slc_system = slc_system
        self.is_active = False
        self.current_wire_path: List[QPointF] = []
        self.drawing_item: Optional[QGraphicsPathItem] = None
        self.from_device = None
        self.connections: List[WireConnection] = []
        self.connection_graphics: List[WireGraphicsItem] = []
        
    def activate(self):
        """Activate the wire drawing tool."""
        self.is_active = True
        self.graphics_view.setCursor(Qt.CursorShape.CrossCursor)
        
    def deactivate(self):
        """Deactivate the wire drawing tool.""" 
        self.is_active = False
        self.graphics_view.setCursor(Qt.CursorShape.ArrowCursor)
        self._clear_current_drawing()
        
    def handle_mouse_press(self, event):
        """Handle mouse press for wire drawing."""
        if not self.is_active:
            return False
            
        scene_pos = self.graphics_view.mapToScene(event.pos())
        
        # Check if clicking on a device
        item = self.graphics_view.scene().itemAt(scene_pos, self.graphics_view.transform())
        device_item = self._find_device_item(item)
        
        if device_item:
            if self.from_device is None:
                # Start wire from this device
                self._start_wire_from_device(device_item, scene_pos)
            else:
                # End wire at this device
                self._end_wire_at_device(device_item, scene_pos)
        else:
            if self.from_device is not None:
                # Add waypoint to current wire
                self._add_wire_waypoint(scene_pos)
                
        return True
        
    def handle_mouse_move(self, event):
        """Handle mouse move for wire drawing preview."""
        if not self.is_active or self.from_device is None:
            return False
            
        scene_pos = self.graphics_view.mapToScene(event.pos())
        self._update_wire_preview(scene_pos)
        return True
        
    def handle_key_press(self, event):
        """Handle key press events."""
        if not self.is_active:
            return False
            
        if event.key() == Qt.Key.Key_Escape:
            self._cancel_current_wire()
            return True
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self._finish_current_wire()
            return True
            
        return False
        
    def _find_device_item(self, item):
        """Find the device item from a graphics item."""
        # Look for device-related items by checking properties or parent hierarchy
        current = item
        while current:
            # Check if this is a DeviceItem (has device_type attribute)
            if hasattr(current, 'device_type') and hasattr(current, 'add_connection'):
                return current
            current = current.parentItem()
        return None
        
    def _start_wire_from_device(self, device_item, pos: QPointF):
        """Start drawing a wire from a device."""
        self.from_device = device_item
        self.current_wire_path = [pos]
        self._create_preview_graphics()
        
    def _end_wire_at_device(self, device_item, pos: QPointF):
        """End wire drawing at a device."""
        if device_item == self.from_device:
            return  # Can't connect device to itself
            
        self.current_wire_path.append(pos)
        
        # Create wire connection
        connection = WireConnection(self.from_device, device_item)
        connection.wire_path = self.current_wire_path.copy()
        connection.calculate_length(self.graphics_view.px_per_ft)
        
        # Request SLC addressing
        self.addressing_requested.emit(self.from_device, device_item)
        
        # Add to connections
        self.connections.append(connection)
        
        # Create graphics item for wire
        wire_graphics = WireGraphicsItem(connection)
        connection.graphics_item = wire_graphics  # Store reference to graphics item
        self.graphics_view.scene().addItem(wire_graphics)
        self.connection_graphics.append(wire_graphics)
        
        # Update device connections
        if self.from_device and hasattr(self.from_device, 'add_connection'):
            self.from_device.add_connection(device_item)
        
        # Emit signal
        self.connection_created.emit(connection)
        
        # Reset for next wire
        self._clear_current_drawing()
        
    def _add_wire_waypoint(self, pos: QPointF):
        """Add a waypoint to the current wire path."""
        if self.from_device is not None:
            self.current_wire_path.append(pos)
            self._update_preview_graphics()
            
    def _create_preview_graphics(self):
        """Create graphics item for wire preview.""" 
        self.drawing_item = QGraphicsPathItem()
        pen = QPen(QColor(255, 100, 100), 2, Qt.PenStyle.DashLine)
        self.drawing_item.setPen(pen)
        self.drawing_item.setZValue(10)  # On top
        self.graphics_view.scene().addItem(self.drawing_item)
        
    def _update_preview_graphics(self):
        """Update the preview graphics with current path."""
        if not self.drawing_item or len(self.current_wire_path) == 0:
            return
            
        path = QPainterPath()
        path.moveTo(self.current_wire_path[0])
        
        for point in self.current_wire_path[1:]:
            path.lineTo(point)
            
        self.drawing_item.setPath(path)
        
    def _update_wire_preview(self, mouse_pos: QPointF):
        """Update wire preview with mouse position."""
        if not self.drawing_item or len(self.current_wire_path) == 0:
            return
            
        # Create preview path including mouse position
        path = QPainterPath()
        path.moveTo(self.current_wire_path[0])
        
        for point in self.current_wire_path[1:]:
            path.lineTo(point)
            
        path.lineTo(mouse_pos)  # Preview line to mouse
        self.drawing_item.setPath(path)
        
    def _clear_current_drawing(self):
        """Clear current wire drawing state."""
        if self.drawing_item:
            self.graphics_view.scene().removeItem(self.drawing_item)
            self.drawing_item = None
            
        self.from_device = None
        self.current_wire_path.clear()
        
    def _cancel_current_wire(self):
        """Cancel current wire drawing."""
        self._clear_current_drawing()
        
    def _finish_current_wire(self):
        """Finish current wire without connecting to device."""
        # Could be used for ending wire at empty space
        self._clear_current_drawing()
        
    def remove_connection(self, connection: WireConnection):
        """Remove a wire connection."""
        if connection in self.connections:
            self.connections.remove(connection)
            
        # Remove graphics
        for graphics in self.connection_graphics:
            if graphics.connection == connection:
                self.graphics_view.scene().removeItem(graphics)
                self.connection_graphics.remove(graphics)
                break
                
        # Update device connections
        if hasattr(connection, 'from_device') and hasattr(connection, 'to_device'):
            # Remove connection from devices
            if connection.from_device and connection.to_device:
                # Remove the connection from both devices
                if hasattr(connection.from_device, 'remove_connection'):
                    connection.from_device.remove_connection(connection.to_device)
                
    def get_device_connections(self, device_item) -> List[WireConnection]:
        """Get all connections for a device."""
        connections = []
        for conn in self.connections:
            if conn.from_device == device_item or conn.to_device == device_item:
                connections.append(conn)
        return connections
        
    def update_slc_addressing(self, connection: WireConnection, circuit_id: int, address: int):
        """Update SLC addressing for a connection."""
        connection.set_addressing_info(circuit_id, address)
        
        # Update graphics to show addressing
        for graphics in self.connection_graphics:
            if graphics.connection == connection:
                graphics.update_connection(connection)
                break
                
        self.connection_updated.emit(connection)
        
        # Update devices with addressing information
        if connection.to_device and hasattr(connection.to_device, 'set_slc_address'):
            connection.to_device.set_slc_address(address)
        if connection.to_device and hasattr(connection.to_device, 'set_circuit_id'):
            connection.to_device.set_circuit_id(circuit_id)
            
    def get_connection_by_devices(self, from_device, to_device) -> Optional[WireConnection]:
        """Get connection between two specific devices."""
        for conn in self.connections:
            if conn.from_device == from_device and conn.to_device == to_device:
                return conn
        return None
        
    def serialize_connections(self) -> List[Dict[str, Any]]:
        """Serialize all connections for saving."""
        return [conn.to_dict() for conn in self.connections]
        
    def load_connections(self, connection_data: List[Dict[str, Any]]):
        """Load connections from serialized data."""
        self.connections.clear()
        self.connection_graphics.clear()
        
        # This would reconstruct connections from saved data
        # For now, we'll just clear and let the user recreate connections
        pass

class SLCAddressingDialog(QtWidgets.QDialog):
    """Dialog for configuring SLC addressing when connecting devices."""
    
    def __init__(self, parent=None, from_device=None, to_device=None, slc_system=None):
        super().__init__(parent)
        self.from_device = from_device
        self.to_device = to_device
        self.slc_system = slc_system
        self.selected_circuit_id = None
        self.assigned_address = None
        self.available_circuits = []
        
        self.setWindowTitle("SLC Device Addressing")
        self.setModal(True)
        self._setup_ui()
        self._load_available_circuits()
        
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Connection info
        info_group = QtWidgets.QGroupBox("Connection Information")
        info_layout = QtWidgets.QFormLayout(info_group)
        
        from_name = getattr(self.from_device, 'name', 'Unknown Device')
        to_name = getattr(self.to_device, 'name', 'Unknown Device')
        
        info_layout.addRow("From Device:", QtWidgets.QLabel(from_name))
        info_layout.addRow("To Device:", QtWidgets.QLabel(to_name))
        layout.addWidget(info_group)
        
        # Circuit selection
        circuit_group = QtWidgets.QGroupBox("SLC Circuit Selection")
        circuit_layout = QtWidgets.QFormLayout(circuit_group)
        
        self.circuit_combo = QtWidgets.QComboBox()
        self.circuit_combo.currentTextChanged.connect(self._on_circuit_changed)
        circuit_layout.addRow("SLC Circuit:", self.circuit_combo)
        
        self.circuit_info = QtWidgets.QTextEdit()
        self.circuit_info.setMaximumHeight(100)
        self.circuit_info.setReadOnly(True)
        circuit_layout.addRow("Circuit Info:", self.circuit_info)
        layout.addWidget(circuit_group)
        
        # Address assignment
        address_group = QtWidgets.QGroupBox("Device Address Assignment")
        address_layout = QtWidgets.QFormLayout(address_group)
        
        self.address_spin = QtWidgets.QSpinBox()
        self.address_spin.setRange(1, 159)
        address_layout.addRow("Device Address:", self.address_spin)
        
        self.auto_assign_btn = QtWidgets.QPushButton("Auto-Assign Next Available")
        self.auto_assign_btn.clicked.connect(self._auto_assign_address)
        address_layout.addRow(self.auto_assign_btn)
        layout.addWidget(address_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("Connect && Assign")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
    def _load_available_circuits(self):
        """Load available SLC circuits."""
        self.circuit_combo.clear()
        self.available_circuits = []
        
        if not self.slc_system:
            # Mock data for now - would load from actual panel/project
            circuits = [
                {"id": 1, "name": "SLC Loop 1", "devices": 15, "max": 159},
                {"id": 2, "name": "SLC Loop 2", "devices": 8, "max": 159}
            ]
            
            for circuit in circuits:
                display_text = f"{circuit['name']} ({circuit['devices']}/{circuit['max']} devices)"
                self.circuit_combo.addItem(display_text, circuit)
                self.available_circuits.append(circuit)
        else:
            # Load actual circuits from SLC system
            try:
                # This would query the actual SLC system for available circuits
                # For now, we'll mock this with sample data
                circuits = [
                    {"id": 1, "name": "SLC Loop 1", "devices": 15, "max": 159},
                    {"id": 2, "name": "SLC Loop 2", "devices": 8, "max": 159}
                ]
                
                for circuit in circuits:
                    display_text = f"{circuit['name']} ({circuit['devices']}/{circuit['max']} devices)"
                    self.circuit_combo.addItem(display_text, circuit)
                    self.available_circuits.append(circuit)
            except Exception as e:
                print(f"Error loading circuits: {e}")
                # Fallback to mock data
                circuits = [
                    {"id": 1, "name": "SLC Loop 1", "devices": 15, "max": 159},
                    {"id": 2, "name": "SLC Loop 2", "devices": 8, "max": 159}
                ]
                
                for circuit in circuits:
                    display_text = f"{circuit['name']} ({circuit['devices']}/{circuit['max']} devices)"
                    self.circuit_combo.addItem(display_text, circuit)
                    self.available_circuits.append(circuit)
            
    def _on_circuit_changed(self):
        """Handle circuit selection change."""
        current_data = self.circuit_combo.currentData()
        if not current_data:
            return
            
        self.selected_circuit_id = current_data['id']
        
        # Update circuit info
        info_text = f"Loop {current_data['id']}\n"
        info_text += f"Devices: {current_data['devices']}/{current_data['max']}\n"
        info_text += f"Available addresses: {current_data['max'] - current_data['devices']}"
        self.circuit_info.setPlainText(info_text)
        
        # Auto-assign next address
        self._auto_assign_address()
        
    def _auto_assign_address(self):
        """Auto-assign next available address."""
        if self.selected_circuit_id:
            # Find the selected circuit data
            selected_circuit = None
            for circuit in self.available_circuits:
                if circuit['id'] == self.selected_circuit_id:
                    selected_circuit = circuit
                    break
                    
            if selected_circuit:
                # Mock next available address - would query SLC system
                # For now, we'll just increment the device count
                next_address = selected_circuit['devices'] + 1
                if next_address > selected_circuit['max']:
                    next_address = 1  # Wrap around if needed
                    
                self.address_spin.setValue(next_address)
                self.assigned_address = next_address
            else:
                # Fallback
                next_address = 16  # Mock value
                self.address_spin.setValue(next_address)
                self.assigned_address = next_address
            
    def get_assignment(self) -> Tuple[Optional[int], Optional[int]]:
        """Get the circuit ID and assigned address."""
        return self.selected_circuit_id, self.assigned_address
