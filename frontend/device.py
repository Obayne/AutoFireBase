from PySide6 import QtCore, QtGui, QtWidgets


class DeviceItem(QtWidgets.QGraphicsItemGroup):
    """Device glyph + label + optional coverage overlays (strobe/speaker/smoke)."""

    Type = QtWidgets.QGraphicsItem.UserType + 101

    def type(self):
        return DeviceItem.Type

    def __init__(self, x, y, symbol, name, manufacturer="", part_number="", layer=None):
        super().__init__()
        self.setFlags(
            QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable
        )
        self.symbol = symbol
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number
        # Optional layer metadata (may be dict or simple id)
        self.layer = layer

        # Base glyph
        self._glyph = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
        pen = QtGui.QPen(QtGui.QColor("#D8D8D8"))
        pen.setCosmetic(True)
        self._glyph.setPen(pen)
        self._glyph.setBrush(QtGui.QColor("#20252B"))
        self._glyph.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self._glyph.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.addToGroup(self._glyph)

        # Label
        self._label = QtWidgets.QGraphicsSimpleTextItem(self.name)
        self._label.setBrush(QtGui.QBrush(QtGui.QColor("#EAEAEA")))
        self._label.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self._label.setPos(QtCore.QPointF(12, -14))
        # Track label offset in scene pixels relative to device origin
        self.label_offset = QtCore.QPointF(self._label.pos())
        self._label.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self._label.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.addToGroup(self._label)

        # Selection halo
        self._halo = QtWidgets.QGraphicsEllipseItem(-9, -9, 18, 18)
        halo_pen = QtGui.QPen(QtGui.QColor(60, 180, 255, 220))
        halo_pen.setCosmetic(True)
        halo_pen.setWidthF(1.4)
        self._halo.setPen(halo_pen)
        self._halo.setBrush(QtCore.Qt.NoBrush)
        self._halo.setZValue(-1)
        self._halo.setVisible(False)
        self.addToGroup(self._halo)

        # Coverage overlays
        self.coverage = {
            "mode": "none",
            "mount": "ceiling",
            "params": {},  # mode-specific inputs
            "computed_radius_ft": 0.0,
            "px_per_ft": 12.0,
        }
        self.coverage_enabled = True
        self._cov_circle = QtWidgets.QGraphicsEllipseItem()
        self._cov_circle.setZValue(-10)
        self._cov_circle.setVisible(False)
        self._cov_circle.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self._cov_circle.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self._cov_circle.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        cpen = QtGui.QPen(QtGui.QColor(80, 170, 255, 200))
        cpen.setCosmetic(True)
        cpen.setStyle(QtCore.Qt.DashLine)
        self._cov_circle.setPen(cpen)
        self._cov_circle.setBrush(QtGui.QColor(80, 170, 255, 40))
        self.addToGroup(self._cov_circle)

        self._cov_square = QtWidgets.QGraphicsRectItem()
        self._cov_square.setZValue(-11)
        self._cov_square.setVisible(False)
        self._cov_square.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self._cov_square.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self._cov_square.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        spen = QtGui.QPen(QtGui.QColor(80, 170, 255, 140))
        spen.setCosmetic(True)
        spen.setStyle(QtCore.Qt.DotLine)
        self._cov_square.setPen(spen)
        self._cov_square.setBrush(QtGui.QColor(80, 170, 255, 25))
        self.addToGroup(self._cov_square)

        # Connection status indicator
        self.connection_status = "unconnected"  # "unconnected", "connected", "partial"
        self._connection_indicator = QtWidgets.QGraphicsEllipseItem(-3, -3, 6, 6)
        self._connection_indicator.setZValue(10)  # Above everything else
        self._connection_indicator.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self._connection_indicator.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self._connection_indicator.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        # Start with unconnected styling (brighter orange dot)
        conn_pen = QtGui.QPen(QtGui.QColor(255, 140, 0, 255))  # Brighter orange
        conn_pen.setCosmetic(True)
        conn_pen.setWidth(2)  # Thicker border
        self._connection_indicator.setPen(conn_pen)
        self._connection_indicator.setBrush(QtGui.QColor(255, 140, 0, 180))  # More opaque

        # Position in top-right corner of device
        self._connection_indicator.setPos(8, -8)
        self.addToGroup(self._connection_indicator)

        # Fire alarm circuit properties
        self.circuit_id = None  # Which circuit this device is on (NAC1, SLC1, etc.)
        self.panel = None  # Reference to the main fire alarm panel
        self.device_type = name  # Store device type for circuit validation

        # Timer for blinking effect on unconnected devices
        self._blink_timer = QtCore.QTimer()
        self._blink_timer.timeout.connect(self._blink_connection_indicator)
        self._blink_visible = True
        self._start_blink_timer()

        self.setPos(x, y)

    # ---- selection visual
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            sel = bool(value)
            self._halo.setVisible(sel)
        return super().itemChange(change, value)

    def set_label_text(self, text: str):
        self._label.setText(text)

    def set_label_offset(self, dx_px: float, dy_px: float):
        try:
            self.label_offset = QtCore.QPointF(float(dx_px), float(dy_px))
            self._label.setPos(self.label_offset)
        except Exception:
            pass

    # ---- connection status ----
    def set_connection_status(self, status: str):
        """Set connection status: 'unconnected', 'connected', 'partial'."""
        self.connection_status = status
        self._update_connection_indicator()

    def _update_connection_indicator(self):
        """Update the visual appearance of the connection indicator."""
        if self.connection_status == "connected":
            # Bright green for connected
            pen = QtGui.QPen(QtGui.QColor(0, 255, 0, 255))
            brush = QtGui.QColor(0, 255, 0, 200)
            self._blink_timer.stop()
            self._connection_indicator.setVisible(True)
        elif self.connection_status == "partial":
            # Bright yellow for partially connected
            pen = QtGui.QPen(QtGui.QColor(255, 255, 0, 255))
            brush = QtGui.QColor(255, 255, 0, 200)
            self._blink_timer.stop()
            self._connection_indicator.setVisible(True)
        else:  # unconnected
            # Brighter orange for unconnected with blinking
            pen = QtGui.QPen(QtGui.QColor(255, 140, 0, 255))
            brush = QtGui.QColor(255, 140, 0, 180)
            self._start_blink_timer()

        pen.setCosmetic(True)
        pen.setWidth(2)  # Thicker border for better visibility
        self._connection_indicator.setPen(pen)
        self._connection_indicator.setBrush(brush)

    def _start_blink_timer(self):
        """Start the blinking timer for unconnected devices."""
        if self.connection_status == "unconnected":
            self._blink_timer.start(1000)  # Blink every 1 second

    def _blink_connection_indicator(self):
        """Toggle visibility of connection indicator for blinking effect."""
        if self.connection_status == "unconnected":
            self._blink_visible = not self._blink_visible
            self._connection_indicator.setVisible(self._blink_visible)

    # ---- fire alarm circuit API ----
    def connect_to_panel(self, panel, circuit_id=None):
        """Connect this device to a fire alarm panel on a specific circuit."""
        if not circuit_id:
            # Auto-determine circuit based on device type
            circuit_id = panel.get_available_circuit(self)

        if not circuit_id:
            return False, "No suitable circuit available"

        if not panel.validate_device_placement(self, circuit_id):
            return False, f"Device type '{self.device_type}' cannot connect to {circuit_id}"

        # Remove from previous circuit if connected
        if self.panel and self.circuit_id:
            self.panel.remove_device_from_circuit(self, self.circuit_id)

        # Connect to new circuit
        panel.add_device_to_circuit(self, circuit_id)
        self.set_connection_status("connected")

        return True, f"Connected to {circuit_id}"

    def disconnect_from_panel(self):
        """Disconnect this device from its current panel/circuit."""
        if self.panel and self.circuit_id:
            self.panel.remove_device_from_circuit(self, self.circuit_id)
            self.set_connection_status("unconnected")
            return True
        return False

    def get_circuit_info(self):
        """Get information about the circuit this device is connected to."""
        if not self.panel or not self.circuit_id:
            return None

        circuit = self.panel.circuits.get(self.circuit_id)
        if circuit:
            return {
                "circuit_id": self.circuit_id,
                "circuit_type": circuit["type"],
                "status": circuit["status"],
                "device_count": len(circuit["devices"]),
                "panel_name": self.panel.name,
            }
        return None

    # ---- coverage API
    def set_coverage(self, cfg: dict):
        if not cfg:
            return
        self.coverage.update(cfg)
        self._update_coverage_items()

    def _update_coverage_items(self):
        if not self.coverage_enabled:
            self._cov_circle.setVisible(False)
            self._cov_square.setVisible(False)
            return

        source = self.coverage.get("source", "manual")
        if source == "manual":
            color = QtGui.QColor(255, 193, 7, 200)  # Yellow/Amber
            brush_color = QtGui.QColor(255, 193, 7, 40)
        else:  # auto
            color = QtGui.QColor(80, 170, 255, 200)  # Blue
            brush_color = QtGui.QColor(80, 170, 255, 40)

        cpen = self._cov_circle.pen()
        cpen.setColor(color)
        self._cov_circle.setPen(cpen)
        self._cov_circle.setBrush(brush_color)

        spen = self._cov_square.pen()
        spen.setColor(color)
        self._cov_square.setPen(spen)
        self._cov_square.setBrush(brush_color)

        mode = self.coverage.get("mode", "none")
        r_ft = float(self.coverage.get("computed_radius_ft") or 0.0)
        ppf = float(self.coverage.get("px_per_ft") or 12.0)
        r_px = r_ft * ppf

        # hide all
        self._cov_circle.setVisible(False)
        self._cov_square.setVisible(False)
        if mode == "none" or r_px <= 0:
            return

        # circle always
        self._cov_circle.setRect(-r_px, -r_px, 2 * r_px, 2 * r_px)
        self._cov_circle.setVisible(True)

        # if strobe + ceiling: show square footprint
        if mode == "strobe" and self.coverage.get("mount", "ceiling") == "ceiling":
            side = 2 * r_px
            self._cov_square.setRect(-side / 2, -side / 2, side, side)
            self._cov_square.setVisible(True)

    def set_coverage_enabled(self, on: bool):
        self.coverage_enabled = bool(on)
        self._update_coverage_items()

    # ---- serialization
    def to_json(self):
        return {
            "x": float(self.pos().x()),
            "y": float(self.pos().y()),
            "symbol": self.symbol,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "part_number": self.part_number,
            "coverage": self.coverage,
            "show_coverage": bool(getattr(self, "coverage_enabled", True)),
        }

    @staticmethod
    def from_json(d: dict):
        it = DeviceItem(
            float(d.get("x", 0)),
            float(d.get("y", 0)),
            d.get("symbol", "?"),
            d.get("name", "Device"),
            d.get("manufacturer", ""),
            d.get("part_number", ""),
        )
        cov = d.get("coverage")
        if cov:
            it.set_coverage(cov)
        it.set_coverage_enabled(bool(d.get("show_coverage", True)))
        return it
