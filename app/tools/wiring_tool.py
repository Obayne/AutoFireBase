import math

from PySide6 import QtCore

from app.tools.draw import DrawMode


class ElectricalCircuit:
    """Represents an electrical circuit with devices and wiring."""

    def __init__(self, circuit_id: str, voltage: float = 24.0):
        self.circuit_id = circuit_id
        self.voltage = voltage
        self.devices = []  # List of (device_item, position) tuples
        self.wire_length = 0.0  # Total wire length in feet
        self.wire_gauge = 18  # AWG gauge
        self.current_draw = 0.0  # Total current in amps

    def add_device(self, device_item, position: QtCore.QPointF):
        """Add a device to this circuit."""
        self.devices.append((device_item, position))

        # Set circuit connection on the device
        if hasattr(device_item, 'set_circuit'):
            device_item.set_circuit(self.circuit_id)

        # Estimate current draw based on device type
        device_name = getattr(device_item, "name", "").lower()
        if "smoke" in device_name or "heat" in device_name:
            self.current_draw += 0.02  # Typical detector current
        elif "strobe" in device_name or "horn" in device_name:
            self.current_draw += 0.15  # Typical notification appliance
        elif "speaker" in device_name:
            self.current_draw += 0.20  # Typical speaker
        else:
            self.current_draw += 0.05  # Default

    def calculate_voltage_drop(self) -> float:
        """Calculate voltage drop for this circuit."""
        # Simplified voltage drop calculation
        # Vdrop = I * R, where R = (2 * L * ρ) / A
        # ρ = resistivity of copper (10.4 ohm-circular-mils/ft)
        # A = cross-sectional area in circular mils

        resistivity = 10.4  # ohm-circular-mils/ft for copper
        gauge_areas = {
            18: 1620,  # circular mils
            16: 2580,
            14: 4110,
            12: 6530,
        }

        area = gauge_areas.get(self.wire_gauge, 1620)  # Default to 18 AWG
        resistance_per_ft = (2 * resistivity) / area  # Round trip resistance

        voltage_drop = self.current_draw * self.wire_length * resistance_per_ft
        return voltage_drop

    def get_status(self) -> str:
        """Get circuit status summary."""
        voltage_drop = self.calculate_voltage_drop()
        voltage_at_end = self.voltage - voltage_drop

        status = f"Circuit {self.circuit_id}: {len(self.devices)} devices, "
        status += f"{self.current_draw:.2f}A, {self.wire_length:.1f}ft wire, "
        status += f"{voltage_drop:.2f}V drop ({voltage_at_end:.1f}V at end)"

        if voltage_at_end < 20.0:  # NFPA 72 minimum
            status += " ⚠️ LOW VOLTAGE"
        elif voltage_drop > self.voltage * 0.1:  # More than 10% drop
            status += " ⚠️ HIGH DROP"

        return status


class WiringTool:
    def __init__(self, window):
        self.win = window
        self.active = False
        self.circuits = {}  # circuit_id -> ElectricalCircuit
        self.current_circuit = None
        self.wire_start_device = None
        self.wire_segments = []  # List of wire segments for current circuit

    def start(self):
        """Start the wiring tool."""
        self.active = True
        self.win.draw.set_mode(DrawMode.WIRE)
        self.win.statusBar().showMessage(
            "Wiring: click device to start circuit, click to route wire, right-click to finish circuit"
        )

    def cancel(self):
        """Cancel the wiring operation."""
        self.active = False
        self.wire_start_device = None
        self.wire_segments = []
        if hasattr(self.win, "draw"):
            self.win.draw.finish()

    def on_mouse_move(self, p: QtCore.QPointF):
        """Handle mouse movement during wiring."""
        if hasattr(self.win, "draw"):
            self.win.draw.on_mouse_move(p, shift_ortho=False)

    def on_click(self, p: QtCore.QPointF):
        """Handle mouse click during wiring."""
        if not self.active:
            return False

        # Check if clicking on a device
        device_item = self._get_device_at_position(p)
        if device_item:
            return self._handle_device_click(device_item, p)
        else:
            return self._handle_wire_routing(p)

    def _get_device_at_position(self, pos: QtCore.QPointF):
        """Get device item at the given position."""
        if not hasattr(self.win, "scene"):
            return None

        items = self.win.scene.items(pos)
        for item in items:
            if hasattr(item, "name") and hasattr(item, "symbol"):  # DeviceItem
                return item
        return None

    def _handle_device_click(self, device_item, pos: QtCore.QPointF):
        """Handle clicking on a device."""
        if self.wire_start_device is None:
            # Start new circuit
            self.wire_start_device = device_item
            circuit_id = f"Circuit_{len(self.circuits) + 1}"
            self.current_circuit = ElectricalCircuit(circuit_id)
            if self.current_circuit:
                self.current_circuit.add_device(device_item, pos)
            self.wire_segments = []

            self.win.statusBar().showMessage(
                f"Started {circuit_id} at {getattr(device_item, 'name', 'device')}. Click to route wire or right-click device to finish."
            )
            return False
        else:
            # Finish circuit at this device
            if device_item != self.wire_start_device:  # Don't connect to self
                if self.current_circuit:
                    self.current_circuit.add_device(device_item, pos)
                self._finalize_circuit()
                return True
            else:
                # Same device - finish circuit
                self._finalize_circuit()
                return True

    def _handle_wire_routing(self, pos: QtCore.QPointF):
        """Handle wire routing click."""
        if self.wire_start_device is None:
            self.win.statusBar().showMessage("Click on a device first to start a circuit.")
            return False

        # Add wire segment
        if hasattr(self.win, "draw") and self.current_circuit:
            result = self.win.draw.on_click(pos, shift_ortho=False)
            if result:
                # Wire segment was completed
                # Calculate segment length (simplified - just add to total)
                if len(self.wire_segments) > 0:
                    last_pos = self.wire_segments[-1]
                    segment_length = math.sqrt(
                        (pos.x() - last_pos.x()) ** 2 + (pos.y() - last_pos.y()) ** 2
                    )
                    # Convert pixels to feet (assuming 1 unit = 1 foot for now)
                    segment_length_feet = segment_length / 12  # Rough conversion
                    self.current_circuit.wire_length += segment_length_feet

                self.wire_segments.append(pos)
                self.win.statusBar().showMessage(
                    f"Wire segment added. Total length: {self.current_circuit.wire_length:.1f}ft. Right-click device to finish circuit."
                )
            return result

        return False

    def _finalize_circuit(self):
        """Finalize the current circuit."""
        if self.current_circuit:
            self.circuits[self.current_circuit.circuit_id] = self.current_circuit

            # Update system info palette if available
            if hasattr(self.win, "app_controller") and hasattr(
                self.win.app_controller, "system_info_palette"
            ):
                self.win.app_controller.system_info_palette._update_circuit_info()

            status = self.current_circuit.get_status()
            self.win.statusBar().showMessage(f"Circuit completed: {status}")

            # Reset for next circuit
            self.wire_start_device = None
            self.current_circuit = None
            self.wire_segments = []

    def get_circuit_summary(self) -> str:
        """Get summary of all circuits."""
        if not self.circuits:
            return "No circuits defined."

        summary = f"Circuit Summary ({len(self.circuits)} circuits):\n\n"
        total_current = 0.0
        total_length = 0.0

        for circuit in self.circuits.values():
            summary += f"• {circuit.get_status()}\n"
            total_current += circuit.current_draw
            total_length += circuit.wire_length

        summary += f"\nTotals: {total_current:.2f}A total current, {total_length:.1f}ft total wire"
        return summary
