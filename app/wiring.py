from PySide6 import QtGui, QtWidgets
from PySide6.QtGui import QPainterPath, QPen, QColor, QBrush
from PySide6.QtCore import QPointF, Qt
from typing import Optional

class WireItem(QtWidgets.QGraphicsPathItem):
    def __init__(self, a: QPointF, b: QPointF, wire_type: str = "SLC"):
        super().__init__()
        self.wire_type = wire_type  # SLC (Signaling Line Circuit) or NAC (Notification Appliance Circuit)
        self.circuit_id: Optional[int] = None
        self.from_device = None
        self.to_device = None
        self.slc_address: Optional[int] = None
        
        path = QPainterPath(a); path.lineTo(b)
        self.setPath(path)
        
        # Set pen based on wire type with enhanced visual representation
        if wire_type == "SLC":
            pen = QPen(QColor(255, 0, 0))  # Red for SLC
            pen.setWidthF(2.5)
        elif wire_type == "NAC":
            pen = QPen(QColor(0, 0, 255))  # Blue for NAC
            pen.setWidthF(2.5)
        else:
            pen = QPen(QColor(0, 100, 0))  # Green for other
            pen.setWidthF(2.0)
            
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setZValue(60)
        
        # Add wire type label
        self.label = QtWidgets.QGraphicsSimpleTextItem(wire_type)
        font = QtGui.QFont("Arial", 6)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setBrush(QBrush(QColor("#FFFFFF")))
        # Position label at midpoint of wire
        mid_x = (a.x() + b.x()) / 2
        mid_y = (a.y() + b.y()) / 2
        self.label.setPos(mid_x - 10, mid_y - 10)
        self.label.setParentItem(self)
        self.label.setVisible(False)  # Hide by default

    def to_json(self):
        p = self.path()
        a = p.elementAt(0)
        b = p.elementAt(1)
        # Access element properties using getattr to avoid linter issues
        ax = float(getattr(a, 'x', 0.0))
        ay = float(getattr(a, 'y', 0.0))
        bx = float(getattr(b, 'x', 0.0))
        by = float(getattr(b, 'y', 0.0))
        return {
            "ax": ax, 
            "ay": ay, 
            "bx": bx, 
            "by": by,
            "wire_type": self.wire_type,
            "circuit_id": self.circuit_id,
            "slc_address": self.slc_address
        }
        
    @staticmethod
    def from_json(d: dict):
        a = QPointF(float(d.get("ax", 0)), float(d.get("ay", 0)))
        b = QPointF(float(d.get("bx", 0)), float(d.get("by", 0)))
        wire_type = d.get("wire_type", "SLC")
        wire = WireItem(a, b, wire_type)
        circuit_id = d.get("circuit_id")
        if circuit_id is not None:
            wire.circuit_id = int(circuit_id)
        slc_address = d.get("slc_address")
        if slc_address is not None:
            wire.slc_address = int(slc_address)
        return wire

class WireManager:
    """Manager for handling wire connections and circuits."""
    
    def __init__(self):
        self.circuits = {}  # circuit_id -> circuit_info
        self.wires = []     # list of WireItem objects
        
    def create_circuit(self, circuit_id: int, circuit_type: str = "SLC", description: str = ""):
        """Create a new circuit."""
        self.circuits[circuit_id] = {
            "type": circuit_type,
            "description": description,
            "devices": [],
            "wires": []
        }
        
    def add_wire_to_circuit(self, wire: WireItem, circuit_id: int):
        """Add a wire to a circuit."""
        if circuit_id not in self.circuits:
            self.create_circuit(circuit_id, wire.wire_type)
            
        wire.circuit_id = circuit_id
        self.circuits[circuit_id]["wires"].append(wire)
        self.wires.append(wire)
        
    def connect_devices(self, from_device, to_device, circuit_id: int, wire_type: str = "SLC"):
        """Create a wire connection between two devices."""
        pos1 = from_device.pos()
        pos2 = to_device.pos()
        wire = WireItem(pos1, pos2, wire_type)
        wire.from_device = from_device
        wire.to_device = to_device
        self.add_wire_to_circuit(wire, circuit_id)
        
        # Add devices to circuit if not already present
        if from_device not in self.circuits[circuit_id]["devices"]:
            self.circuits[circuit_id]["devices"].append(from_device)
        if to_device not in self.circuits[circuit_id]["devices"]:
            self.circuits[circuit_id]["devices"].append(to_device)
            
        # Update connection status for devices
        if hasattr(from_device, 'add_connection'):
            from_device.add_connection(to_device)
        if hasattr(to_device, 'add_connection'):
            to_device.add_connection(from_device)
            
        return wire
        
    def connect_device_to_circuit(self, device, circuit_id: int, auto_assign_address: bool = True):
        """Connect a device to a circuit with optional automatic address assignment."""
        if circuit_id not in self.circuits:
            self.create_circuit(circuit_id, "SLC")
            
        # Add device to circuit if not already present
        if device not in self.circuits[circuit_id]["devices"]:
            self.circuits[circuit_id]["devices"].append(device)
            
        # Auto-assign address if requested
        if auto_assign_address and hasattr(device, 'set_slc_address'):
            # Find next available address
            existing_addresses = []
            for d in self.circuits[circuit_id]["devices"]:
                if hasattr(d, 'slc_address') and d.slc_address is not None:
                    existing_addresses.append(d.slc_address)
                    
            # Assign next available address
            next_address = 1
            while next_address in existing_addresses:
                next_address += 1
            device.set_slc_address(next_address)
            
        # Update connection status
        if hasattr(device, 'set_connection_status'):
            device.set_connection_status("connected")
        
    def get_circuit_wires(self, circuit_id: int) -> list:
        """Get all wires in a circuit."""
        if circuit_id in self.circuits:
            return self.circuits[circuit_id]["wires"]
        return []
        
    def get_circuit_devices(self, circuit_id: int) -> list:
        """Get all devices in a circuit."""
        if circuit_id in self.circuits:
            return self.circuits[circuit_id]["devices"]
        return []
        
    def assign_addresses_to_circuit(self, circuit_id: int) -> int:
        """Assign sequential SLC addresses to all devices on a circuit."""
        if circuit_id not in self.circuits:
            return 0
            
        devices = self.circuits[circuit_id]["devices"]
        assigned_count = 0
        
        # Sort devices by position for consistent addressing
        sorted_devices = sorted(devices, key=lambda d: (d.pos().x(), d.pos().y()))
        
        # Assign addresses sequentially
        for i, device in enumerate(sorted_devices):
            address = i + 1
            if hasattr(device, 'set_slc_address'):
                device.set_slc_address(address)
                assigned_count += 1
                
        return assigned_count
        
    def auto_assign_all_circuits(self) -> dict:
        """Automatically assign addresses to all circuits."""
        results = {}
        for circuit_id in self.circuits:
            assigned = self.assign_addresses_to_circuit(circuit_id)
            results[circuit_id] = assigned
        return results
        
    def get_circuit_statistics(self, circuit_id: int) -> dict:
        """Get statistics for a circuit."""
        if circuit_id not in self.circuits:
            return {}
            
        circuit = self.circuits[circuit_id]
        devices = circuit["devices"]
        wires = circuit["wires"]
        
        # Count device types
        device_types = {}
        for device in devices:
            device_type = getattr(device, 'device_type', 'Unknown')
            device_types[device_type] = device_types.get(device_type, 0) + 1
            
        # Calculate wire length
        total_length = 0.0
        for wire in wires:
            path = wire.path()
            if path.elementCount() >= 2:
                a = path.elementAt(0)
                b = path.elementAt(1)
                # Calculate distance
                dx = getattr(b, 'x', 0.0) - getattr(a, 'x', 0.0)
                dy = getattr(b, 'y', 0.0) - getattr(a, 'y', 0.0)
                length = (dx * dx + dy * dy) ** 0.5
                total_length += length
                
        return {
            "device_count": len(devices),
            "wire_count": len(wires),
            "total_wire_length": total_length,
            "device_types": device_types,
            "circuit_type": circuit["type"]
        }
        
    def validate_circuit_connections(self, circuit_id: int) -> dict:
        """Validate connections on a circuit."""
        if circuit_id not in self.circuits:
            return {}
            
        devices = self.circuits[circuit_id]["devices"]
        disconnected_devices = []
        partially_connected_devices = []
        connected_devices = []
        
        for device in devices:
            if hasattr(device, 'connection_status'):
                status = device.connection_status
                if status == "disconnected":
                    disconnected_devices.append(device)
                elif status == "partial":
                    partially_connected_devices.append(device)
                else:  # connected
                    connected_devices.append(device)
            else:
                # Default to disconnected if no status
                disconnected_devices.append(device)
                
        return {
            "total_devices": len(devices),
            "connected": len(connected_devices),
            "partially_connected": len(partially_connected_devices),
            "disconnected": len(disconnected_devices),
            "issues": len(disconnected_devices) + len(partially_connected_devices)
        }