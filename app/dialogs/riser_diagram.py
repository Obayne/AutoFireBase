from PySide6 import QtCore, QtGui, QtWidgets


class RiserDiagramDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Riser Diagram")
        self.setModal(True)
        self.resize(800, 600)

        self.main_window = parent

        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Riser Diagram Generator")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Diagram options
        options_group = QtWidgets.QGroupBox("Diagram Options")
        options_layout = QtWidgets.QFormLayout(options_group)

        self.diagram_type_combo = QtWidgets.QComboBox()
        self.diagram_type_combo.addItems(["System Overview", "Panel Connections", "Circuit Layout"])
        options_layout.addRow("Diagram Type:", self.diagram_type_combo)

        self.orientation_combo = QtWidgets.QComboBox()
        self.orientation_combo.addItems(["Vertical", "Horizontal"])
        options_layout.addRow("Orientation:", self.orientation_combo)

        self.include_panels = QtWidgets.QCheckBox("Include Panels")
        self.include_panels.setChecked(True)
        options_layout.addRow("Panels:", self.include_panels)

        self.include_circuits = QtWidgets.QCheckBox("Include Circuits")
        self.include_circuits.setChecked(True)
        options_layout.addRow("Circuits:", self.include_circuits)

        self.include_devices = QtWidgets.QCheckBox("Include Devices")
        options_layout.addRow("Devices:", self.include_devices)

        layout.addWidget(options_group)

        # Preview area
        preview_group = QtWidgets.QGroupBox("Diagram Preview")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)

        self.diagram_view = QtWidgets.QGraphicsView()
        self.diagram_scene = QtWidgets.QGraphicsScene()
        self.diagram_view.setScene(self.diagram_scene)
        self.diagram_view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        preview_layout.addWidget(self.diagram_view)

        layout.addWidget(preview_group)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        self.generate_btn = QtWidgets.QPushButton("Generate Diagram")
        self.generate_btn.clicked.connect(self.generate_diagram)
        button_layout.addWidget(self.generate_btn)

        self.export_btn = QtWidgets.QPushButton("Export Diagram")
        self.export_btn.clicked.connect(self.export_diagram)
        button_layout.addWidget(self.export_btn)

        button_layout.addStretch()

        self.ok_btn = QtWidgets.QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

        # Generate initial diagram
        self.generate_diagram()

    def generate_diagram(self):
        """Generate the riser diagram."""
        # Clear existing diagram
        self.diagram_scene.clear()

        # Get diagram parameters
        diagram_type = self.diagram_type_combo.currentText()
        orientation = self.orientation_combo.currentText()
        include_panels = self.include_panels.isChecked()
        include_circuits = self.include_circuits.isChecked()
        include_devices = self.include_devices.isChecked()

        # Create diagram based on type
        if diagram_type == "System Overview":
            self.create_system_overview()
        elif diagram_type == "Panel Connections":
            self.create_panel_connections()
        elif diagram_type == "Circuit Layout":
            self.create_circuit_layout()

        # Fit view to content
        self.diagram_view.fitInView(
            self.diagram_scene.itemsBoundingRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio
        )

    def create_system_overview(self):
        """Create a system overview diagram."""
        # Draw title
        title = QtWidgets.QGraphicsTextItem("Fire Alarm System Overview")
        title.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))
        title.setPos(200, 20)
        self.diagram_scene.addItem(title)

        # Draw panels
        if self.include_panels.isChecked():
            panel_y = 100
            for i in range(3):  # Sample panels
                panel = self.draw_panel(f"Panel {i+1}", 100, panel_y)
                panel_y += 150

        # Draw connections
        if self.include_circuits.isChecked():
            self.draw_connections()

    def create_panel_connections(self):
        """Create a panel connections diagram."""
        # Draw title
        title = QtWidgets.QGraphicsTextItem("Panel Connections Diagram")
        title.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))
        title.setPos(200, 20)
        self.diagram_scene.addItem(title)

        # Draw main panel
        main_panel = self.draw_panel("Main FACP Panel", 300, 100, is_main=True)

        # Draw sub-panels
        if self.include_panels.isChecked():
            sub_panel_y = 250
            for i in range(4):  # Sample sub-panels
                sub_panel = self.draw_panel(f"Sub-Panel {i+1}", 100 + i * 150, sub_panel_y)
                # Draw connection line
                line = QtWidgets.QGraphicsLineItem(350, 180, 150 + i * 150, sub_panel_y)
                pen = QtGui.QPen(QtCore.Qt.GlobalColor.black, 2)
                line.setPen(pen)
                self.diagram_scene.addItem(line)

    def create_circuit_layout(self):
        """Create a circuit layout diagram."""
        # Draw title
        title = QtWidgets.QGraphicsTextItem("Circuit Layout Diagram")
        title.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Weight.Bold))
        title.setPos(200, 20)
        self.diagram_scene.addItem(title)

        # Draw circuit
        circuit_y = 100
        for i in range(3):  # Sample circuits
            circuit_group = QtWidgets.QGraphicsItemGroup()

            # Circuit label
            label = QtWidgets.QGraphicsTextItem(f"Circuit {i+1}")
            label.setPos(50, circuit_y)
            circuit_group.addToGroup(label)

            # Devices on circuit
            if self.include_devices.isChecked():
                device_x = 150
                for j in range(5):  # Sample devices
                    device = self.draw_device(f"Device {j+1}", device_x, circuit_y)
                    circuit_group.addToGroup(device)
                    device_x += 80

            self.diagram_scene.addItem(circuit_group)
            circuit_y += 100

    def draw_panel(self, name, x, y, is_main=False):
        """Draw a panel box."""
        # Panel rectangle
        rect = QtWidgets.QGraphicsRectItem(x, y, 100, 80)
        color = QtCore.Qt.GlobalColor.blue if is_main else QtCore.Qt.GlobalColor.lightGray
        rect.setBrush(QtGui.QBrush(color))
        rect.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.black, 2))
        self.diagram_scene.addItem(rect)

        # Panel label
        text = QtWidgets.QGraphicsTextItem(name)
        text.setFont(QtGui.QFont("Arial", 10))
        text.setPos(x + 5, y + 30)
        self.diagram_scene.addItem(text)

        return rect

    def draw_device(self, name, x, y):
        """Draw a device symbol."""
        # Device circle
        circle = QtWidgets.QGraphicsEllipseItem(x, y, 30, 30)
        circle.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.white))
        circle.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.black, 1))
        self.diagram_scene.addItem(circle)

        # Device label
        text = QtWidgets.QGraphicsTextItem(name[:3])  # Abbreviated name
        text.setFont(QtGui.QFont("Arial", 8))
        text.setPos(x + 5, y + 10)
        self.diagram_scene.addItem(text)

        return circle

    def draw_connections(self):
        """Draw connection lines between panels."""
        # Sample connections
        lines = [(150, 140, 150, 290), (150, 140, 300, 290), (150, 140, 450, 290)]

        for x1, y1, x2, y2 in lines:
            line = QtWidgets.QGraphicsLineItem(x1, y1, x2, y2)
            pen = QtGui.QPen(QtCore.Qt.GlobalColor.black, 1, QtCore.Qt.PenStyle.DashLine)
            line.setPen(pen)
            self.diagram_scene.addItem(line)

    def export_diagram(self):
        """Export the diagram to an image file."""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Riser Diagram", "", "PNG Files (*.png);;SVG Files (*.svg);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Create pixmap of the scene
            rect = self.diagram_scene.itemsBoundingRect()
            pixmap = QtGui.QPixmap(int(rect.width()), int(rect.height()))
            pixmap.fill(QtCore.Qt.GlobalColor.white)

            # Render scene to pixmap
            painter = QtGui.QPainter(pixmap)
            self.diagram_scene.render(painter, QtCore.QRectF(), rect)
            painter.end()

            # Save pixmap
            if pixmap.save(file_path, "PNG"):
                QtWidgets.QMessageBox.information(
                    self, "Export Success", f"Diagram exported successfully to {file_path}"
                )
            else:
                QtWidgets.QMessageBox.critical(self, "Export Error", "Failed to save diagram.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Export Error", f"Failed to export diagram: {str(e)}"
            )
