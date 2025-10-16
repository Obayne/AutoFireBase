"""
Fire Alarm Control Panel - Main power and control source for all circuits
"""

from PySide6 import QtCore, QtGui, QtWidgets

from frontend.device import DeviceItem


class FireAlarmPanel(DeviceItem):
    """Main fire alarm control panel - the heart of the system."""

    def __init__(self, x, y, symbol=None, name=None, manufacturer=None, part_number=None):
        # Initialize as a special device with provided or default values
        super().__init__(
            x,
            y,
            symbol=symbol or "■",
            name=name or "Fire Alarm Control Panel",
            manufacturer=manufacturer or "System",
            part_number=part_number or "MAIN-PANEL",
        )

        # Panel-specific properties
        self.panel_type = "main"
        self.circuits = {
            "NAC1": {"type": "NAC", "devices": [], "status": "ready"},
            "NAC2": {"type": "NAC", "devices": [], "status": "ready"},
            "SLC1": {"type": "SLC", "devices": [], "status": "ready"},
            "SLC2": {"type": "SLC", "devices": [], "status": "ready"},
            "POWER": {"type": "POWER", "devices": [], "status": "ready"},
        }

        # Override the base device appearance for panel
        self._setup_panel_appearance()

    def _setup_panel_appearance(self):
        """Customize panel appearance to look like a control panel."""
        # Remove the default glyph only if we have a scene
        if self.scene() and hasattr(self, "_glyph") and self._glyph:
            self.scene().removeItem(self._glyph)

        # Panel body
        self._panel_body = QtWidgets.QGraphicsRectItem(-30, -20, 60, 40)
        panel_pen = QtGui.QPen(QtGui.QColor("#0078d4"))
        panel_pen.setCosmetic(True)
        panel_pen.setWidth(2)
        self._panel_body.setPen(panel_pen)
        self._panel_body.setBrush(QtGui.QColor("#1e1e1e"))
        self.addToGroup(self._panel_body)

        # Circuit terminals (visual connection points)
        self._terminals = {}
        positions = [
            ("NAC1", -25, -10),
            ("NAC2", -25, 10),
            ("SLC1", 25, -10),
            ("SLC2", 25, 10),
            ("POWER", 0, -15),
        ]

        for circuit_id, x_offset, y_offset in positions:
            terminal = QtWidgets.QGraphicsEllipseItem(-3, -3, 6, 6)
            terminal.setPos(x_offset, y_offset)

            # Color code terminals
            if circuit_id.startswith("NAC"):
                color = QtGui.QColor(255, 0, 0)  # Red for NAC
            elif circuit_id.startswith("SLC"):
                color = QtGui.QColor(0, 0, 255)  # Blue for SLC
            else:
                color = QtGui.QColor(0, 0, 0)  # Black for Power

            terminal_pen = QtGui.QPen(color)
            terminal_pen.setCosmetic(True)
            terminal_pen.setWidth(2)
            terminal.setPen(terminal_pen)
            terminal.setBrush(color)

            # Tag terminal with its circuit id and back-reference to this panel
            terminal.circuit_id = circuit_id  # type: ignore[attr-defined]
            terminal.panel_ref = self  # type: ignore[attr-defined]
            self.addToGroup(terminal)
            self._terminals[circuit_id] = terminal

        # Update label to show it's the main panel
        self._label.setText("FACP")
        self._label.setPos(QtCore.QPointF(0, 25))

    def add_device_to_circuit(self, device, circuit_id):
        """Add a device to a specific circuit."""
        if circuit_id in self.circuits:
            self.circuits[circuit_id]["devices"].append(device)
            device.circuit_id = circuit_id
            device.panel = self
            self._update_circuit_status(circuit_id)

    def remove_device_from_circuit(self, device, circuit_id):
        """Remove a device from a circuit."""
        if circuit_id in self.circuits and device in self.circuits[circuit_id]["devices"]:
            self.circuits[circuit_id]["devices"].remove(device)
            device.circuit_id = None
            device.panel = None
            self._update_circuit_status(circuit_id)

    def _update_circuit_status(self, circuit_id):
        """Update circuit status based on connected devices."""
        circuit = self.circuits[circuit_id]
        device_count = len(circuit["devices"])

        if device_count == 0:
            circuit["status"] = "ready"
        else:
            # Check if all devices in circuit are properly connected
            all_connected = all(
                hasattr(device, "connection_status") and device.connection_status == "connected"
                for device in circuit["devices"]
            )
            circuit["status"] = "connected" if all_connected else "partial"

    def get_circuit_for_device_type(self, device_type):
        """Determine which circuit type a device should connect to."""
        device_type = device_type.lower()

        # Initiating devices go on SLC (Signaling Line Circuit)
        if any(keyword in device_type for keyword in ["detector", "pull", "switch", "monitor"]):
            return "SLC"

        # Notification devices go on NAC (Notification Appliance Circuit)
        elif any(
            keyword in device_type for keyword in ["strobe", "horn", "speaker", "bell", "siren"]
        ):
            return "NAC"

        # Power devices
        elif any(keyword in device_type for keyword in ["power", "supply", "battery"]):
            return "POWER"

        return None  # Unknown device type

    def validate_device_placement(self, device, circuit_id):
        """Validate if a device can be placed on a specific circuit."""
        circuit_type = self.circuits[circuit_id]["type"]
        device_type = getattr(device, "device_type", getattr(device, "name", "")).lower()

        # NAC circuits: only notification devices
        if circuit_type == "NAC":
            return any(
                keyword in device_type for keyword in ["strobe", "horn", "speaker", "bell", "siren"]
            )

        # SLC circuits: only initiating devices
        elif circuit_type == "SLC":
            return any(
                keyword in device_type for keyword in ["detector", "pull", "switch", "monitor"]
            )

        # Power circuits: power devices
        elif circuit_type == "POWER":
            return any(keyword in device_type for keyword in ["power", "supply", "battery"])

        return False

    def get_available_circuit(self, device):
        """Get the next available circuit for a device type."""
        required_circuit_type = self.get_circuit_for_device_type(
            getattr(device, "device_type", getattr(device, "name", ""))
        )

        if not required_circuit_type:
            return None

        # Find circuits of the required type with capacity
        available_circuits = [
            circuit_id
            for circuit_id, circuit in self.circuits.items()
            if circuit["type"] == required_circuit_type
            and len(circuit["devices"]) < 20  # Max 20 devices per circuit
        ]

        return available_circuits[0] if available_circuits else None
