"""
Fire Alarm Integrator for AutoFire Application.
Integrates fire alarm specific functionality with the main CAD application.
"""

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from typing import Optional, Dict, Any
import json
import os

from .fire_alarm_toolbar import FireAlarmToolbar
from .fire_alarm_status import SystemStatusWidget
from backend.fire_alarm_system import FireAlarmSystemManager
from frontend.wire_tool import WireDrawingTool, SLCAddressingDialog

class FireAlarmIntegrator(QtCore.QObject):
    """Integrator for fire alarm functionality with main application."""
    
    # Signals
    device_placed = QtCore.Signal(object)  # DeviceItem
    wire_created = QtCore.Signal(object)   # WireItem
    circuit_updated = QtCore.Signal(int)   # circuit_id
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.fire_alarm_manager: Optional[FireAlarmSystemManager] = None
        self.toolbar: Optional[FireAlarmToolbar] = None
        self.status_widget: Optional[SystemStatusWidget] = None
        self.current_project_id: Optional[str] = None
        self.current_circuit_id: int = 1  # Default to first SLC circuit
        self.wire_tool: Optional[WireDrawingTool] = None
        
        # Initialize fire alarm system
        self._initialize_fire_alarm_system()
        
        # Create and integrate UI components
        self._create_toolbar()
        self._create_status_widget()
        
        # Initialize wire drawing tool
        self._initialize_wire_tool()
        
        # Connect signals
        self._connect_signals()
        
    def _initialize_fire_alarm_system(self):
        """Initialize the fire alarm system manager."""
        try:
            self.fire_alarm_manager = FireAlarmSystemManager()
        except Exception as e:
            print(f"Failed to initialize fire alarm system: {e}")
            
    def _initialize_wire_tool(self):
        """Initialize the wire drawing tool."""
        try:
            if self.main_window and self.main_window.view:
                self.wire_tool = WireDrawingTool(self.main_window.view, self.fire_alarm_manager.slc_system if self.fire_alarm_manager else None)
                # Connect wire tool signals
                if self.wire_tool:
                    self.wire_tool.connection_created.connect(self._on_wire_connection_created)
                    self.wire_tool.addressing_requested.connect(self._on_addressing_requested)
        except Exception as e:
            print(f"Failed to initialize wire drawing tool: {e}")
            
    def _create_toolbar(self):
        """Create and add the fire alarm toolbar to the main window."""
        if not self.main_window:
            return
            
        self.toolbar = FireAlarmToolbar(self.main_window)
        self.main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
    def _create_menus(self):
        """Create fire alarm specific menus."""
        if not self.main_window:
            return
            
        menubar = self.main_window.menuBar()
        
        # Fire Alarm menu
        fire_alarm_menu = menubar.addMenu("&Fire Alarm")
        
        # Device placement submenu
        device_menu = fire_alarm_menu.addMenu("Devices")
        # Add device actions here
        
        # Tools submenu
        tools_menu = fire_alarm_menu.addMenu("Tools")
        tools_menu.addAction("SLC Wiring", lambda: self._activate_wiring_tool("SLC"))
        tools_menu.addAction("NAC Wiring", lambda: self._activate_wiring_tool("NAC"))
        tools_menu.addAction("Address Assignment", self._show_address_assignment)
        
        # Calculations submenu
        calc_menu = fire_alarm_menu.addMenu("Calculations")
        calc_menu.addAction("Circuit Calculations", self._perform_circuit_calculations)
        
        # Reports menu (separate from CAD features)
        reports_menu = menubar.addMenu("&Reports")
        reports_menu.addAction("Bill of Materials", self._generate_bom)
        reports_menu.addAction("Device Schedule", self.main_window.export_device_schedule_csv)
        # Add more report generation options here
        
    def _create_status_widget(self):
        """Create and dock the fire alarm status widget."""
        if not self.main_window:
            return
            
        self.status_widget = SystemStatusWidget(self.main_window)
        
        # Create dock widget
        dock = QtWidgets.QDockWidget("Fire Alarm Status", self.main_window)
        dock.setWidget(self.status_widget)
        self.main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        
    def _connect_signals(self):
        """Connect all signals between components."""
        if not self.toolbar:
            return
            
        # Device selection from toolbar
        self.toolbar.device_selected.connect(self._on_device_selected)
        
        # Tool selection from toolbar
        self.toolbar.tool_selected.connect(self._on_tool_selected)
        
        # Circuit selection from toolbar
        self.toolbar.circuit_selected.connect(self._on_circuit_selected)
        
    def _on_device_selected(self, symbol: str, name: str, manufacturer: str, part_number: str):
        """Handle device selection from toolbar."""
        # Set the current device in the main view
        device_proto = {
            "symbol": symbol,
            "name": name,
            "manufacturer": manufacturer,
            "part_number": part_number,
            "device_type": self._get_device_type_from_symbol(symbol)
        }
        
        self.main_window.view.set_current_device(device_proto)
        self.main_window.statusBar().showMessage(f"Selected: {name} ({symbol})")
        
    def _on_tool_selected(self, tool_name: str):
        """Handle tool selection from toolbar."""
        self.main_window.statusBar().showMessage(f"Selected tool: {tool_name}")
        
        # Handle specific tools
        if tool_name == "slc_wire":
            # Activate SLC wiring tool
            self._activate_wiring_tool("SLC")
        elif tool_name == "nac_wire":
            # Activate NAC wiring tool
            self._activate_wiring_tool("NAC")
        elif tool_name == "assign_address":
            # Show address assignment dialog
            self._show_address_assignment()
        elif tool_name == "circuit_calc":
            # Perform circuit calculations
            self._perform_circuit_calculations()
        elif tool_name == "generate_bom":
            # Generate bill of materials
            self._generate_bom()
            
    def _on_circuit_selected(self, circuit_id: int):
        """Handle circuit selection from toolbar."""
        self.current_circuit_id = circuit_id
        self.circuit_updated.emit(circuit_id)
        self.main_window.statusBar().showMessage(f"Selected circuit: {circuit_id}")
        
    def _get_device_type_from_symbol(self, symbol: str) -> str:
        """Determine device type from symbol."""
        symbol_types = {
            "SD": "Detector",
            "HD": "Detector",
            "S": "Notification",
            "HS": "Notification",
            "SPK": "Notification",
            "PS": "Initiating",
            "FACP": "Control"
        }
        return symbol_types.get(symbol, "Unknown")
        
    def _activate_wiring_tool(self, wire_type: str):
        """Activate the wiring tool for specific wire type."""
        if self.wire_tool:
            self.wire_tool.activate()
            self.main_window.statusBar().showMessage(f"Activated {wire_type} wiring tool - Click on devices to connect")
        else:
            # Fallback to existing wire mode
            self.main_window._set_wire_mode()
            self.main_window.statusBar().showMessage(f"Activated {wire_type} wiring tool")
        
    def _show_address_assignment(self):
        """Show address assignment dialog."""
        # This would show a dialog for assigning addresses to devices
        QtWidgets.QMessageBox.information(
            self.main_window, 
            "Address Assignment", 
            "Address assignment tool would open here"
        )
        
    def _perform_circuit_calculations(self):
        """Perform circuit calculations."""
        if not self.fire_alarm_manager or not self.current_project_id:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                "Circuit Calculations",
                "No project loaded or fire alarm system not initialized"
            )
            return
            
        try:
            # This would perform actual circuit calculations
            calculations = self.fire_alarm_manager.calculate_system_performance()
            QtWidgets.QMessageBox.information(
                self.main_window,
                "Circuit Calculations",
                f"Performed circuit calculations. Results: {json.dumps(calculations, indent=2)}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.main_window,
                "Circuit Calculations Error",
                f"Failed to perform circuit calculations: {str(e)}"
            )
            
    def _generate_bom(self):
        """Generate bill of materials."""
        if not self.fire_alarm_manager or not self.current_project_id:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                "Bill of Materials",
                "No project loaded or fire alarm system not initialized"
            )
            return
            
        try:
            # This would generate an actual BOM
            bom = self.fire_alarm_manager.generate_project_bom()
            QtWidgets.QMessageBox.information(
                self.main_window,
                "Bill of Materials",
                f"Generated BOM with {len(bom.sections) if hasattr(bom, 'sections') else 'N/A'} sections"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.main_window,
                "BOM Generation Error",
                f"Failed to generate bill of materials: {str(e)}"
            )
            
    def _on_wire_connection_created(self, connection):
        """Handle wire connection creation."""
        # Update system status
        self.update_system_status()
        
        # Update device connection indicators
        if hasattr(connection, 'from_device') and connection.from_device:
            connection.from_device._update_connection_status()
        if hasattr(connection, 'to_device') and connection.to_device:
            connection.to_device._update_connection_status()

    def _on_addressing_requested(self, from_device, to_device):
        """Handle SLC addressing request when connecting devices."""
        if not self.fire_alarm_manager:
            # Fallback to simple addressing if no fire alarm manager
            self._handle_simple_addressing(from_device, to_device)
            return
            
        # Show addressing dialog
        dialog = SLCAddressingDialog(
            self.main_window, 
            from_device, 
            to_device, 
            self.fire_alarm_manager.slc_system if self.fire_alarm_manager else None
        )
        
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            circuit_id, address = dialog.get_assignment()
            if circuit_id and address:
                # Here we would update the connection with addressing info
                self.main_window.statusBar().showMessage(f"Assigned address {address} on circuit {circuit_id}")
                
                # Find the connection in the wire tool
                if self.wire_tool:
                    connection = self.wire_tool.get_connection_by_devices(from_device, to_device)
                    if connection:
                        # Update the connection with addressing info
                        self.wire_tool.update_slc_addressing(connection, circuit_id, address)
                        
                        # Update devices with addressing information
                        if hasattr(to_device, 'set_slc_address'):
                            to_device.set_slc_address(address)
                        if hasattr(to_device, 'set_circuit_id'):
                            to_device.set_circuit_id(circuit_id)
                            
                        # Update the device's label to show the address
                        if hasattr(to_device, 'set_label_text'):
                            to_device.set_label_text(f"{to_device.name} (Addr: {address})")

    def _handle_simple_addressing(self, from_device, to_device):
        """Handle simple addressing when no fire alarm manager is available."""
        # Show a simple dialog for manual address assignment
        dialog = QtWidgets.QDialog(self.main_window)
        dialog.setWindowTitle("Device Address Assignment")
        dialog.setModal(True)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Connection info
        info_group = QtWidgets.QGroupBox("Connection Information")
        info_layout = QtWidgets.QFormLayout(info_group)
        info_layout.addRow("From Device:", QtWidgets.QLabel(getattr(from_device, 'name', 'Unknown')))
        info_layout.addRow("To Device:", QtWidgets.QLabel(getattr(to_device, 'name', 'Unknown')))
        layout.addWidget(info_group)
        
        # Address assignment
        address_group = QtWidgets.QGroupBox("Address Assignment")
        address_layout = QtWidgets.QFormLayout(address_group)
        
        circuit_spin = QtWidgets.QSpinBox()
        circuit_spin.setRange(1, 99)
        circuit_spin.setValue(1)
        address_layout.addRow("Circuit ID:", circuit_spin)
        
        address_spin = QtWidgets.QSpinBox()
        address_spin.setRange(1, 159)
        address_spin.setValue(1)
        address_layout.addRow("Device Address:", address_spin)
        
        layout.addWidget(address_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("Assign")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            circuit_id = circuit_spin.value()
            address = address_spin.value()
            
            self.main_window.statusBar().showMessage(f"Assigned address {address} on circuit {circuit_id}")
            
            # Find the connection in the wire tool
            if self.wire_tool:
                connection = self.wire_tool.get_connection_by_devices(from_device, to_device)
                if connection:
                    # Update the connection with addressing info
                    self.wire_tool.update_slc_addressing(connection, circuit_id, address)
                    
                    # Update devices with addressing information
                    if hasattr(to_device, 'set_slc_address'):
                        to_device.set_slc_address(address)
                    if hasattr(to_device, 'set_circuit_id'):
                        to_device.set_circuit_id(circuit_id)
                        
                    # Update the device's label to show the address
                    if hasattr(to_device, 'set_label_text'):
                        to_device.set_label_text(f"{to_device.name} (Addr: {address})")

    def on_device_placed(self, device_item):
        """Handle device placement event."""
        # Update device count in toolbar
        if self.toolbar:
            # Get current device count
            device_count = len(self.main_window.layer_devices.childItems())
            self.toolbar.update_device_count(device_count)
            
        # Emit signal
        self.device_placed.emit(device_item)
        
        # If we have a fire alarm manager, register the device
        if self.fire_alarm_manager and self.current_project_id:
            try:
                # This would register the device with the fire alarm system
                pass
            except Exception as e:
                print(f"Failed to register device with fire alarm system: {e}")
                
    def on_wire_created(self, wire_item):
        """Handle wire creation event."""
        # Emit signal
        self.wire_created.emit(wire_item)
        
        # Update system status
        self.update_system_status()
        
    def create_new_project(self, project_id: str, project_name: str, client: str, location: str):
        """Create a new fire alarm project."""
        self.current_project_id = project_id
        
        if self.fire_alarm_manager:
            try:
                project = self.fire_alarm_manager.create_new_project(
                    project_id, project_name, client, location
                )
                
                # Update status widget
                if self.status_widget:
                    self.status_widget.set_project_info(
                        project_id, project_name, client, location
                    )
                    
                # Update system status
                if self.status_widget:
                    self.status_widget.set_system_status("fire_alarm", panels=0, circuits=0, devices=0, connections=0)
                    
                self.main_window.statusBar().showMessage(f"Created fire alarm project: {project_name}")
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self.main_window,
                    "Project Creation Error",
                    f"Failed to create fire alarm project: {str(e)}"
                )
                
    def load_project(self, project_id: str):
        """Load an existing fire alarm project."""
        self.current_project_id = project_id
        
        if self.fire_alarm_manager:
            try:
                project = self.fire_alarm_manager.load_project(project_id)
                
                if project:
                    # Update status widget
                    if self.status_widget:
                        self.status_widget.set_project_info(
                            project.project_id,
                            project.project_name,
                            project.client,
                            project.location
                        )
                        
                        # Update system status
                        panels = len(project.panels)
                        circuits = len(project.circuits)
                        devices = len(project.devices)
                        connections = 0  # Would need to calculate actual connections
                        self.status_widget.set_system_status("fire_alarm", panels=panels, circuits=circuits, devices=devices, connections=connections)
                        
                    self.main_window.statusBar().showMessage(f"Loaded fire alarm project: {project.project_name}")
                else:
                    QtWidgets.QMessageBox.warning(
                        self.main_window,
                        "Project Load",
                        f"Project {project_id} not found"
                    )
                    
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self.main_window,
                    "Project Load Error",
                    f"Failed to load fire alarm project: {str(e)}"
                )
                
    def update_system_status(self):
        """Update the system status display."""
        if not self.status_widget or not self.fire_alarm_manager or not self.current_project_id:
            return
            
        try:
            # Get project summary
            summary = self.fire_alarm_manager.get_project_summary()
            
            # Update status widget
            self.status_widget.set_system_status(
                "fire_alarm",
                panels=summary.get('total_panels', 0),
                circuits=summary.get('total_circuits', 0),
                devices=summary.get('total_devices', 0),
                connections=0  # Connections would need to be calculated
            )
            
        except Exception as e:
            print(f"Failed to update system status: {e}")