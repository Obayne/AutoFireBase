from PySide6 import QtCore, QtGui, QtWidgets
from app.device import DeviceItem


class WireTool:
    def __init__(self, win, layer, connections_tree):
        self.win = win
        self.layer = layer
        self.connections_tree = connections_tree
        self.active = False
        self.points = []
        self.wire_type = None
        self.circuit_type = None  # New attribute for circuit type

    def set_wire_type(self, wire_type):
        self.wire_type = wire_type

    def set_circuit_type(self, circuit_type):
        self.circuit_type = circuit_type
        self.wire_type = wire_type

    def start(self):
        self.active = True
        self.points = []
        self.win.statusBar().showMessage("Wire Tool: Click to place points, press Esc to finish.")

    def cancel(self):
        self.active = False
        self.points = []

    def on_click(self, p: QtCore.QPointF, shift_ortho: bool = False):
        self.points.append(p)

        # Identify the device at the clicked point
        clicked_item = self.win.scene.itemAt(p, self.win.view.transform())
        if isinstance(clicked_item, DeviceItem):
            self.points[-1] = clicked_item  # Store the device item instead of just the point

        if len(self.points) >= 2:
            self.finish()
            return True
        return False

    def on_mouse_move(self, p: QtCore.QPointF, shift_ortho: bool = False):
        pass

    def finish(self):
        if len(self.points) >= 2:
            start_device = self.points[0] if isinstance(self.points[0], DeviceItem) else None
            end_device = self.points[1] if isinstance(self.points[1], DeviceItem) else None

            if not start_device or not end_device:
                self.win.statusBar().showMessage(
                    "Wire Tool: Please click on two devices to connect."
                )
                self.cancel()
                return

            if not self._check_compatibility(start_device, end_device):
                self.win.statusBar().showMessage("Wire Tool: Incompatible devices or circuit type.")
                self.cancel()
                return

            line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(start_device.pos(), end_device.pos()))
            color = self.wire_type["color"] if self.wire_type else "red"
            pen = QtGui.QPen(QtGui.QColor(color), 2)
            line.setPen(pen)
            line.setParentItem(self.layer)

            # Add to connections tree
            self.connections_tree.add_device_to_panel(
                start_device.name, end_device.name, f"Wire: {self.wire_type['part_number']}"
            )

        self.cancel()

    def _check_compatibility(self, start_device: DeviceItem, end_device: DeviceItem) -> bool:
        # Basic compatibility check (can be expanded)
        if not self.circuit_type:
            self.win.statusBar().showMessage("Wire Tool: Please select a circuit type (SLC/NAC).")
            return False

        if self.circuit_type == "SLC":
            # Both devices must be SLC compatible
            if not getattr(start_device, "slc_compatible", False) or not getattr(
                end_device, "slc_compatible", False
            ):
                self.win.statusBar().showMessage("Wire Tool: Both devices must be SLC compatible.")
                return False
        elif self.circuit_type == "NAC":
            # Both devices must be NAC compatible
            if not getattr(start_device, "nac_compatible", False) or not getattr(
                end_device, "nac_compatible", False
            ):
                self.win.statusBar().showMessage("Wire Tool: Both devices must be NAC compatible.")
                return False

        return True
