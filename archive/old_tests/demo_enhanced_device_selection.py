#!/usr/bin/env python3
"""
🔥 FlameCAD Enhanced Device Selection Demo
Replaces simple quantity inputs with database-driven device selection interface.
"""

import sqlite3
import os
import sys
from typing import List, Dict, Any

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
        QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QListWidget, 
        QListWidgetItem, QGroupBox, QSpinBox, QFrame, QScrollArea,
        QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
        QSplitter, QTextEdit, QCheckBox
    )
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QFont, QPixmap, QPainter, QColor
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from frontend.design_system import (
        AutoFireColor, AutoFireStyleSheet, AutoFireTypography, 
        AutoFireSpacing, apply_autofire_theme
    )
except ImportError:
    # Fallback if design system not available
    class AutoFireColor:
        PRIMARY = "#FF4444"
        BACKGROUND = "#1A1A1A" 
        TEXT_PRIMARY = "#FFFFFF"
        CIRCUIT_SLC = "#DC3545"  # Red
        CIRCUIT_NAC = "#FFC107"  # Yellow
        CIRCUIT_POWER = "#FF6B35"  # Orange


class DeviceSelectionWidget(QWidget):
    """Enhanced device selection widget with database browsing."""
    
    device_selected = Signal(dict, int)  # device_info, quantity
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.device_catalog = self._load_device_catalog()
        self.selected_devices = {}  # device_id -> quantity
        self._setup_ui()
        self._load_devices()
    
    def _setup_ui(self):
        """Setup the enhanced device selection interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(AutoFireSpacing.MEDIUM)
        
        # Header
        header = QLabel("🔥 Device Selection - FlameCAD Professional")
        header.setStyleSheet(f"""
            QLabel {{
                color: {AutoFireColor.PRIMARY.value};
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                background-color: {AutoFireColor.SURFACE_PRIMARY.value};
                border-radius: 8px;
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(header)
        
        # Main content in splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Device catalog browser
        catalog_widget = self._create_catalog_browser()
        splitter.addWidget(catalog_widget)
        
        # Right side - Selected devices
        selection_widget = self._create_selection_panel()
        splitter.addWidget(selection_widget)
        
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)
        
        # Apply styling
        if PYSIDE6_AVAILABLE:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {AutoFireColor.BACKGROUND.value};
                    color: {AutoFireColor.TEXT_PRIMARY.value};
                }}
            """)
    
    def _create_catalog_browser(self):
        """Create the device catalog browser panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search and filter controls
        controls_frame = QFrame()
        controls_layout = QGridLayout(controls_frame)
        
        # Search box
        search_label = QLabel("🔍 Search Devices:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter device name, model, or manufacturer...")
        self.search_box.textChanged.connect(self._filter_devices)
        
        # Filter by type
        type_label = QLabel("📂 Device Type:")
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types", "")
        self.type_filter.currentTextChanged.connect(self._filter_devices)
        
        # Filter by manufacturer
        mfg_label = QLabel("🏭 Manufacturer:")
        self.mfg_filter = QComboBox()
        self.mfg_filter.addItem("All Manufacturers", "")
        self.mfg_filter.currentTextChanged.connect(self._filter_devices)
        
        # Circuit type filter
        circuit_label = QLabel("⚡ Circuit Type:")
        self.circuit_filter = QComboBox()
        circuit_items = [
            ("All Circuits", ""),
            ("🔴 SLC Devices", "SLC"),
            ("🟡 NAC Devices", "NAC"), 
            ("🟠 Power Devices", "POWER")
        ]
        for name, value in circuit_items:
            self.circuit_filter.addItem(name, value)
        self.circuit_filter.currentTextChanged.connect(self._filter_devices)
        
        controls_layout.addWidget(search_label, 0, 0)
        controls_layout.addWidget(self.search_box, 0, 1)
        controls_layout.addWidget(type_label, 1, 0)
        controls_layout.addWidget(self.type_filter, 1, 1)
        controls_layout.addWidget(mfg_label, 2, 0)
        controls_layout.addWidget(self.mfg_filter, 2, 1)
        controls_layout.addWidget(circuit_label, 3, 0)
        controls_layout.addWidget(self.circuit_filter, 3, 1)
        
        if PYSIDE6_AVAILABLE:
            controls_frame.setStyleSheet(AutoFireStyleSheet.group_box())
        
        layout.addWidget(controls_frame)
        
        # Device list with details
        devices_group = QGroupBox("Available Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        # Device table
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(6)
        self.device_table.setHorizontalHeaderLabels([
            "Device", "Model", "Manufacturer", "Type", "Circuit", "Add"
        ])
        
        # Configure table
        header = self.device_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Device name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Model
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Manufacturer
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Circuit
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Add button
        self.device_table.setColumnWidth(5, 120)
        
        self.device_table.setAlternatingRowColors(True)
        
        if PYSIDE6_AVAILABLE:
            self.device_table.setStyleSheet(f"""
                QTableWidget {{
                    background-color: {AutoFireColor.SURFACE_PRIMARY.value};
                    color: {AutoFireColor.TEXT_PRIMARY.value};
                    gridline-color: {AutoFireColor.BORDER_PRIMARY.value};
                    border: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
                    border-radius: 6px;
                }}
                QTableWidget::item {{
                    padding: 8px;
                    border: none;
                }}
                QTableWidget::item:selected {{
                    background-color: {AutoFireColor.ACCENT.value};
                }}
                QHeaderView::section {{
                    background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                    color: {AutoFireColor.TEXT_PRIMARY.value};
                    padding: 8px;
                    border: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
                    font-weight: bold;
                }}
            """)
        
        devices_layout.addWidget(self.device_table)
        
        if PYSIDE6_AVAILABLE:
            devices_group.setStyleSheet(AutoFireStyleSheet.group_box())
        
        layout.addWidget(devices_group)
        
        return widget
    
    def _create_selection_panel(self):
        """Create the selected devices panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Selected devices group
        selection_group = QGroupBox("Selected Devices")
        selection_layout = QVBoxLayout(selection_group)
        
        # Stats display
        self.stats_label = QLabel("📊 No devices selected")
        self.stats_label.setWordWrap(True)
        if PYSIDE6_AVAILABLE:
            self.stats_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                    color: {AutoFireColor.TEXT_PRIMARY.value};
                    padding: 10px;
                    border-radius: 6px;
                    font-weight: bold;
                }}
            """)
        selection_layout.addWidget(self.stats_label)
        
        # Selected devices list
        self.selected_list = QTableWidget()
        self.selected_list.setColumnCount(4)
        self.selected_list.setHorizontalHeaderLabels(["Device", "Qty", "Circuit", "Remove"])
        
        header = self.selected_list.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.selected_list.setColumnWidth(1, 60)
        self.selected_list.setColumnWidth(3, 80)
        
        if PYSIDE6_AVAILABLE:
            self.selected_list.setStyleSheet(f"""
                QTableWidget {{
                    background-color: {AutoFireColor.SURFACE_PRIMARY.value};
                    color: {AutoFireColor.TEXT_PRIMARY.value};
                    gridline-color: {AutoFireColor.BORDER_PRIMARY.value};
                    border: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
                    border-radius: 6px;
                }}
                QTableWidget::item {{
                    padding: 6px;
                    border: none;
                }}
                QHeaderView::section {{
                    background-color: {AutoFireColor.SURFACE_SECONDARY.value};
                    color: {AutoFireColor.TEXT_PRIMARY.value};
                    padding: 6px;
                    border: 1px solid {AutoFireColor.BORDER_PRIMARY.value};
                    font-weight: bold;
                }}
            """)
        
        selection_layout.addWidget(self.selected_list)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("🗑️ Clear All")
        self.clear_btn.clicked.connect(self._clear_selection)
        
        self.export_btn = QPushButton("📤 Export to Palette")
        self.export_btn.clicked.connect(self._export_to_palette)
        
        if PYSIDE6_AVAILABLE:
            self.clear_btn.setStyleSheet(AutoFireStyleSheet.button_secondary())
            self.export_btn.setStyleSheet(AutoFireStyleSheet.button_primary())
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.export_btn)
        selection_layout.addLayout(buttons_layout)
        
        if PYSIDE6_AVAILABLE:
            selection_group.setStyleSheet(AutoFireStyleSheet.group_box())
        
        layout.addWidget(selection_group)
        
        return widget
    
    def _load_device_catalog(self):
        """Load device catalog from database."""
        try:
            db_path = os.path.join(os.path.dirname(__file__), "autofire.db")
            if not os.path.exists(db_path):
                # Try alternative path
                db_path = os.path.join(os.path.dirname(__file__), "..", "autofire.db")
            
            if not os.path.exists(db_path):
                print(f"Database not found at {db_path}, using fallback devices")
                return self._get_fallback_devices()
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT d.id, m.name as manufacturer, dt.code as type, d.model, d.name, d.symbol
                FROM devices d
                LEFT JOIN manufacturers m ON m.id = d.manufacturer_id  
                LEFT JOIN device_types dt ON dt.id = d.type_id
                WHERE d.name IS NOT NULL AND d.name != ''
                ORDER BY m.name, dt.code, d.name
            """)
            
            devices = []
            for row in cursor.fetchall():
                device = {
                    "id": row[0],
                    "manufacturer": row[1] or "Unknown",
                    "type": row[2] or "Unknown", 
                    "model": row[3] or "",
                    "name": row[4] or "Unnamed Device",
                    "symbol": row[5] or "?",
                    "circuit_type": self._determine_circuit_type(row[2], row[4])
                }
                devices.append(device)
            
            conn.close()
            print(f"Loaded {len(devices)} devices from database")
            return devices
            
        except Exception as e:
            print(f"Error loading device catalog: {e}")
            return self._get_fallback_devices()
    
    def _determine_circuit_type(self, device_type, device_name):
        """Determine circuit type based on device type and name."""
        if not device_type and not device_name:
            return "POWER"
        
        device_str = f"{device_type} {device_name}".lower()
        
        if any(x in device_str for x in ["smoke", "heat", "detector", "pull", "station", "monitor"]):
            return "SLC"
        elif any(x in device_str for x in ["horn", "strobe", "speaker", "beacon", "notification"]):
            return "NAC"
        elif any(x in device_str for x in ["panel", "power", "supply", "battery", "transformer"]):
            return "POWER"
        else:
            return "SLC"  # Default to SLC for initiating devices
    
    def _get_fallback_devices(self):
        """Fallback device list if database fails."""
        return [
            {
                "id": 1, "manufacturer": "Fire-Lite", "type": "Panel", "model": "NFS2-3030",
                "name": "Fire Alarm Control Panel", "symbol": "FACP", "circuit_type": "POWER"
            },
            {
                "id": 2, "manufacturer": "Fire-Lite", "type": "Detector", "model": "SD365",
                "name": "Photoelectric Smoke Detector", "symbol": "SD", "circuit_type": "SLC"
            },
            {
                "id": 3, "manufacturer": "Fire-Lite", "type": "Detector", "model": "HD135F",
                "name": "Fixed Temperature Heat Detector", "symbol": "HD", "circuit_type": "SLC"
            },
            {
                "id": 4, "manufacturer": "Fire-Lite", "type": "Station", "model": "BG12L",
                "name": "Manual Pull Station", "symbol": "PS", "circuit_type": "SLC"
            },
            {
                "id": 5, "manufacturer": "Fire-Lite", "type": "Notification", "model": "HSW",
                "name": "Horn/Strobe (Wall Mount)", "symbol": "HS", "circuit_type": "NAC"
            },
            {
                "id": 6, "manufacturer": "Fire-Lite", "type": "Notification", "model": "HSC",
                "name": "Horn/Strobe (Ceiling Mount)", "symbol": "HS", "circuit_type": "NAC"
            },
            {
                "id": 7, "manufacturer": "System Sensor", "type": "Detector", "model": "2151",
                "name": "Photoelectric Smoke Detector", "symbol": "SD", "circuit_type": "SLC"
            }
        ]
    
    def _load_devices(self):
        """Load devices into the catalog browser."""
        # Populate filter dropdowns
        types = set()
        manufacturers = set()
        
        for device in self.device_catalog:
            if device["type"]:
                types.add(device["type"])
            if device["manufacturer"]:
                manufacturers.add(device["manufacturer"])
        
        for device_type in sorted(types):
            self.type_filter.addItem(device_type, device_type)
        
        for manufacturer in sorted(manufacturers):
            self.mfg_filter.addItem(manufacturer, manufacturer)
        
        # Load initial device list
        self._populate_device_table(self.device_catalog)
    
    def _populate_device_table(self, devices):
        """Populate the device table with filtered devices."""
        self.device_table.setRowCount(len(devices))
        
        for row, device in enumerate(devices):
            # Device name
            name_item = QTableWidgetItem(device["name"])
            name_item.setData(Qt.UserRole, device)
            self.device_table.setItem(row, 0, name_item)
            
            # Model
            model_item = QTableWidgetItem(device["model"])
            self.device_table.setItem(row, 1, model_item)
            
            # Manufacturer
            mfg_item = QTableWidgetItem(device["manufacturer"])
            self.device_table.setItem(row, 2, mfg_item)
            
            # Type
            type_item = QTableWidgetItem(device["type"])
            self.device_table.setItem(row, 3, type_item)
            
            # Circuit type with color coding
            circuit_item = QTableWidgetItem(device["circuit_type"])
            circuit_color = self._get_circuit_color(device["circuit_type"])
            circuit_item.setBackground(QColor(circuit_color))
            self.device_table.setItem(row, 4, circuit_item)
            
            # Add button
            add_widget = QWidget()
            add_layout = QHBoxLayout(add_widget)
            add_layout.setContentsMargins(5, 2, 5, 2)
            
            qty_spin = QSpinBox()
            qty_spin.setMinimum(1)
            qty_spin.setMaximum(999)
            qty_spin.setValue(1)
            qty_spin.setFixedWidth(50)
            
            add_btn = QPushButton("Add")
            add_btn.setFixedWidth(50)
            add_btn.clicked.connect(lambda checked, d=device, s=qty_spin: self._add_device_to_selection(d, s.value()))
            
            if PYSIDE6_AVAILABLE:
                add_btn.setStyleSheet(AutoFireStyleSheet.button_success())
            
            add_layout.addWidget(qty_spin)
            add_layout.addWidget(add_btn)
            
            self.device_table.setCellWidget(row, 5, add_widget)
    
    def _get_circuit_color(self, circuit_type):
        """Get color for circuit type."""
        color_map = {
            "SLC": AutoFireColor.CIRCUIT_SLC.value,
            "NAC": AutoFireColor.CIRCUIT_NAC.value, 
            "POWER": AutoFireColor.CIRCUIT_POWER.value
        }
        return color_map.get(circuit_type, AutoFireColor.TEXT_SECONDARY.value)
    
    def _filter_devices(self):
        """Filter devices based on search criteria."""
        search_text = self.search_box.text().lower()
        type_filter = self.type_filter.currentData() or ""
        mfg_filter = self.mfg_filter.currentData() or ""
        circuit_filter = self.circuit_filter.currentData() or ""
        
        filtered_devices = []
        
        for device in self.device_catalog:
            # Search text filter
            if search_text:
                searchable = f"{device['name']} {device['model']} {device['manufacturer']}".lower()
                if search_text not in searchable:
                    continue
            
            # Type filter
            if type_filter and device["type"] != type_filter:
                continue
                
            # Manufacturer filter 
            if mfg_filter and device["manufacturer"] != mfg_filter:
                continue
            
            # Circuit filter
            if circuit_filter and device["circuit_type"] != circuit_filter:
                continue
            
            filtered_devices.append(device)
        
        self._populate_device_table(filtered_devices)
    
    def _add_device_to_selection(self, device, quantity):
        """Add device to selection with specified quantity."""
        device_id = device["id"]
        
        if device_id in self.selected_devices:
            self.selected_devices[device_id]["quantity"] += quantity
        else:
            self.selected_devices[device_id] = {
                "device": device,
                "quantity": quantity
            }
        
        self._update_selection_display()
        self.device_selected.emit(device, quantity)
    
    def _update_selection_display(self):
        """Update the selected devices display."""
        self.selected_list.setRowCount(len(self.selected_devices))
        
        total_devices = 0
        circuit_counts = {"SLC": 0, "NAC": 0, "POWER": 0}
        
        for row, (device_id, info) in enumerate(self.selected_devices.items()):
            device = info["device"]
            quantity = info["quantity"]
            total_devices += quantity
            circuit_counts[device["circuit_type"]] += quantity
            
            # Device name
            name_item = QTableWidgetItem(device["name"])
            self.selected_list.setItem(row, 0, name_item)
            
            # Quantity (editable)
            qty_spin = QSpinBox()
            qty_spin.setMinimum(1)
            qty_spin.setMaximum(999)
            qty_spin.setValue(quantity)
            qty_spin.valueChanged.connect(lambda val, did=device_id: self._update_quantity(did, val))
            self.selected_list.setCellWidget(row, 1, qty_spin)
            
            # Circuit type
            circuit_item = QTableWidgetItem(device["circuit_type"])
            circuit_color = self._get_circuit_color(device["circuit_type"])
            circuit_item.setBackground(QColor(circuit_color))
            self.selected_list.setItem(row, 2, circuit_item)
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda checked, did=device_id: self._remove_device(did))
            if PYSIDE6_AVAILABLE:
                remove_btn.setStyleSheet(AutoFireStyleSheet.button_secondary())
            self.selected_list.setCellWidget(row, 3, remove_btn)
        
        # Update stats
        stats_text = f"📊 Selected: {total_devices} total devices\n"
        stats_text += f"🔴 SLC: {circuit_counts['SLC']} devices\n"
        stats_text += f"🟡 NAC: {circuit_counts['NAC']} devices\n"
        stats_text += f"🟠 Power: {circuit_counts['POWER']} devices"
        
        self.stats_label.setText(stats_text)
    
    def _update_quantity(self, device_id, quantity):
        """Update quantity for a selected device."""
        if device_id in self.selected_devices:
            self.selected_devices[device_id]["quantity"] = quantity
            self._update_selection_display()
    
    def _remove_device(self, device_id):
        """Remove device from selection."""
        if device_id in self.selected_devices:
            del self.selected_devices[device_id]
            self._update_selection_display()
    
    def _clear_selection(self):
        """Clear all selected devices."""
        self.selected_devices.clear()
        self._update_selection_display()
    
    def _export_to_palette(self):
        """Export selected devices to device palette."""
        if not self.selected_devices:
            print("No devices selected to export")
            return
        
        print("🔥 Exporting to Device Palette:")
        for device_id, info in self.selected_devices.items():
            device = info["device"]
            quantity = info["quantity"]
            print(f"  • {device['name']} ({device['manufacturer']}) x{quantity} - {device['circuit_type']}")
        
        print("✅ Export complete - devices ready for placement")


class EnhancedDeviceSelectionDemo(QMainWindow):
    """Demo window for enhanced device selection."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 FlameCAD Enhanced Device Selection Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create device selection widget
        self.device_selector = DeviceSelectionWidget()
        self.device_selector.device_selected.connect(self._on_device_selected)
        
        self.setCentralWidget(self.device_selector)
        
        # Apply theme
        if PYSIDE6_AVAILABLE:
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {AutoFireColor.BACKGROUND.value};
                }}
            """)
    
    def _on_device_selected(self, device, quantity):
        """Handle device selection."""
        print(f"Device selected: {device['name']} x{quantity}")


def main():
    """Run the enhanced device selection demo."""
    if not PYSIDE6_AVAILABLE:
        print("❌ PySide6 not available. Please install: pip install PySide6")
        return
    
    print("🔥 Starting FlameCAD Enhanced Device Selection Demo...")
    
    app = QApplication(sys.argv)
    apply_autofire_theme(app)
    
    window = EnhancedDeviceSelectionDemo()
    window.show()
    
    print("✅ Demo launched successfully!")
    print("\nFeatures demonstrated:")
    print("• Database-driven device catalog browsing")
    print("• Advanced filtering (search, type, manufacturer, circuit)")
    print("• Circuit color coding (SLC=Red, NAC=Yellow, Power=Orange)")
    print("• Quantity selection with live statistics")
    print("• Professional FlameCAD dark theme")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()