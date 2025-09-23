"""
Fire Alarm Toolbar for AutoFire Application.
Provides quick access to fire alarm specific tools and device placement.
"""

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor, QIcon, QPixmap
from typing import Optional, Callable

class FireAlarmToolbar(QtWidgets.QToolBar):
    """Fire alarm specific toolbar with device placement and system tools."""
    
    # Signals
    device_selected = QtCore.Signal(str, str, str, str)  # symbol, name, manufacturer, part_number
    tool_selected = QtCore.Signal(str)  # tool name
    circuit_selected = QtCore.Signal(int)  # circuit_id
    panel_selected = QtCore.Signal(str)  # panel model
    
    def __init__(self, parent=None):
        super().__init__("Fire Alarm", parent)
        self.setWindowTitle("Fire Alarm Toolbar")
        self.setMovable(True)
        self.setFloatable(True)
        self.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea | Qt.ToolBarArea.BottomToolBarArea)
        
        # Fire alarm tools (without device buttons since we have a dedicated device dock)
        self._create_tool_buttons()
        
        # Add separator
        self.addSeparator()
        
        # Circuit selection
        self._create_circuit_controls()
        
        # Add separator
        self.addSeparator()
        
        # System status
        self._create_status_widgets()
        
    def _create_tool_buttons(self):
        """Create buttons for fire alarm specific tools."""
        tools = [
            {"name": "SLC Wiring", "icon": "slc", "tool": "slc_wire"},
            {"name": "NAC Wiring", "icon": "nac", "tool": "nac_wire"},
            {"name": "Address Assign", "icon": "address", "tool": "assign_address"}
            # Removed BOM Gen and Circuit Calc from toolbar since they're now in separate menus
        ]
        
        for tool in tools:
            action = QtGui.QAction(tool["name"], self)
            action.setData(tool["tool"])
            # Use a closure to capture the tool data
            def make_handler(tool_name):
                return lambda checked: self.tool_selected.emit(tool_name)
            action.triggered.connect(make_handler(tool["tool"]))
            self.addAction(action)
            
    def _create_circuit_controls(self):
        """Create circuit selection controls."""
        # Circuit selector
        self.circuit_label = QtWidgets.QLabel("Circuit:")
        self.addWidget(self.circuit_label)
        
        self.circuit_combo = QtWidgets.QComboBox()
        self.circuit_combo.addItem("SLC-1", 1)
        self.circuit_combo.addItem("SLC-2", 2)
        self.circuit_combo.addItem("SLC-3", 3)
        self.circuit_combo.addItem("NAC-1", 101)
        self.circuit_combo.addItem("NAC-2", 102)
        self.circuit_combo.currentIndexChanged.connect(self._on_circuit_changed)
        self.addWidget(self.circuit_combo)
        
    def _create_status_widgets(self):
        """Create system status widgets."""
        # Device count
        self.device_count_label = QtWidgets.QLabel("Devices: 0")
        self.device_count_label.setStyleSheet("QLabel { padding: 0 10px; }")
        self.addWidget(self.device_count_label)
        
        # Circuit status
        self.circuit_status_label = QtWidgets.QLabel("Circuit: SLC-1")
        self.circuit_status_label.setStyleSheet("QLabel { padding: 0 10px; }")
        self.addWidget(self.circuit_status_label)
        
    def _on_circuit_changed(self, index):
        """Handle circuit selection change."""
        circuit_id = self.circuit_combo.currentData()
        if circuit_id is not None:
            self.circuit_selected.emit(int(circuit_id))
            circuit_name = self.circuit_combo.currentText()
            self.circuit_status_label.setText(f"Circuit: {circuit_name}")
            
    def update_device_count(self, count: int):
        """Update the device count display."""
        self.device_count_label.setText(f"Devices: {count}")
        
    def add_circuit(self, circuit_id: int, circuit_name: str):
        """Add a new circuit to the selector."""
        self.circuit_combo.addItem(circuit_name, circuit_id)
        
    def set_current_circuit(self, circuit_id: int):
        """Set the current circuit."""
        index = self.circuit_combo.findData(circuit_id)
        if index >= 0:
            self.circuit_combo.setCurrentIndex(index)