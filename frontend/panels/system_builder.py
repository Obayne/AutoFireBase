"""
System Builder - Visual logic and flow design for fire alarm systems
"""

from enum import Enum

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt


class LogicType(Enum):
    """Types of logic elements in the system."""

    INPUT_DEVICE = "input_device"
    OUTPUT_DEVICE = "output_device"
    AND_GATE = "and_gate"
    OR_GATE = "or_gate"
    NOT_GATE = "not_gate"
    TIMER = "timer"
    DELAY = "delay"


class ConnectionPoint:
    """Represents a connection point on a logic element."""

    def __init__(self, element, point_type: str, position: QtCore.QPointF, label: str = ""):
        self.element = element
        self.point_type = point_type  # "input" or "output"
        self.position = position
        self.label = label
        self.connections: list[Connection] = []

    def scene_pos(self) -> QtCore.QPointF:
        """Get the position in scene coordinates."""
        if hasattr(self.element, "scenePos"):
            return self.element.scenePos() + self.position
        return self.position


class Connection:
    """Represents a connection between two connection points."""

    def __init__(self, start_point: ConnectionPoint, end_point: ConnectionPoint):
        self.start_point = start_point
        self.end_point = end_point
        self.path_item: QtWidgets.QGraphicsPathItem | None = None

    def update_path(self):
        """Update the visual path of the connection."""
        if not self.path_item:
            return

        start_pos = self.start_point.scene_pos()
        end_pos = self.end_point.scene_pos()

        # Create curved path
        path = QtGui.QPainterPath()
        path.moveTo(start_pos)

        # Control points for curve
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()

        cp1 = QtCore.QPointF(start_pos.x() + dx * 0.4, start_pos.y())
        cp2 = QtCore.QPointF(end_pos.x() - dx * 0.4, end_pos.y())

        path.cubicTo(cp1, cp2, end_pos)

        self.path_item.setPath(path)


class LogicElement(QtWidgets.QGraphicsItem):
    """Base class for logic elements in the system builder."""

    def __init__(self, logic_type: LogicType, name: str, width: float = 80, height: float = 60):
        super().__init__()
        self.logic_type = logic_type
        self.name = name
        self.width = width
        self.height = height

        self.setFlags(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Connection points
        self.input_points: list[ConnectionPoint] = []
        self.output_points: list[ConnectionPoint] = []

        self._setup_connection_points()

    def _setup_connection_points(self):
        """Setup connection points based on logic type."""
        if self.logic_type == LogicType.INPUT_DEVICE:
            # Input devices have one output
            self.output_points.append(
                ConnectionPoint(self, "output", QtCore.QPointF(self.width, self.height / 2), "OUT")
            )
        elif self.logic_type == LogicType.OUTPUT_DEVICE:
            # Output devices have one input
            self.input_points.append(
                ConnectionPoint(self, "input", QtCore.QPointF(0, self.height / 2), "IN")
            )
        elif self.logic_type in [LogicType.AND_GATE, LogicType.OR_GATE]:
            # Binary gates have two inputs and one output
            self.input_points.append(
                ConnectionPoint(self, "input", QtCore.QPointF(0, self.height / 3), "IN1")
            )
            self.input_points.append(
                ConnectionPoint(self, "input", QtCore.QPointF(0, 2 * self.height / 3), "IN2")
            )
            self.output_points.append(
                ConnectionPoint(self, "output", QtCore.QPointF(self.width, self.height / 2), "OUT")
            )
        elif self.logic_type == LogicType.NOT_GATE:
            # NOT gate has one input and one output
            self.input_points.append(
                ConnectionPoint(self, "input", QtCore.QPointF(0, self.height / 2), "IN")
            )
            self.output_points.append(
                ConnectionPoint(self, "output", QtCore.QPointF(self.width, self.height / 2), "OUT")
            )
        elif self.logic_type in [LogicType.TIMER, LogicType.DELAY]:
            # Timer/delay have one input and one output
            self.input_points.append(
                ConnectionPoint(self, "input", QtCore.QPointF(0, self.height / 2), "IN")
            )
            self.output_points.append(
                ConnectionPoint(self, "output", QtCore.QPointF(self.width, self.height / 2), "OUT")
            )

    def boundingRect(self) -> QtCore.QRectF:
        """Return the bounding rectangle."""
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QtGui.QPainter, option, widget):
        """Paint the logic element."""
        # Set colors based on selection
        if self.isSelected():
            pen_color = QtGui.QColor("#0078d4")
            brush_color = QtGui.QColor("#e6f3ff")
        else:
            pen_color = QtGui.QColor("#333333")
            brush_color = QtGui.QColor("#ffffff")

        # Draw main rectangle
        pen = QtGui.QPen(pen_color, 2)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(brush_color))
        painter.drawRoundedRect(0, 0, int(self.width), int(self.height), 5, 5)

        # Draw logic symbol
        painter.setPen(QtGui.QPen(QtGui.QColor("#000000"), 2))
        self._draw_logic_symbol(painter)

        # Draw name
        painter.setPen(QtGui.QPen(QtGui.QColor("#000000")))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(
            QtCore.QRectF(5, 5, self.width - 10, 15), QtCore.Qt.AlignmentFlag.AlignCenter, self.name
        )

        # Draw connection points
        point_radius = 4
        painter.setPen(QtGui.QPen(QtGui.QColor("#666666"), 1))
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#cccccc")))

        for point in self.input_points + self.output_points:
            painter.drawEllipse(point.position, point_radius, point_radius)

    def _draw_logic_symbol(self, painter: QtGui.QPainter):
        """Draw the logic symbol inside the element."""
        center_x = self.width / 2
        center_y = self.height / 2
        size = min(self.width, self.height) * 0.4

        if self.logic_type == LogicType.AND_GATE:
            # Draw AND gate symbol
            path = QtGui.QPainterPath()
            path.moveTo(int(center_x - size / 2), int(center_y - size / 2))
            path.lineTo(int(center_x), int(center_y - size / 2))
            path.arcTo(
                int(center_x - size / 2), int(center_y - size / 2), int(size), int(size), 90, -180
            )
            path.lineTo(int(center_x - size / 2), int(center_y + size / 2))
            painter.drawPath(path)

        elif self.logic_type == LogicType.OR_GATE:
            # Draw OR gate symbol
            path = QtGui.QPainterPath()
            path.moveTo(int(center_x - size / 2), int(center_y - size / 2))
            path.quadTo(
                int(center_x + size / 4),
                int(center_y),
                int(center_x - size / 2),
                int(center_y + size / 2),
            )
            path.moveTo(int(center_x - size / 2), int(center_y - size / 2))
            path.lineTo(int(center_x), int(center_y))
            path.lineTo(int(center_x - size / 2), int(center_y + size / 2))
            painter.drawPath(path)

        elif self.logic_type == LogicType.NOT_GATE:
            # Draw NOT gate symbol (triangle with circle)
            path = QtGui.QPainterPath()
            path.moveTo(int(center_x - size / 2), int(center_y - size / 2))
            path.lineTo(int(center_x - size / 2), int(center_y + size / 2))
            path.lineTo(int(center_x + size / 3), int(center_y))
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawEllipse(
                int(center_x + size / 3), int(center_y - size / 8), int(size / 4), int(size / 4)
            )

        elif self.logic_type in [LogicType.TIMER, LogicType.DELAY]:
            # Draw timer/delay symbol (clock)
            painter.drawEllipse(
                int(center_x - size / 3),
                int(center_y - size / 3),
                int(size * 2 / 3),
                int(size * 2 / 3),
            )
            # Clock hands
            painter.drawLine(int(center_x), int(center_y), int(center_x + size / 4), int(center_y))
            painter.drawLine(int(center_x), int(center_y), int(center_x), int(center_y - size / 4))

    def itemChange(self, change, value):
        """Handle item changes."""
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # Update connection paths when item moves
            for point in self.input_points + self.output_points:
                for connection in point.connections:
                    connection.update_path()

        return super().itemChange(change, value)


class SystemBuilderScene(QtWidgets.QGraphicsScene):
    """Scene for the system builder."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connections: list[Connection] = []
        self.pending_connection: ConnectionPoint | None = None
        self.temp_line: QtWidgets.QGraphicsLineItem | None = None

    def mousePressEvent(self, event):
        """Handle mouse press events for connection creation."""
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.scenePos(), QtGui.QTransform())
            if isinstance(item, LogicElement):
                # Check if clicking on a connection point
                for point in item.input_points + item.output_points:
                    point_scene_pos = point.scene_pos()
                    distance = (event.scenePos() - point_scene_pos).manhattanLength()
                    if distance < 8:  # 8 pixel tolerance for clicking
                        if self.pending_connection is None:
                            # Start connection from this point
                            self.pending_connection = point
                            self.temp_line = QtWidgets.QGraphicsLineItem()
                            self.temp_line.setPen(
                                QtGui.QPen(QtGui.QColor("#0078d4"), 2, Qt.PenStyle.DashLine)
                            )
                            self.addItem(self.temp_line)
                        else:
                            # Complete connection to this point
                            if self._can_connect(self.pending_connection, point):
                                self.add_connection(self.pending_connection, point)
                            self._clear_pending_connection()
                        return

        # Clear pending connection if clicking elsewhere
        if self.pending_connection:
            self._clear_pending_connection()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events for connection preview."""
        if self.pending_connection and self.temp_line:
            # Update temporary connection line
            start_pos = self.pending_connection.scene_pos()
            end_pos = event.scenePos()
            self.temp_line.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

        super().mouseMoveEvent(event)

    def _can_connect(self, start_point: ConnectionPoint, end_point: ConnectionPoint) -> bool:
        """Check if two connection points can be connected."""
        # Can't connect point to itself
        if start_point == end_point:
            return False

        # Can't connect within the same element
        if start_point.element == end_point.element:
            return False

        # Output can connect to input, but not output to output or input to input
        if start_point.point_type == end_point.point_type:
            return False

        # Check if connection already exists
        for conn in self.connections:
            if (conn.start_point == start_point and conn.end_point == end_point) or (
                conn.start_point == end_point and conn.end_point == start_point
            ):
                return False

        return True

    def _clear_pending_connection(self):
        """Clear the pending connection state."""
        if self.temp_line:
            self.removeItem(self.temp_line)
            self.temp_line = None
        self.pending_connection = None

    def add_connection(self, start_point: ConnectionPoint, end_point: ConnectionPoint):
        """Add a connection between two points."""
        # Check if connection already exists
        for conn in self.connections:
            if (conn.start_point == start_point and conn.end_point == end_point) or (
                conn.start_point == end_point and conn.end_point == start_point
            ):
                return

        connection = Connection(start_point, end_point)
        self.connections.append(connection)

        # Create visual path
        path_item = QtWidgets.QGraphicsPathItem()
        pen = QtGui.QPen(QtGui.QColor("#0078d4"), 2)
        path_item.setPen(pen)
        path_item.setZValue(-1)  # Behind elements
        self.addItem(path_item)

        connection.path_item = path_item
        connection.update_path()

        # Add to connection lists
        start_point.connections.append(connection)
        end_point.connections.append(connection)

    def remove_connection(self, connection: Connection):
        """Remove a connection."""
        if connection in self.connections:
            self.connections.remove(connection)

            if connection.path_item:
                self.removeItem(connection.path_item)

            connection.start_point.connections.remove(connection)
            connection.end_point.connections.remove(connection)


class SystemBuilderPanel(QtWidgets.QDockWidget):
    """System Builder panel for designing fire alarm system logic."""

    def __init__(self, parent=None):
        super().__init__("System Builder", parent)
        self.scene = SystemBuilderScene()
        self.view = QtWidgets.QGraphicsView(self.scene)

        self.setup_ui()
        self.setup_toolbar()

    def setup_ui(self):
        """Setup the user interface."""
        widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout(widget)

        # Toolbar
        self._setup_toolbar()

        # Graphics view
        self.view.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
        self.view.setMinimumHeight(300)
        self.main_layout.addWidget(self.view)

        # Status
        self.status_label = QtWidgets.QLabel("Ready")
        self.main_layout.addWidget(self.status_label)

        self.setWidget(widget)
        self.setMinimumWidth(400)

    def _setup_toolbar(self):
        """Setup the toolbar with action buttons."""
        toolbar_widget = QtWidgets.QWidget()
        toolbar_layout = QtWidgets.QHBoxLayout(toolbar_widget)

        # File operations
        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.clicked.connect(self.save_system)
        toolbar_layout.addWidget(self.save_button)

        self.load_button = QtWidgets.QPushButton("Load")
        self.load_button.clicked.connect(self.load_system)
        toolbar_layout.addWidget(self.load_button)

        # Separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        toolbar_layout.addWidget(separator)

        # Add element buttons
        self.add_device_button = QtWidgets.QPushButton("Add Device")
        self.add_device_button.clicked.connect(self.add_device)
        toolbar_layout.addWidget(self.add_device_button)

        self.add_gate_button = QtWidgets.QPushButton("Add Gate")
        self.add_gate_button.clicked.connect(self.show_gate_menu)
        toolbar_layout.addWidget(self.add_gate_button)

        toolbar_layout.addStretch()

        self.validate_button = QtWidgets.QPushButton("Validate")
        self.validate_button.clicked.connect(self.validate_system)
        toolbar_layout.addWidget(self.validate_button)

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_scene)
        toolbar_layout.addWidget(self.clear_button)

        # Add toolbar to main layout
        self.main_layout.addWidget(toolbar_widget)

    def setup_toolbar(self):
        """Setup additional toolbar functionality."""
        # Context menu for adding gates
        self.gate_menu = QtWidgets.QMenu(self)
        self.gate_menu.addAction("AND Gate", lambda: self.add_gate(LogicType.AND_GATE))
        self.gate_menu.addAction("OR Gate", lambda: self.add_gate(LogicType.OR_GATE))
        self.gate_menu.addAction("NOT Gate", lambda: self.add_gate(LogicType.NOT_GATE))
        self.gate_menu.addSeparator()
        self.gate_menu.addAction("Timer", lambda: self.add_gate(LogicType.TIMER))
        self.gate_menu.addAction("Delay", lambda: self.add_gate(LogicType.DELAY))

    def add_device(self):
        """Add a device to the scene."""
        # Show device selection dialog
        devices = [
            ("Smoke Detector", LogicType.INPUT_DEVICE),
            ("Pull Station", LogicType.INPUT_DEVICE),
            ("Horn", LogicType.OUTPUT_DEVICE),
            ("Strobe", LogicType.OUTPUT_DEVICE),
            ("Speaker", LogicType.OUTPUT_DEVICE),
        ]

        device_names = [name for name, _ in devices]
        device_name, ok = QtWidgets.QInputDialog.getItem(
            self, "Add Device", "Select device type:", device_names, 0, False
        )

        if ok and device_name:
            device_type = next(t for n, t in devices if n == device_name)
            self._add_element(device_type, device_name)

    def show_gate_menu(self):
        """Show the gate selection menu."""
        self.gate_menu.exec(QtGui.QCursor.pos())

    def add_gate(self, gate_type: LogicType):
        """Add a logic gate to the scene."""
        name_map = {
            LogicType.AND_GATE: "AND",
            LogicType.OR_GATE: "OR",
            LogicType.NOT_GATE: "NOT",
            LogicType.TIMER: "Timer",
            LogicType.DELAY: "Delay",
        }
        name = name_map.get(gate_type, "Gate")
        self._add_element(gate_type, name)

    def _add_element(self, element_type: LogicType, name: str):
        """Add an element to the scene."""
        element = LogicElement(element_type, name)

        # Position at center of view
        view_center = self.view.mapToScene(self.view.viewport().rect().center())
        element.setPos(view_center - QtCore.QPointF(element.width / 2, element.height / 2))

        self.scene.addItem(element)
        self.status_label.setText(f"Added: {name}")

    def save_system(self):
        """Save the current system design to a file."""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save System", "", "System Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                import json

                data = self.get_system_data()
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
                self.status_label.setText(f"System saved to {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Save Error", f"Failed to save system: {e}")
                self.status_label.setText("Save failed")

    def load_system(self):
        """Load a system design from a file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load System", "", "System Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                import json

                with open(file_path) as f:
                    data = json.load(f)
                self.load_system_data(data)
                self.status_label.setText(f"System loaded from {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Load Error", f"Failed to load system: {e}")
                self.status_label.setText("Load failed")

    def validate_system(self):
        """Validate the current system design."""
        issues = []

        # Check for unconnected inputs
        for item in self.scene.items():
            if isinstance(item, LogicElement):
                if item.logic_type in [
                    LogicType.INPUT_DEVICE,
                    LogicType.AND_GATE,
                    LogicType.OR_GATE,
                    LogicType.NOT_GATE,
                ]:
                    for point in item.input_points:
                        if not point.connections:
                            issues.append(f"Unconnected input: {item.name}.{point.label}")

        # Check for unconnected outputs (warning, not error)
        unconnected_outputs = []
        for item in self.scene.items():
            if isinstance(item, LogicElement):
                if item.logic_type in [
                    LogicType.OUTPUT_DEVICE,
                    LogicType.AND_GATE,
                    LogicType.OR_GATE,
                    LogicType.NOT_GATE,
                ]:
                    for point in item.output_points:
                        if not point.connections:
                            unconnected_outputs.append(f"{item.name}.{point.label}")

        if issues:
            message = "Validation Issues:\n" + "\n".join(issues)
            if unconnected_outputs:
                message += "\n\nWarnings (unconnected outputs):\n" + "\n".join(unconnected_outputs)
            QtWidgets.QMessageBox.warning(self, "Validation Results", message)
            self.status_label.setText(f"Validation: {len(issues)} issues found")
        else:
            message = "System validation passed!"
            if unconnected_outputs:
                message += f"\n\nNote: {len(unconnected_outputs)} unconnected outputs"
            QtWidgets.QMessageBox.information(self, "Validation Results", message)
            self.status_label.setText("Validation passed")

    def clear_scene(self):
        """Clear all elements from the scene."""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Clear Scene",
            "Remove all elements from the system builder?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.scene.clear()
            self.scene.connections.clear()
            self.status_label.setText("Scene cleared")

    def get_system_data(self) -> dict:
        """Get the system data for serialization."""
        elements = []
        connections = []

        for item in self.scene.items():
            if isinstance(item, LogicElement):
                element_data = {
                    "type": item.logic_type.value,
                    "name": item.name,
                    "position": [item.x(), item.y()],
                }
                elements.append(element_data)

        for connection in self.scene.connections:
            conn_data = {
                "start_element": connection.start_point.element.name,
                "start_point": connection.start_point.label,
                "end_element": connection.end_point.element.name,
                "end_point": connection.end_point.label,
            }
            connections.append(conn_data)

        return {
            "elements": elements,
            "connections": connections,
        }

    def load_system_data(self, data: dict):
        """Load system data from serialization."""
        self.scene.clear()
        self.scene.connections.clear()

        # Create elements
        element_map = {}
        for element_data in data.get("elements", []):
            element_type = LogicType(element_data["type"])
            element = LogicElement(element_type, element_data["name"])
            element.setPos(*element_data["position"])
            self.scene.addItem(element)
            element_map[element_data["name"]] = element

        # Create connections
        for conn_data in data.get("connections", []):
            start_element = element_map.get(conn_data["start_element"])
            end_element = element_map.get(conn_data["end_element"])

            if start_element and end_element:
                # Find connection points
                start_point = None
                end_point = None

                for point in start_element.output_points:
                    if point.label == conn_data["start_point"]:
                        start_point = point
                        break

                for point in end_element.input_points:
                    if point.label == conn_data["end_point"]:
                        end_point = point
                        break

                if start_point and end_point:
                    self.scene.add_connection(start_point, end_point)
