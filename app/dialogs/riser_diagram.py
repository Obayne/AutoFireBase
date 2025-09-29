from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QPushButton, QSpinBox, QComboBox
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor

import math


class RiserDiagramDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Riser Diagram Generator")
        self.setMinimumSize(900, 800)

        layout = QVBoxLayout(self)

        # Configuration panel
        config_group = QGroupBox("Building Configuration")
        config_layout = QHBoxLayout(config_group)

        # Building parameters
        config_layout.addWidget(QLabel("Floors:"))
        self.floor_count = QSpinBox()
        self.floor_count.setRange(1, 50)
        self.floor_count.setValue(5)
        self.floor_count.valueChanged.connect(self._update_diagram)
        config_layout.addWidget(self.floor_count)

        config_layout.addWidget(QLabel("Basement Floors:"))
        self.basement_count = QSpinBox()
        self.basement_count.setRange(0, 10)
        self.basement_count.setValue(1)
        self.basement_count.valueChanged.connect(self._update_diagram)
        config_layout.addWidget(self.basement_count)

        config_layout.addWidget(QLabel("Building Type:"))
        self.building_type = QComboBox()
        self.building_type.addItems([
            "Office Building", "Hotel", "Apartment", "Hospital", "School", "Warehouse", "Custom"
        ])
        self.building_type.currentTextChanged.connect(self._update_diagram)
        config_layout.addWidget(self.building_type)

        config_layout.addStretch()

        generate_btn = QPushButton("Generate Diagram")
        generate_btn.clicked.connect(self._generate_diagram)
        config_layout.addWidget(generate_btn)

        layout.addWidget(config_group)

        # Main content area
        content_layout = QHBoxLayout()

        # Diagram display
        diagram_group = QGroupBox("Riser Diagram")
        diagram_layout = QVBoxLayout(diagram_group)

        self.diagram_view = RiserDiagramView()
        diagram_layout.addWidget(self.diagram_view)

        content_layout.addWidget(diagram_group, 2)  # 2/3 width

        # Equipment panel
        equipment_group = QGroupBox("Equipment Schedule")
        equipment_layout = QVBoxLayout(equipment_group)

        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(4)
        self.equipment_table.setHorizontalHeaderLabels([
            "Floor", "Equipment Type", "Location", "Notes"
        ])
        self.equipment_table.horizontalHeader().setStretchLastSection(True)
        self.equipment_table.setAlternatingRowColors(True)

        equipment_layout.addWidget(self.equipment_table)

        content_layout.addWidget(equipment_group, 1)  # 1/3 width

        layout.addLayout(content_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        export_btn = QPushButton("Export Diagram")
        export_btn.clicked.connect(self._export_diagram)
        button_layout.addWidget(export_btn)

        print_btn = QPushButton("Print")
        print_btn.clicked.connect(self._print_diagram)
        button_layout.addWidget(print_btn)

        button_layout.addStretch()

        ok_btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        ok_btn.accepted.connect(self.accept)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # Initialize
        self._generate_diagram()

    def _generate_diagram(self):
        """Generate the riser diagram based on current settings"""
        floors = self.floor_count.value()
        basements = self.basement_count.value()
        building_type = self.building_type.currentText()

        # Generate equipment schedule
        self._generate_equipment_schedule(floors, basements, building_type)

        # Update diagram view
        self.diagram_view.set_building_config(floors, basements, building_type)
        self.diagram_view.update()

    def _generate_equipment_schedule(self, floors, basements, building_type):
        """Generate equipment schedule for the riser diagram"""
        equipment = []

        # FACP is typically in basement or first floor
        facp_floor = "Basement" if basements > 0 else "1st Floor"
        equipment.append([facp_floor, "Fire Alarm Control Panel (FACP)", "Electrical Room", "Main system controller"])

        # Batteries with FACP
        equipment.append([facp_floor, "Backup Batteries", "Electrical Room", "24V system batteries"])

        # Generator if required
        if building_type in ["Hospital", "Hotel", "Apartment"]:
            equipment.append([facp_floor, "Emergency Generator", "Exterior", "Automatic transfer switch"])

        # Annunciator panels
        equipment.append(["Lobby/Main Entrance", "Annunciator Panel", "Security Desk", "System status display"])

        # Floor equipment
        for floor_num in range(-basements + 1, floors + 1):
            if floor_num <= 0:
                floor_name = f"B{abs(floor_num)}" if floor_num < 0 else "Ground"
            else:
                floor_name = f"{floor_num}{'st' if floor_num == 1 else 'nd' if floor_num == 2 else 'rd' if floor_num == 3 else 'th'} Floor"

            # Smoke detectors (typical: 1 per 900 sq ft)
            equipment.append([floor_name, "Smoke Detectors", "Throughout", "~20-30 detectors per floor"])

            # Heat detectors in some areas
            if building_type in ["Warehouse", "Hospital"]:
                equipment.append([floor_name, "Heat Detectors", "Storage/Kitchen", "Rate-of-rise detectors"])

            # Strobes (visible notification)
            equipment.append([floor_name, "Strobe Lights", "Corridors/Exits", "Wall/ceiling mounted"])

            # Speakers (audible notification)
            equipment.append([floor_name, "Speakers", "Corridors/Public Areas", "Voice evacuation system"])

            # Pull stations
            equipment.append([floor_name, "Manual Pull Stations", "Exit Doors", "Red break-glass stations"])

            # Floor control panel (if required)
            if floors > 10:  # High-rise buildings
                equipment.append([floor_name, "Floor Repeater Panel", "Elevator Lobby", "Floor status display"])

        # Roof equipment
        equipment.append(["Roof", "Antenna", "Roof Top", "Radio communication backup"])

        # Populate table
        self.equipment_table.setRowCount(len(equipment))
        for row, (floor, equip_type, location, notes) in enumerate(equipment):
            self.equipment_table.setItem(row, 0, QTableWidgetItem(floor))
            self.equipment_table.setItem(row, 1, QTableWidgetItem(equip_type))
            self.equipment_table.setItem(row, 2, QTableWidgetItem(location))
            self.equipment_table.setItem(row, 3, QTableWidgetItem(notes))

    def _update_diagram(self):
        """Update diagram when parameters change"""
        self._generate_diagram()

    def _export_diagram(self):
        """Export diagram to file"""
        # TODO: Implement diagram export
        QtWidgets.QMessageBox.information(self, "Export", "Diagram export will be implemented here.")

    def _print_diagram(self):
        """Print the riser diagram"""
        # TODO: Implement printing
        QtWidgets.QMessageBox.information(self, "Print", "Printing will be implemented here.")


class RiserDiagramView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.floors = 5
        self.basements = 1
        self.building_type = "Office Building"

        # Set minimum size
        self.setMinimumSize(600, 400)

    def set_building_config(self, floors, basements, building_type):
        self.floors = floors
        self.basements = basements
        self.building_type = building_type

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Calculate layout
        total_floors = self.floors + self.basements
        floor_height = height / (total_floors + 2)  # +2 for margins
        riser_width = width * 0.8
        riser_x = (width - riser_width) / 2

        # Draw building outline
        self._draw_building_outline(painter, riser_x, floor_height, riser_width, height)

        # Draw floors
        self._draw_floors(painter, riser_x, floor_height, riser_width, total_floors)

        # Draw equipment symbols
        self._draw_equipment(painter, riser_x, floor_height, riser_width, total_floors)

        # Draw riser backbone
        self._draw_riser_backbone(painter, riser_x + riser_width/2, floor_height, height)

    def _draw_building_outline(self, painter, x, floor_height, width, height):
        """Draw the building outline"""
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(QColor(240, 240, 240)))

        # Building rectangle
        building_rect = QRectF(x - 20, floor_height, width + 40, height - 2*floor_height)
        painter.drawRect(building_rect)

        # Title
        painter.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        title_rect = QRectF(x, floor_height/2, width, floor_height)
        painter.drawText(title_rect, Qt.AlignCenter, f"{self.building_type} Riser Diagram")

    def _draw_floors(self, painter, x, floor_height, width, total_floors):
        """Draw floor lines and labels"""
        painter.setFont(QtGui.QFont("Arial", 10))

        for i in range(total_floors):
            y = (i + 1) * floor_height + floor_height

            # Floor line
            painter.setPen(QPen(Qt.gray, 1, Qt.DashLine))
            painter.drawLine(int(x), int(y), int(x + width), int(y))

            # Floor label
            floor_num = i - self.basements + 1
            if floor_num <= 0:
                floor_label = f"B{abs(floor_num)}" if floor_num < 0 else "Ground"
            else:
                floor_label = f"{floor_num}"

            # Label on left side
            label_rect = QRectF(x - 60, y - floor_height/2, 50, floor_height)
            painter.setPen(QPen(Qt.black, 1))
            painter.drawText(label_rect, Qt.AlignRight | Qt.AlignVCenter, floor_label)

    def _draw_equipment(self, painter, x, floor_height, width, total_floors):
        """Draw equipment symbols on each floor"""
        symbol_size = min(floor_height * 0.6, 20)

        for i in range(total_floors):
            y = (i + 1.5) * floor_height + floor_height

            # FACP on first floor or basement
            if i == self.basements:  # Ground/first floor
                self._draw_fACP_symbol(painter, x + width * 0.1, y, symbol_size)

            # Detectors throughout
            self._draw_detector_symbol(painter, x + width * 0.3, y, symbol_size)

            # Strobes
            self._draw_strobe_symbol(painter, x + width * 0.5, y, symbol_size)

            # Pull stations at exits
            self._draw_pull_station_symbol(painter, x + width * 0.7, y, symbol_size)

    def _draw_fACP_symbol(self, painter, x, y, size):
        """Draw FACP symbol (rectangle with text)"""
        painter.setPen(QPen(Qt.blue, 2))
        painter.setBrush(QBrush(QColor(200, 220, 255)))
        rect = QRectF(x - size/2, y - size/2, size, size)
        painter.drawRect(rect)

        painter.setFont(QtGui.QFont("Arial", 8))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawText(rect, Qt.AlignCenter, "FACP")

    def _draw_detector_symbol(self, painter, x, y, size):
        """Draw smoke detector symbol (circle)"""
        painter.setPen(QPen(Qt.red, 2))
        painter.setBrush(QBrush(QColor(255, 200, 200)))
        painter.drawEllipse(int(x - size/2), int(y - size/2), int(size), int(size))

    def _draw_strobe_symbol(self, painter, x, y, size):
        """Draw strobe symbol (triangle)"""
        painter.setPen(QPen(Qt.green, 2))
        painter.setBrush(QBrush(QColor(200, 255, 200)))

        # Triangle points
        points = [
            QPointF(x, y - size/2),
            QPointF(x - size/2, y + size/2),
            QPointF(x + size/2, y + size/2)
        ]
        painter.drawPolygon(points)

    def _draw_pull_station_symbol(self, painter, x, y, size):
        """Draw pull station symbol (square)"""
        painter.setPen(QPen(Qt.orange, 2))
        painter.setBrush(QBrush(QColor(255, 235, 200)))
        rect = QRectF(x - size/2, y - size/2, size, size)
        painter.drawRect(rect)

        # Handle
        painter.drawLine(int(x - size/4), int(y), int(x + size/4), int(y))

    def _draw_riser_backbone(self, painter, x, y_start, height):
        """Draw the main riser cable backbone"""
        painter.setPen(QPen(Qt.black, 3))
        painter.drawLine(int(x), int(y_start), int(x), int(height - y_start))

        # Cable label
        painter.setFont(QtGui.QFont("Arial", 8))
        painter.setPen(QPen(Qt.black, 1))
        label_rect = QRectF(x + 5, height/2 - 20, 100, 40)
        painter.drawText(label_rect, Qt.AlignLeft | Qt.AlignVCenter, "Main\nRiser\nCable")