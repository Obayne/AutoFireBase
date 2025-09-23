from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor

class DeviceItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, x, y, symbol, name, manufacturer, part_number, layer=None, device_type="Unknown", id=None, slc_compatible=False, nac_compatible=False):
        super().__init__()
        self.setPos(x, y)
        self.setFlags(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.symbol = symbol
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number
        self.layer = layer
        self.device_type = device_type
        self.id = id
        self.slc_compatible = slc_compatible
        self.nac_compatible = nac_compatible
        self.system_category = "Fire Alarm"  # Default to Fire Alarm

        # Connection status indicators
        self.connection_status = "disconnected"  # disconnected, partial, connected
        self.connections = []  # List of connected devices
        self.incoming_connections = []  # List of devices connected to this device

        # Create device symbol based on type
        self._glyph = self._create_device_symbol(symbol)
        self._glyph.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._glyph.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.addToGroup(self._glyph)

        # Label
        self._label = QtWidgets.QGraphicsSimpleTextItem(self.name)
        self._label.setBrush(QBrush(QColor("#EAEAEA")))
        self._label.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self._label.setPos(QtCore.QPointF(12, -14))
        # Track label offset in scene pixels relative to device origin
        self.label_offset = QtCore.QPointF(self._label.pos())
        self._label.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._label.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.addToGroup(self._label)

        # Selection halo
        self._halo = QtWidgets.QGraphicsEllipseItem(-9, -9, 18, 18)
        halo_pen = QPen(QColor(60,180,255,220)); halo_pen.setCosmetic(True); halo_pen.setWidthF(1.4)
        self._halo.setPen(halo_pen); self._halo.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self._halo.setZValue(-1); self._halo.setVisible(False)
        self.addToGroup(self._halo)

        # Coverage overlays
        self.coverage = {"mode":"none", "mount":"ceiling",
                         "params":{},  # mode-specific inputs
                         "computed_radius_ft":0.0,
                         "px_per_ft":12.0}
        self.coverage_enabled = True
        self._cov_circle = QtWidgets.QGraphicsEllipseItem(); self._cov_circle.setZValue(-10); self._cov_circle.setVisible(False)
        self._cov_circle.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._cov_circle.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self._cov_circle.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        cpen = QPen(QColor(80,170,255,200)); cpen.setCosmetic(True); cpen.setStyle(Qt.PenStyle.DashLine)
        self._cov_circle.setPen(cpen); self._cov_circle.setBrush(QBrush(QColor(80,170,255,40)))
        self.addToGroup(self._cov_circle)

        self._cov_square = QtWidgets.QGraphicsRectItem(); self._cov_square.setZValue(-11); self._cov_square.setVisible(False)
        self._cov_square.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._cov_square.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self._cov_square.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        spen = QPen(QColor(80,170,255,140)); spen.setCosmetic(True); spen.setStyle(Qt.PenStyle.DotLine)
        self._cov_square.setPen(spen); self._cov_square.setBrush(QBrush(QColor(80,170,255,25)))
        self.addToGroup(self._cov_square)

        # Connection status indicator
        self._connection_indicator = QtWidgets.QGraphicsRectItem(-12, -12, 5, 5)
        self._connection_indicator.setZValue(100)  # On top
        self._connection_indicator.setPen(QPen(QColor(255, 255, 255, 200)))
        self._connection_indicator.setBrush(QBrush(QColor(255, 0, 0, 200)))  # Red for disconnected
        self._connection_indicator.setVisible(True)
        self._blink_state = False
        self._blink_timer = None
        self._update_connection_indicator()
        self.addToGroup(self._connection_indicator)

        # Fire alarm specific properties
        self.slc_address = None
        self.circuit_id = None
        self.zone = ""
        
        self.setPos(x, y)

        self.update_layer_properties()

    def update_layer_properties(self):
        if self.layer:
            self.setVisible(self.layer['visible'])
            self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, not self.layer['locked'])
            self._label.setVisible(self.layer['show_name'])
            # Update glyph color
            pen = self._glyph.pen()
            pen.setColor(QColor(self.layer['color']))
            self._glyph.setPen(pen)

    def _create_device_symbol(self, symbol):
        """Create appropriate device symbol based on symbol code."""
        # Default pen and brush
        pen = QPen(QColor("#D8D8D8")); pen.setCosmetic(True); pen.setWidthF(1.5)
        if self.layer:
            pen.setColor(QColor(self.layer['color']))
        brush = QBrush(QColor("#20252B"))
        
        # Fire alarm specific colors based on device type
        if self.device_type == "Detector":
            pen.setColor(QColor("#4CAF50"))  # Green for detectors
            brush = QBrush(QColor("#1B5E20"))  # Darker green fill
        elif self.device_type == "Notification":
            pen.setColor(QColor("#2196F3"))  # Blue for notifications
            brush = QBrush(QColor("#0D47A1"))  # Darker blue fill
        elif self.device_type == "Initiating":
            pen.setColor(QColor("#FF9800"))  # Orange for initiating devices
            brush = QBrush(QColor("#E65100"))  # Darker orange fill
        elif self.device_type == "Control":
            pen.setColor(QColor("#F44336"))  # Red for control panels
            brush = QBrush(QColor("#B71C1C"))  # Darker red fill
            
        # Create symbol based on device type with enhanced visual representation
        if symbol in ["SD", "HD"]:  # Smoke/Heat Detectors
            # Enhanced circle with cross inside and additional details
            item = QtWidgets.QGraphicsEllipseItem(-7, -7, 14, 14)
            item.setPen(pen)
            item.setBrush(brush)
            
            # Add cross lines with enhanced visibility
            cross_pen = QPen(pen.color()); cross_pen.setCosmetic(True); cross_pen.setWidthF(2.0)
            line1 = QtWidgets.QGraphicsLineItem(-5, -5, 5, 5)
            line1.setPen(cross_pen)
            line1.setParentItem(item)
            line2 = QtWidgets.QGraphicsLineItem(-5, 5, 5, -5)
            line2.setPen(cross_pen)
            line2.setParentItem(item)
            
            # Add small circle in center to represent sensor
            center_pen = QPen(pen.color()); center_pen.setCosmetic(True); center_pen.setWidthF(1.5)
            center_brush = QBrush(pen.color())
            center_circle = QtWidgets.QGraphicsEllipseItem(-2, -2, 4, 4)
            center_circle.setPen(center_pen)
            center_circle.setBrush(center_brush)
            center_circle.setParentItem(item)
            
            # Add device type indicator
            if symbol == "SD":
                # Add "S" for smoke detector
                text = QtWidgets.QGraphicsSimpleTextItem("S")
                font = QtGui.QFont("Arial", 6)
                font.setBold(True)
                text.setFont(font)
                text.setBrush(QBrush(QColor("#FFFFFF")))
                text.setPos(-3, -4)
                text.setParentItem(item)
            elif symbol == "HD":
                # Add "H" for heat detector
                text = QtWidgets.QGraphicsSimpleTextItem("H")
                font = QtGui.QFont("Arial", 6)
                font.setBold(True)
                text.setFont(font)
                text.setBrush(QBrush(QColor("#FFFFFF")))
                text.setPos(-3, -4)
                text.setParentItem(item)
            
        elif symbol in ["S", "HS"]:  # Strobes
            # Enhanced diamond shape with internal details
            path = QtGui.QPainterPath()
            path.moveTo(0, -7)  # Top
            path.lineTo(7, 0)   # Right
            path.lineTo(0, 7)   # Bottom
            path.lineTo(-7, 0)  # Left
            path.closeSubpath()
            item = QtWidgets.QGraphicsPathItem(path)
            item.setPen(pen)
            item.setBrush(brush)
            
            # Add internal lines to represent flash element
            if symbol == "HS":  # Horn Strobe has additional details
                # Add arc to represent horn
                arc_path = QtGui.QPainterPath()
                arc_path.arcMoveTo(-4, -4, 8, 8, 45)
                arc_path.arcTo(-4, -4, 8, 8, 45, 90)
                arc_item = QtWidgets.QGraphicsPathItem(arc_path)
                arc_pen = QPen(pen.color()); arc_pen.setCosmetic(True); arc_pen.setWidthF(1.5)
                arc_item.setPen(arc_pen)
                arc_item.setParentItem(item)
                
                # Add "HS" text
                text = QtWidgets.QGraphicsSimpleTextItem("HS")
                font = QtGui.QFont("Arial", 5)
                font.setBold(True)
                text.setFont(font)
                text.setBrush(QBrush(QColor("#FFFFFF")))
                text.setPos(-6, -3)
                text.setParentItem(item)
            else:
                # Add "S" text for strobe
                text = QtWidgets.QGraphicsSimpleTextItem("S")
                font = QtGui.QFont("Arial", 6)
                font.setBold(True)
                text.setFont(font)
                text.setBrush(QBrush(QColor("#FFFFFF")))
                text.setPos(-3, -4)
                text.setParentItem(item)
            
        elif symbol == "SPK":  # Speakers
            # Enhanced triangle shape with sound wave representation
            path = QtGui.QPainterPath()
            path.moveTo(0, -8)      # Top
            path.lineTo(6.9, 4)     # Bottom right
            path.lineTo(-6.9, 4)    # Bottom left
            path.closeSubpath()
            item = QtWidgets.QGraphicsPathItem(path)
            item.setPen(pen)
            item.setBrush(brush)
            
            # Add sound waves with enhanced visibility
            wave_pen = QPen(pen.color()); wave_pen.setCosmetic(True); wave_pen.setWidthF(1.2)
            for i in range(3):
                wave_path = QtGui.QPainterPath()
                wave_path.arcMoveTo(-3-i, -3-i, 6+2*i, 6+2*i, -30)
                wave_path.arcTo(-3-i, -3-i, 6+2*i, 6+2*i, -30, 60)
                wave_item = QtWidgets.QGraphicsPathItem(wave_path)
                wave_item.setPen(wave_pen)
                wave_item.setParentItem(item)
            
            # Add "SP" text
            text = QtWidgets.QGraphicsSimpleTextItem("SP")
            font = QtGui.QFont("Arial", 5)
            font.setBold(True)
            text.setFont(font)
            text.setBrush(QBrush(QColor("#FFFFFF")))
            text.setPos(-5, -2)
            text.setParentItem(item)
            
        elif symbol == "PS":  # Pull Stations
            # Enhanced rectangle with diagonal line and pull handle
            item = QtWidgets.QGraphicsRectItem(-6, -6, 12, 12)
            item.setPen(pen)
            item.setBrush(brush)
            
            # Add diagonal line with enhanced visibility
            diag_pen = QPen(pen.color()); diag_pen.setCosmetic(True); diag_pen.setWidthF(2.0)
            diag_line = QtWidgets.QGraphicsLineItem(-4, -4, 4, 4)
            diag_line.setPen(diag_pen)
            diag_line.setParentItem(item)
            
            # Add pull handle with enhanced visibility
            handle_pen = QPen(pen.color()); handle_pen.setCosmetic(True); handle_pen.setWidthF(2.5)
            handle_line = QtWidgets.QGraphicsLineItem(0, 4, 0, 10)
            handle_line.setPen(handle_pen)
            handle_line.setParentItem(item)
            
            # Add "PS" text
            text = QtWidgets.QGraphicsSimpleTextItem("PS")
            font = QtGui.QFont("Arial", 5)
            font.setBold(True)
            text.setFont(font)
            text.setBrush(QBrush(QColor("#FFFFFF")))
            text.setPos(-5, -5)
            text.setParentItem(item)
            
        elif symbol.startswith("FACP") or self.device_type == "Control":  # Control Panels
            # Enhanced larger rectangle with multiple internal elements
            item = QtWidgets.QGraphicsRectItem(-10, -10, 20, 20)
            item.setPen(pen)
            item.setBrush(brush)
            
            # Add internal grid lines to represent panel with enhanced visibility
            grid_pen = QPen(pen.color()); grid_pen.setCosmetic(True); grid_pen.setWidthF(1.2)
            # Horizontal lines
            h_line1 = QtWidgets.QGraphicsLineItem(-8, -5, 8, -5)
            h_line1.setPen(grid_pen)
            h_line1.setParentItem(item)
            h_line2 = QtWidgets.QGraphicsLineItem(-8, 0, 8, 0)
            h_line2.setPen(grid_pen)
            h_line2.setParentItem(item)
            h_line3 = QtWidgets.QGraphicsLineItem(-8, 5, 8, 5)
            h_line3.setPen(grid_pen)
            h_line3.setParentItem(item)
            # Vertical lines
            v_line1 = QtWidgets.QGraphicsLineItem(-5, -8, -5, 8)
            v_line1.setPen(grid_pen)
            v_line1.setParentItem(item)
            v_line2 = QtWidgets.QGraphicsLineItem(0, -8, 0, 8)
            v_line2.setPen(grid_pen)
            v_line2.setParentItem(item)
            v_line3 = QtWidgets.QGraphicsLineItem(5, -8, 5, 8)
            v_line3.setPen(grid_pen)
            v_line3.setParentItem(item)
            
            # Add status indicator LED with enhanced visibility
            led_pen = QPen(QColor("#4CAF50")); led_pen.setCosmetic(True); led_pen.setWidthF(1.5)
            led_brush = QBrush(QColor("#4CAF50"))
            led = QtWidgets.QGraphicsEllipseItem(6, -8, 3, 3)
            led.setPen(led_pen)
            led.setBrush(led_brush)
            led.setParentItem(item)
            
            # Add "FACP" text
            text = QtWidgets.QGraphicsSimpleTextItem("FACP")
            font = QtGui.QFont("Arial", 4)
            font.setBold(True)
            text.setFont(font)
            text.setBrush(QBrush(QColor("#FFFFFF")))
            text.setPos(-4, -9)
            text.setParentItem(item)
            
        else:  # Default/Unknown
            # Enhanced simple circle with question mark
            item = QtWidgets.QGraphicsEllipseItem(-7, -7, 14, 14)
            item.setPen(pen)
            item.setBrush(brush)
            
            # Add question mark with enhanced visibility
            question = QtWidgets.QGraphicsSimpleTextItem("?")
            font = QtGui.QFont("Arial", 8)
            font.setBold(True)
            question.setFont(font)
            question.setPos(-4, -5)
            question.setBrush(QBrush(QColor("#FFFFFF")))
            question.setParentItem(item)
            
        return item

    # ---- selection visual ----
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
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

    # ---- address annotation ----
    def show_address_annotation(self):
        """Show the device address as an annotation next to the device."""
        if self.slc_address is not None:
            # Create or update address annotation
            if not hasattr(self, '_address_annotation'):
                self._address_annotation = QtWidgets.QGraphicsSimpleTextItem()
                self._address_annotation.setBrush(QBrush(QColor("#FFFF00")))  # Yellow text
                self._address_annotation.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
                self._address_annotation.setZValue(200)  # On top
                self._address_annotation.setParentItem(self)
                
            # Position the annotation next to the device
            self._address_annotation.setText(f"Addr: {self.slc_address}")
            self._address_annotation.setPos(12, 0)  # Position to the right of the device
            
    def hide_address_annotation(self):
        """Hide the address annotation."""
        if hasattr(self, '_address_annotation'):
            self._address_annotation.setVisible(False)

    # ---- coverage API ----
    def set_coverage(self, cfg: dict):
        if not cfg: return
        self.coverage.update(cfg)
        self._update_coverage_items()

    def _update_coverage_items(self):
        if not self.coverage_enabled:
            self._cov_circle.setVisible(False)
            self._cov_square.setVisible(False)
            return
        mode = self.coverage.get("mode","none")
        r_ft = float(self.coverage.get("computed_radius_ft") or 0.0)
        ppf  = float(self.coverage.get("px_per_ft") or 12.0)
        r_px = r_ft * ppf

        # hide all
        self._cov_circle.setVisible(False)
        self._cov_square.setVisible(False)
        if mode == "none" or r_px <= 0:
            return

        # circle always
        self._cov_circle.setRect(-r_px, -r_px, 2*r_px, 2*r_px)
        self._cov_circle.setVisible(True)

        # if strobe + ceiling: show square footprint
        if mode == "strobe" and self.coverage.get("mount","ceiling") == "ceiling":
            side = 2*r_px
            self._cov_square.setRect(-side/2, -side/2, side, side)
            self._cov_square.setVisible(True)

    def set_coverage_enabled(self, on: bool):
        self.coverage_enabled = bool(on)
        self._update_coverage_items()

    # ---- connection methods ----
    def _update_connection_indicator(self):
        """Update the connection indicator based on connection status."""
        # Stop any existing blink timer
        if self._blink_timer:
            self._blink_timer.stop()
            self._blink_timer = None
            
        if self.connection_status == "disconnected":
            # Red square for disconnected
            self._connection_indicator.setBrush(QBrush(QColor(255, 0, 0, 200)))  # Red
            self._connection_indicator.setRect(-12, -12, 5, 5)
            # Start blinking for disconnected devices
            self._start_blinking()
        elif self.connection_status == "partial":
            # Yellow square for partial connections
            self._connection_indicator.setBrush(QBrush(QColor(255, 255, 0, 200)))  # Yellow
            self._connection_indicator.setRect(-12, -12, 5, 5)
            # Start slow blinking for partial connections
            self._start_blinking(slow=True)
        else:  # connected
            # Green square for fully connected (no blinking)
            self._connection_indicator.setBrush(QBrush(QColor(0, 255, 0, 200)))  # Green
            self._connection_indicator.setRect(-12, -12, 5, 5)
            self._connection_indicator.setVisible(True)
            
    def _start_blinking(self, slow=False):
        """Start blinking the connection indicator."""
        # Import QtCore here to avoid circular imports
        from PySide6.QtCore import QTimer
        
        # Create timer if it doesn't exist
        if not self._blink_timer:
            self._blink_timer = QTimer()
            self._blink_timer.timeout.connect(self._toggle_blink)
            
        # Set blinking interval (fast for disconnected, slow for partial)
        interval = 500 if slow else 250  # milliseconds
        self._blink_timer.start(interval)
        self._blink_state = True
        self._connection_indicator.setVisible(True)
        
    def _toggle_blink(self):
        """Toggle the visibility of the connection indicator for blinking effect."""
        self._blink_state = not self._blink_state
        self._connection_indicator.setVisible(self._blink_state)
            
    def set_connection_status(self, status):
        """Set the connection status and update the indicator."""
        self.connection_status = status
        self._update_connection_indicator()
        
    def add_connection(self, device):
        """Add a connection to another device."""
        if device not in self.connections:
            self.connections.append(device)
            # Also add this device to the target's incoming connections
            if self not in device.incoming_connections:
                device.incoming_connections.append(self)
            self._update_connection_status()
                
    def remove_connection(self, device):
        """Remove a connection to another device."""
        if device in self.connections:
            self.connections.remove(device)
            # Also remove this device from the target's incoming connections
            if self in device.incoming_connections:
                device.incoming_connections.remove(self)
            self._update_connection_status()
            
    def _update_connection_status(self):
        """Update connection status based on connections."""
        total_connections = len(self.connections) + len(self.incoming_connections)
        
        if total_connections == 0:
            self.set_connection_status("disconnected")
        elif self.device_type == "Control":  # Control panels might have many connections
            # For control panels, consider connected if they have outgoing connections
            if len(self.connections) > 0:
                self.set_connection_status("connected")
            else:
                self.set_connection_status("disconnected")
        else:
            # For other devices, consider connected if they have any connections
            self.set_connection_status("connected")
            
    def get_connection_count(self):
        """Get total number of connections (incoming + outgoing)."""
        return len(self.connections) + len(self.incoming_connections)

    # ---- fire alarm specific methods ----
    def set_slc_address(self, address: int):
        """Set the SLC address for this device."""
        self.slc_address = address
        
    def set_circuit_id(self, circuit_id: int):
        """Set the circuit ID for this device."""
        self.circuit_id = circuit_id
        
    def set_zone(self, zone: str):
        """Set the zone for this device."""
        self.zone = zone

    # ---- serialization ----
    def to_json(self):
        return {
            "id": self.id,
            "x": float(self.pos().x()),
            "y": float(self.pos().y()),
            "symbol": self.symbol,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "part_number": self.part_number,
            "device_type": self.device_type,
            "slc_address": self.slc_address,
            "circuit_id": self.circuit_id,
            "zone": self.zone,
            "coverage": self.coverage,
            "show_coverage": bool(getattr(self, 'coverage_enabled', True)),
        }

    @staticmethod
    def from_json(d: dict):
        it = DeviceItem(float(d.get("x",0)), float(d.get("y",0)),
                        d.get("symbol","?"), d.get("name","Device"),
                        d.get("manufacturer",""), d.get("part_number",""),
                        device_type=d.get("type",""), id=d.get("id"),
                        slc_compatible=d.get("slc_compatible", False), nac_compatible=d.get("nac_compatible", False))
        cov = d.get("coverage")
        if cov: it.set_coverage(cov)
        it.set_coverage_enabled(bool(d.get("show_coverage", True)))
        
        # Set fire alarm specific properties
        if "slc_address" in d:
            it.set_slc_address(d["slc_address"])
        if "circuit_id" in d:
            it.set_circuit_id(d["circuit_id"])
        if "zone" in d:
            it.set_zone(d["zone"])
            
        return it