"""
Visual Wire System for Fire Alarm Circuits
Displays actual wire connections with proper color coding and routing.
"""

from PySide6 import QtCore, QtGui, QtWidgets


class CircuitWire(QtWidgets.QGraphicsLineItem):
    """Visual representation of a wire connection between devices."""

    def __init__(self, from_device, to_device, circuit_type):
        super().__init__()

        self.from_device = from_device
        self.to_device = to_device
        self.circuit_type = circuit_type

        # Set visual properties based on circuit type
        self._setup_wire_appearance()

        # Make wires selectable but not movable
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(5)  # Below devices but above background

        # Update wire path
        self.update_path()

    def _setup_wire_appearance(self):
        """Set wire color and style based on circuit type."""
        pen = QtGui.QPen()
        pen.setCosmetic(True)
        pen.setWidth(3)

        # Color coding for fire alarm circuits
        if self.circuit_type == "NAC":
            pen.setColor(QtGui.QColor(220, 20, 20))  # Red for NAC
            pen.setStyle(QtCore.Qt.SolidLine)
        elif self.circuit_type == "SLC":
            pen.setColor(QtGui.QColor(20, 20, 220))  # Blue for SLC
            pen.setStyle(QtCore.Qt.SolidLine)
        elif self.circuit_type == "POWER":
            pen.setColor(QtGui.QColor(20, 20, 20))  # Black for Power
            pen.setStyle(QtCore.Qt.SolidLine)
        else:
            pen.setColor(QtGui.QColor(128, 128, 128))  # Gray for unknown
            pen.setStyle(QtCore.Qt.DashLine)

        self.setPen(pen)

    def update_path(self):
        """Update the wire path between connected devices."""
        if not self.from_device or not self.to_device:
            return

        # Get device positions
        from_pos = self.from_device.scenePos()
        to_pos = self.to_device.scenePos()

        # Simple direct connection for now
        # TODO: Add intelligent routing around obstacles
        self.setLine(from_pos.x(), from_pos.y(), to_pos.x(), to_pos.y())

    def get_wire_info(self):
        """Get information about this wire connection."""
        return {
            "from": getattr(self.from_device, "name", "Unknown"),
            "to": getattr(self.to_device, "name", "Unknown"),
            "circuit_type": self.circuit_type,
            "length_ft": self.get_length_ft(),
        }

    def get_length_ft(self):
        """Calculate wire length in feet."""
        line = self.line()
        length_px = (line.dx() ** 2 + line.dy() ** 2) ** 0.5
        # Convert pixels to feet (assuming 12 px per foot)
        return length_px / 12.0


class CircuitManager:
    """Manages all circuit connections and wire routing."""

    def __init__(self, scene):
        self.scene = scene
        self.wires = []
        self.panels = []

    def add_panel(self, panel):
        """Add a fire alarm panel to the system."""
        self.panels.append(panel)

    def remove_panel(self, panel):
        """Remove a fire alarm panel from the system."""
        if panel in self.panels:
            self.panels.remove(panel)

    def get_main_panel(self):
        """Get the main fire alarm control panel."""
        for panel in self.panels:
            if getattr(panel, "panel_type", "") == "main":
                return panel
        return None

    def connect_devices(self, device1, device2, circuit_type=None):
        """Create a wire connection between two devices."""
        main_panel = self.get_main_panel()
        if not main_panel:
            return False, "No main panel found. Add a Fire Alarm Control Panel first."

        # Determine circuit type if not specified
        if not circuit_type:
            circuit_type = main_panel.get_circuit_for_device_type(device1.device_type)

        if not circuit_type:
            return False, f"Cannot determine circuit type for {device1.name}"

        # Validate both devices can be on this circuit type
        if not main_panel.validate_device_placement(device1, f"{circuit_type}1"):
            return False, f"{device1.name} cannot be placed on {circuit_type} circuit"

        if not main_panel.validate_device_placement(device2, f"{circuit_type}1"):
            return False, f"{device2.name} cannot be placed on {circuit_type} circuit"

        # Create visual wire
        wire = CircuitWire(device1, device2, circuit_type)
        self.wires.append(wire)
        self.scene.addItem(wire)

        # Connect devices to panel
        available_circuit = main_panel.get_available_circuit(device1)
        if available_circuit:
            device1.connect_to_panel(main_panel, available_circuit)
            device2.connect_to_panel(main_panel, available_circuit)

        return True, f"Connected via {circuit_type} circuit"

    def disconnect_devices(self, device1, device2):
        """Remove wire connection between two devices."""
        wires_to_remove = []

        for wire in self.wires:
            if (wire.from_device == device1 and wire.to_device == device2) or (
                wire.from_device == device2 and wire.to_device == device1
            ):
                wires_to_remove.append(wire)

        for wire in wires_to_remove:
            self.scene.removeItem(wire)
            self.wires.remove(wire)

        # Update device connection status
        device1.set_connection_status("unconnected")
        device2.set_connection_status("unconnected")

        return len(wires_to_remove) > 0

    def update_all_wire_paths(self):
        """Update all wire paths (call when devices move)."""
        for wire in self.wires:
            wire.update_path()

    def get_circuit_status(self):
        """Get status of all circuits in the system."""
        main_panel = self.get_main_panel()
        if not main_panel:
            return {"error": "No main panel found"}

        status = {}
        for circuit_id, circuit in main_panel.circuits.items():
            status[circuit_id] = {
                "type": circuit["type"],
                "device_count": len(circuit["devices"]),
                "status": circuit["status"],
                "devices": [device.name for device in circuit["devices"]],
            }

        return status

    def validate_system_integrity(self):
        """Check for system integrity issues."""
        issues = []
        main_panel = self.get_main_panel()

        if not main_panel:
            issues.append("No main fire alarm control panel found")
            return issues

        # Check for unconnected devices
        all_devices = [
            item
            for item in self.scene.items()
            if hasattr(item, "device_type") and item != main_panel
        ]

        unconnected_devices = [
            device for device in all_devices if device.connection_status == "unconnected"
        ]

        if unconnected_devices:
            issues.append(f"{len(unconnected_devices)} devices are not connected to any circuit")

        # Check for circuit overloads
        for circuit_id, circuit in main_panel.circuits.items():
            if len(circuit["devices"]) > 20:  # Typical circuit limit
                issues.append(
                    f"Circuit {circuit_id} has {len(circuit['devices'])} devices (limit: 20)"
                )

        return issues
