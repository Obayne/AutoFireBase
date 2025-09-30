from PySide6 import QtCore, QtGui, QtWidgets


class DeviceItem(QtWidgets.QGraphicsItemGroup):
    """Device glyph + label + optional coverage overlays (strobe/speaker/smoke)."""

    Type = QtWidgets.QGraphicsItem.UserType + 101

    def type(self):
        return DeviceItem.Type

    def __init__(self, x, y, symbol, name, manufacturer="", part_number="", layer=None, device_type=None, properties=None):
        super().__init__()
        self.setFlags(
            QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable
        )
        self.symbol = symbol
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number
        self.device_type = device_type
        self.properties = properties or {}
        if isinstance(self.properties, str):
            import json
            try:
                self.properties = json.loads(self.properties)
            except:
                self.properties = {}
        # Optional layer metadata (may be dict or simple id)
        self.layer = layer

        # Check if this is an NFPA 170 symbol
        self.is_nfpa_symbol = device_type == "NFPA 170"

        if self.is_nfpa_symbol:
            # For NFPA symbols, use a larger text display instead of small glyph
            self._glyph = QtWidgets.QGraphicsSimpleTextItem(self.symbol)
            font = self._glyph.font()
            # Get minimum size from properties (default 6 inches)
            min_inches = self.properties.get("min_size_inches", 6)
            # For now, use a fixed pixel size - in future this could be scaled by px_per_ft
            # Assuming 96 px/ft (1/8" scale), convert inches to pixels
            font_size_px = max(12, min_inches * 8)  # Rough approximation
            font.setPointSizeF(font_size_px)
            font.setBold(True)
            self._glyph.setFont(font)
            # Use color from properties or default to red for NFPA symbols
            color_name = self.properties.get("color", "red")
            if color_name == "red":
                color = QtGui.QColor("#FF0000")
            elif color_name == "green":
                color = QtGui.QColor("#00FF00")
            else:
                color = QtGui.QColor("#FF0000")  # Default red
            self._glyph.setBrush(QtGui.QBrush(color))
            self._glyph.setAcceptedMouseButtons(QtCore.Qt.NoButton)
            self._glyph.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
            # Center the text
            self._glyph.setPos(-self._glyph.boundingRect().width()/2, -self._glyph.boundingRect().height()/2)
            self.addToGroup(self._glyph)
        else:
            # Base glyph - enhanced for underlay visibility
            self._glyph = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
            # Use a more prominent border for better visibility on underlays
            pen = QtGui.QPen(QtGui.QColor("#FFFFFF"))  # White border
            pen.setCosmetic(True)
            pen.setWidthF(2.0)  # Thicker border
            self._glyph.setPen(pen)
            self._glyph.setBrush(QtGui.QColor("#20252B"))
            self._glyph.setAcceptedMouseButtons(QtCore.Qt.NoButton)
            self._glyph.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
            self.addToGroup(self._glyph)

        # Label background for underlay visibility
        self._label_bg = QtWidgets.QGraphicsRectItem()
        self._label_bg.setBrush(QtGui.QBrush(QtGui.QColor("#FFFFFF")))  # White background
        self._label_bg.setPen(QtGui.QPen(QtGui.QColor("#000000")))  # Black border
        self._label_bg.setZValue(-2)  # Behind label
        self._label_bg.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self._label_bg.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self._label_bg.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.addToGroup(self._label_bg)

        # Label - enhanced for underlay visibility
        self._label = QtWidgets.QGraphicsSimpleTextItem(self.name)
        # Use darker text with white outline for better contrast on underlays
        self._label.setBrush(QtGui.QBrush(QtGui.QColor("#000000")))  # Black text
        # Add white outline for visibility
        font = self._label.font()
        font.setBold(True)
        self._label.setFont(font)
        self._label.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self._label.setPos(QtCore.QPointF(12, -14))
        # Track label offset in scene pixels relative to device origin
        self.label_offset = QtCore.QPointF(self._label.pos())
        self._label.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self._label.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.addToGroup(self._label)

        # Initialize label background
        self.set_label_text(self.name)

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

        # Electrical properties for circuit connections
        self.electrical = {
            "terminals": [],  # List of terminal positions relative to device center
            "current_standby_a": 0.02,  # Standby current in amps
            "current_alarm_a": 0.15,  # Alarm current in amps
            "voltage_v": 24.0,  # Operating voltage
            "power_w": 0.0,  # Power consumption in watts
            "wire_gauge": 18,  # Recommended wire gauge
            "connection_type": "screw",  # screw, push, crimp, etc.
        }

        # Circuit connection properties
        self.circuit_id = None  # Circuit ID when connected (e.g., "C1", "Circuit_1")
        self.circuit_badge = None  # Visual badge showing circuit ID

        # Initialize default terminals based on device type
        self._init_terminals()

        # Terminal connection points (visual)
        self._terminal_points = []
        self._update_terminal_visuals()

        self.setPos(x, y)

    # ---- selection visual
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            sel = bool(value)
            self._halo.setVisible(sel)
        return super().itemChange(change, value)

    def set_label_text(self, text: str):
        self._label.setText(text)
        # Update background size to fit the text
        rect = self._label.boundingRect()
        self._label_bg.setRect(rect.adjusted(-2, -1, 2, 1))  # Small padding
        self._label_bg.setPos(self._label.pos())

    def set_label_offset(self, dx_px: float, dy_px: float):
        try:
            self.label_offset = QtCore.QPointF(float(dx_px), float(dy_px))
            self._label.setPos(self.label_offset)
        except Exception:
            pass

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
            "electrical": self.electrical,
            "circuit_id": self.circuit_id,
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

        # Load electrical properties
        electrical = d.get("electrical")
        if electrical:
            it.set_electrical_properties(electrical)

        # Load circuit connection
        circuit_id = d.get("circuit_id")
        if circuit_id:
            it.set_circuit(circuit_id)

        return it

    # ---- terminals
    def _init_terminals(self):
        """Initialize terminal positions based on device type."""
        device_type = self.name.lower()

        if "smoke" in device_type or "heat" in device_type:
            # Detectors typically have 2 terminals (positive, negative)
            self.electrical["terminals"] = [
                {"name": "+", "pos": QtCore.QPointF(-8, 6), "type": "power"},
                {"name": "-", "pos": QtCore.QPointF(8, 6), "type": "power"},
            ]
        elif "strobe" in device_type or "horn" in device_type or "speaker" in device_type:
            # Notification appliances typically have 2-4 terminals
            self.electrical["terminals"] = [
                {"name": "+", "pos": QtCore.QPointF(-10, 6), "type": "power"},
                {"name": "-", "pos": QtCore.QPointF(-10, -6), "type": "power"},
                {"name": "C", "pos": QtCore.QPointF(10, 6), "type": "signal"},
                {"name": "NC", "pos": QtCore.QPointF(10, -6), "type": "signal"},
            ]
        else:
            # Default 2 terminals
            self.electrical["terminals"] = [
                {"name": "1", "pos": QtCore.QPointF(-6, 6), "type": "power"},
                {"name": "2", "pos": QtCore.QPointF(6, 6), "type": "power"},
            ]

    def _update_terminal_visuals(self):
        """Update visual representation of terminal points."""
        # Clear existing terminal visuals
        for point in self._terminal_points:
            self.removeFromGroup(point)
        self._terminal_points.clear()

        # Add terminal points
        for terminal in self.electrical["terminals"]:
            point = QtWidgets.QGraphicsEllipseItem(-2, -2, 4, 4)
            point.setPos(terminal["pos"])
            point.setBrush(QtGui.QBrush(QtGui.QColor("#FFD700")))  # Gold color
            point.setPen(QtGui.QPen(QtGui.QColor("#000000"), 1))
            point.setZValue(1)
            point.setAcceptedMouseButtons(QtCore.Qt.NoButton)
            point.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
            self.addToGroup(point)
            self._terminal_points.append(point)

    def set_electrical_properties(self, properties: dict):
        """Set electrical properties for the device."""
        if properties:
            self.electrical.update(properties)
            self._update_terminal_visuals()

    def get_terminal_positions(self) -> list:
        """Get list of terminal positions in scene coordinates."""
        positions = []
        for terminal in self.electrical["terminals"]:
            scene_pos = self.mapToScene(terminal["pos"])
            positions.append(
                {"name": terminal["name"], "position": scene_pos, "type": terminal["type"]}
            )
        return positions

    def get_electrical_current(self, mode: str = "standby") -> float:
        """Get current draw for specified mode (standby/alarm)."""
        if mode == "alarm":
            return self.electrical["current_alarm_a"]
        else:
            return self.electrical["current_standby_a"]

    # ---- circuit connection
    def set_circuit(self, circuit_id: str | None):
        """Set the circuit ID for this device and update visual badge."""
        self.circuit_id = circuit_id

        if circuit_id:
            # Create or update circuit badge
            if self.circuit_badge is None:
                self.circuit_badge = QtWidgets.QGraphicsTextItem()
                self.circuit_badge.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
                self.circuit_badge.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
                self.circuit_badge.mousePressEvent = self._on_badge_click
                self.addToGroup(self.circuit_badge)

            # Format circuit ID (e.g., "Circuit_1" -> "C1")
            display_id = circuit_id.replace("Circuit_", "C") if circuit_id.startswith("Circuit_") else circuit_id
            self.circuit_badge.setPlainText(display_id)

            # Style the badge
            font = self.circuit_badge.font()
            font.setBold(True)
            font.setPointSize(8)
            self.circuit_badge.setFont(font)
            self.circuit_badge.setDefaultTextColor(QtGui.QColor("#FFFFFF"))
            self.circuit_badge.setPos(12, 6)  # Position next to device

            # Add background for visibility
            # Note: For simplicity, we'll use text color contrast for now
            self.circuit_badge.setVisible(True)
        else:
            # Remove badge if no circuit
            if self.circuit_badge:
                self.removeFromGroup(self.circuit_badge)
                self.circuit_badge = None

    def _on_badge_click(self, event):
        """Handle click on circuit badge to show device attributes."""
        # Emit signal or call parent method to show device attributes dialog
        # For now, we'll use a simple message box
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("Device Attributes")
        msg.setText(f"Device: {self.name}\nCircuit: {self.circuit_id}\nManufacturer: {self.manufacturer}\nPart #: {self.part_number}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def get_circuit_info(self) -> dict | None:
        """Get circuit connection information for this device."""
        if self.circuit_id:
            return {
                "circuit_id": self.circuit_id,
                "device_name": self.name,
                "device_type": self.symbol,
                "position": self.pos(),
                "electrical": self.electrical
            }
        return None
