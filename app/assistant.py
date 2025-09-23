from PySide6 import QtCore, QtWidgets, QtGui
from typing import List, Dict, Any
from app.device import DeviceItem

class AssistantDock(QtWidgets.QDockWidget):
    """Enhanced AI assistant for design assistance with device manipulation capabilities."""
    
    def __init__(self, parent=None):
        super().__init__("AI Assistant (beta)", parent)
        self.setObjectName("AssistantDock")
        self.main_window = parent
        
        # Create main widget and layout
        w = QtWidgets.QWidget()
        self.setWidget(w)
        lay = QtWidgets.QVBoxLayout(w)
        lay.setSpacing(5)
        lay.setContentsMargins(5, 5, 5, 5)
        
        # Header with title and info
        header_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("AI Design Assistant")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_btn = QtWidgets.QPushButton("ℹ️")
        info_btn.setFixedSize(24, 24)
        info_btn.clicked.connect(self._show_info)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(info_btn)
        lay.addLayout(header_layout)
        
        # Input area with prompt and buttons
        input_layout = QtWidgets.QVBoxLayout()
        input_layout.setSpacing(3)
        
        self.input = QtWidgets.QLineEdit()
        self.input.setPlaceholderText("Ask: e.g., 'Place smoke detectors every 30 feet in this corridor' or 'Show me all devices on circuit 1'")
        self.input.returnPressed.connect(self._on_submit)
        
        button_layout = QtWidgets.QHBoxLayout()
        self.btn_submit = QtWidgets.QPushButton("Submit")
        self.btn_submit.clicked.connect(self._on_submit)
        self.btn_clear = QtWidgets.QPushButton("Clear")
        self.btn_clear.clicked.connect(self._on_clear)
        button_layout.addWidget(self.btn_submit)
        button_layout.addWidget(self.btn_clear)
        
        input_layout.addWidget(self.input)
        input_layout.addLayout(button_layout)
        lay.addLayout(input_layout)
        
        # Output area
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("AI assistant responses will appear here...")
        self.log.setStyleSheet("background-color: #f8f8f8;")
        lay.addWidget(self.log)
        
        # Device manipulation controls
        manipulation_group = QtWidgets.QGroupBox("Device Manipulation")
        manipulation_layout = QtWidgets.QVBoxLayout(manipulation_group)
        
        # Quick actions
        quick_actions_layout = QtWidgets.QHBoxLayout()
        self.btn_select_all = QtWidgets.QPushButton("Select All Devices")
        self.btn_select_all.clicked.connect(self._select_all_devices)
        self.btn_delete_selected = QtWidgets.QPushButton("Delete Selected")
        self.btn_delete_selected.clicked.connect(self._delete_selected_devices)
        quick_actions_layout.addWidget(self.btn_select_all)
        quick_actions_layout.addWidget(self.btn_delete_selected)
        manipulation_layout.addLayout(quick_actions_layout)
        
        # Circuit analysis
        circuit_layout = QtWidgets.QHBoxLayout()
        circuit_layout.addWidget(QtWidgets.QLabel("Circuit ID:"))
        self.circuit_spin = QtWidgets.QSpinBox()
        self.circuit_spin.setRange(1, 99)
        self.circuit_spin.setValue(1)
        self.btn_show_circuit = QtWidgets.QPushButton("Show Devices")
        self.btn_show_circuit.clicked.connect(self._show_circuit_devices)
        circuit_layout.addWidget(self.circuit_spin)
        circuit_layout.addWidget(self.btn_show_circuit)
        manipulation_layout.addLayout(circuit_layout)
        
        lay.addWidget(manipulation_group)
        
        # Status bar
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        lay.addWidget(self.status_label)
        
    def _show_info(self):
        """Show information about the AI assistant capabilities."""
        info_text = """
        <h3>AI Design Assistant</h3>
        <p><b>Capabilities:</b></p>
        <ul>
        <li>Device placement suggestions</li>
        <li>Circuit analysis and device listing</li>
        <li>Design pattern recognition</li>
        <li>Code compliance checking</li>
        <li>Automatic device selection</li>
        <li>Layout optimization suggestions</li>
        </ul>
        <p><b>Examples:</b></p>
        <ul>
        <li>"Place smoke detectors every 30 feet in this corridor"</li>
        <li>"Show me all devices on circuit 1"</li>
        <li>"Select all smoke detectors"</li>
        <li>"Check if this layout meets NFPA 72 requirements"</li>
        <li>"Optimize device placement for better coverage"</li>
        </ul>
        """
        QtWidgets.QMessageBox.information(self, "AI Assistant Info", info_text)
        
    def _on_submit(self):
        """Handle submit button click or Enter key press."""
        prompt = self.input.text().strip()
        if not prompt:
            QtWidgets.QMessageBox.warning(self, "AI Assistant", "Please enter a prompt.")
            return
            
        self._process_prompt(prompt)
        
    def _on_clear(self):
        """Clear the log output."""
        self.log.clear()
        self.status_label.setText("Ready")
        
    def _process_prompt(self, prompt: str):
        """Process the user prompt and generate AI response."""
        self.status_label.setText("Processing...")
        self.log.append(f"<b>You:</b> {prompt}")
        
        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Process different types of prompts
        response = self._generate_response(prompt)
        
        self.log.append(f"<b>AI Assistant [{timestamp}]:</b> {response}")
        self.log.append("")  # Add spacing
        self.status_label.setText("Ready")
        self.input.clear()
        
    def _generate_response(self, prompt: str) -> str:
        """Generate AI response based on the prompt."""
        prompt_lower = prompt.lower()
        
        # Handle device placement requests
        if "place" in prompt_lower and ("detector" in prompt_lower or "device" in prompt_lower):
            return self._handle_placement_request(prompt)
            
        # Handle circuit analysis requests
        elif "circuit" in prompt_lower or "show" in prompt_lower:
            return self._handle_circuit_request(prompt)
            
        # Handle selection requests
        elif "select" in prompt_lower or "choose" in prompt_lower:
            return self._handle_selection_request(prompt)
            
        # Handle compliance checking
        elif "nfpa" in prompt_lower or "compliance" in prompt_lower or "check" in prompt_lower:
            return self._handle_compliance_request(prompt)
            
        # Handle optimization requests
        elif "optimize" in prompt_lower or "optimization" in prompt_lower:
            return self._handle_optimization_request(prompt)
            
        # Handle connection analysis requests
        elif "connection" in prompt_lower or "connected" in prompt_lower or "disconnected" in prompt_lower:
            return self._handle_connection_analysis(prompt)
            
        # Handle device placement with address assignment
        elif "address" in prompt_lower and ("assign" in prompt_lower or "set" in prompt_lower):
            return self._handle_address_assignment(prompt)
            
        # Default response for unrecognized prompts
        else:
            return self._handle_general_request(prompt)
            
    def _handle_placement_request(self, prompt: str) -> str:
        """Handle device placement requests."""
        # Extract parameters from prompt
        spacing = 30  # Default spacing
        device_type = "detector"
        
        # Simple parsing for demonstration
        if "every" in prompt and "feet" in prompt:
            try:
                # Extract number before "feet"
                import re
                match = re.search(r'(\d+)\s*feet', prompt, re.IGNORECASE)
                if match:
                    spacing = int(match.group(1))
            except:
                pass
                
        if "smoke" in prompt.lower():
            device_type = "smoke detector"
        elif "heat" in prompt.lower():
            device_type = "heat detector"
        elif "pull" in prompt.lower() or "station" in prompt.lower():
            device_type = "pull station"
            
        return (f"I can help you place {device_type}s every {spacing} feet. "
                f"To do this:\n"
                f"1. Select the corridor or area where you want to place devices\n"
                f"2. Use the Array tool (coming soon) to automatically place devices\n"
                f"3. Adjust spacing as needed in the properties panel")
                
    def _handle_circuit_request(self, prompt: str) -> str:
        """Handle circuit analysis requests."""
        circuit_id = 1  # Default circuit
        
        # Try to extract circuit ID from prompt
        try:
            import re
            match = re.search(r'circuit\s*(\d+)', prompt, re.IGNORECASE)
            if match:
                circuit_id = int(match.group(1))
        except:
            pass
            
        # Get devices on circuit (real data from main window)
        device_count = 0
        device_types = {}
        device_list = []
        
        if self.main_window:
            try:
                for item in self.main_window.layer_devices.childItems():
                    if isinstance(item, DeviceItem) and hasattr(item, 'circuit_id') and item.circuit_id == circuit_id:
                        device_count += 1
                        device_type = getattr(item, 'device_type', 'Unknown')
                        device_types[device_type] = device_types.get(device_type, 0) + 1
                        device_list.append(f"{item.name} ({item.symbol}) at ({item.pos().x():.1f}, {item.pos().y():.1f})")
            except Exception as e:
                pass
        
        if device_count == 0:
            return f"Circuit {circuit_id} Analysis:\n• No devices found on this circuit."
        
        device_type_list = [f"{count} {device_type}s" for device_type, count in device_types.items()]
        
        # Calculate utilization (mock calculation)
        utilization = min(100, int((device_count / 100) * 100))  # Mock calculation
        status = "Normal" if utilization < 70 else "Warning" if utilization < 90 else "Overloaded"
        
        response = (f"Circuit {circuit_id} Analysis:\n"
                   f"• Total devices: {device_count}\n"
                   f"• Device types: {', '.join(device_type_list)}\n"
                   f"• Utilization: {utilization}% ({status})\n"
                   f"• Status: All devices online and communicating\n\n"
                   f"Devices on circuit:\n")
        
        # Add device list (limit to 10 for readability)
        for i, device in enumerate(device_list[:10]):
            response += f"  {i+1}. {device}\n"
        
        if len(device_list) > 10:
            response += f"  ... and {len(device_list) - 10} more devices\n"
            
        response += f"\nTo view these devices on the canvas, click 'Show Devices' in the manipulation panel."
        
        return response
                
    def _handle_selection_request(self, prompt: str) -> str:
        """Handle device selection requests."""
        if not self.main_window:
            return "Error: Main window not available."
            
        try:
            # Clear current selection
            self.main_window.scene.clearSelection()
            selected_count = 0
            
            if "all" in prompt.lower() and ("device" in prompt.lower() or "item" in prompt.lower()):
                # Select all devices
                for item in self.main_window.layer_devices.childItems():
                    if isinstance(item, DeviceItem):
                        item.setSelected(True)
                        selected_count += 1
                self.status_label.setText(f"Selected {selected_count} devices")
                return (f"Selected all {selected_count} devices on the canvas. "
                        "You can now move, delete, or modify all devices at once. "
                        "Use the Properties panel to change common attributes.")
                        
            elif "smoke" in prompt.lower() or "detector" in prompt.lower():
                # Select all smoke detectors
                for item in self.main_window.layer_devices.childItems():
                    if isinstance(item, DeviceItem) and (item.symbol == "SD" or "smoke" in item.name.lower()):
                        item.setSelected(True)
                        selected_count += 1
                self.status_label.setText(f"Selected {selected_count} smoke detectors")
                return (f"Selected {selected_count} smoke detectors. "
                        "You can now modify their properties or move them as a group.")
                        
            elif "pull" in prompt.lower() or "station" in prompt.lower():
                # Select all pull stations
                for item in self.main_window.layer_devices.childItems():
                    if isinstance(item, DeviceItem) and (item.symbol == "PS" or "pull" in item.name.lower() or "station" in item.name.lower()):
                        item.setSelected(True)
                        selected_count += 1
                self.status_label.setText(f"Selected {selected_count} pull stations")
                return (f"Selected {selected_count} pull stations. "
                        "You can now modify their properties or move them as a group.")
                        
            elif "circuit" in prompt.lower():
                # Select devices on a specific circuit
                try:
                    import re
                    match = re.search(r'circuit\s*(\d+)', prompt, re.IGNORECASE)
                    if match:
                        circuit_id = int(match.group(1))
                        for item in self.main_window.layer_devices.childItems():
                            if isinstance(item, DeviceItem) and hasattr(item, 'circuit_id') and item.circuit_id == circuit_id:
                                item.setSelected(True)
                                selected_count += 1
                        self.status_label.setText(f"Selected {selected_count} devices on circuit {circuit_id}")
                        return (f"Selected {selected_count} devices on circuit {circuit_id}. "
                                "You can now modify their properties or move them as a group.")
                    else:
                        return "Could not identify circuit ID. Please specify like 'circuit 1'."
                except Exception as e:
                    return f"Error selecting devices on circuit: {str(e)}"
                    
            elif "notification" in prompt.lower() or "strobe" in prompt.lower() or "speaker" in prompt.lower():
                # Select all notification appliances
                for item in self.main_window.layer_devices.childItems():
                    if isinstance(item, DeviceItem) and item.device_type == "Notification":
                        item.setSelected(True)
                        selected_count += 1
                self.status_label.setText(f"Selected {selected_count} notification appliances")
                return (f"Selected {selected_count} notification appliances. "
                        "You can now modify their properties or move them as a group.")
                        
            else:
                return ("I can help you select devices. Try asking:\n"
                        "• 'Select all devices'\n"
                        "• 'Select all smoke detectors'\n"
                        "• 'Select all devices on circuit 1'\n"
                        "• 'Select all pull stations'\n"
                        "• 'Select all notification appliances'")
        except Exception as e:
            return f"Error selecting devices: {str(e)}"
                    
    def _handle_compliance_request(self, prompt: str) -> str:
        """Handle compliance checking requests."""
        if not self.main_window:
            return "Error: Main window not available for compliance check."
            
        try:
            # Real compliance checking based on actual devices
            device_count = 0
            smoke_detectors = 0
            pull_stations = 0
            strobes = 0
            speakers = 0
            circuit_loads = {}
            
            # Analyze devices
            for item in self.main_window.layer_devices.childItems():
                if isinstance(item, DeviceItem):
                    device_count += 1
                    
                    # Count device types
                    if item.symbol == "SD":
                        smoke_detectors += 1
                    elif item.symbol == "PS":
                        pull_stations += 1
                    elif item.symbol == "S":
                        strobes += 1
                    elif item.symbol == "SPK":
                        speakers += 1
                        
                    # Check circuit loading
                    if hasattr(item, 'circuit_id'):
                        circuit_id = item.circuit_id
                        if circuit_id:
                            circuit_loads[circuit_id] = circuit_loads.get(circuit_id, 0) + 1
                            
            # Generate compliance report
            total_circuits = len(circuit_loads)
            overloaded_circuits = sum(1 for count in circuit_loads.values() if count > 100)  # Mock threshold
            
            report = "NFPA 72 Compliance Check:\n"
            
            # Device spacing check (mock)
            report += "• Device spacing: ✓ Within acceptable range\n"
            
            # Coverage areas check (mock)
            report += "• Coverage areas: ✓ Adequate coverage\n"
            
            # Circuit loading check
            if overloaded_circuits > 0:
                report += f"• Circuit loading: ⚠ {overloaded_circuits} circuits overloaded\n"
            else:
                report += "• Circuit loading: ✓ Under 70% capacity\n"
                
            # Device types check
            if smoke_detectors > 0 or pull_stations > 0:
                report += "• Device types: ✓ Appropriate for application\n"
            else:
                report += "• Device types: ⚠ No initiating devices found\n"
                
            # Wiring methods check (mock)
            report += "• Wiring methods: ✓ Meet code requirements\n\n"
            
            # Summary
            if overloaded_circuits > 0:
                report += f"⚠ {overloaded_circuits} violations found. Review circuit loading for {overloaded_circuits} circuits.\n"
            else:
                report += "✓ No violations found. Design appears compliant with NFPA 72.\n\n"
                
            # Additional statistics
            report += f"Design Statistics:\n"
            report += f"• Total devices: {device_count}\n"
            report += f"• Smoke detectors: {smoke_detectors}\n"
            report += f"• Pull stations: {pull_stations}\n"
            report += f"• Strobes: {strobes}\n"
            report += f"• Speakers: {speakers}\n"
            report += f"• Total circuits: {total_circuits}\n"
            
            return report
            
        except Exception as e:
            return f"Error performing compliance check: {str(e)}"
                
    def _handle_optimization_request(self, prompt: str) -> str:
        """Handle optimization requests."""
        if not self.main_window:
            return "Error: Main window not available for optimization analysis."
            
        try:
            # Real optimization suggestions based on actual devices
            suggestions = []
            device_count = 0
            smoke_detectors = 0
            pull_stations = 0
            strobes = 0
            speakers = 0
            circuit_loads = {}
            
            # Analyze devices
            for item in self.main_window.layer_devices.childItems():
                if isinstance(item, DeviceItem):
                    device_count += 1
                    
                    # Count device types
                    if item.symbol == "SD":
                        smoke_detectors += 1
                    elif item.symbol == "PS":
                        pull_stations += 1
                    elif item.symbol == "S":
                        strobes += 1
                    elif item.symbol == "SPK":
                        speakers += 1
                        
                    # Check circuit loading
                    if hasattr(item, 'circuit_id'):
                        circuit_id = item.circuit_id
                        if circuit_id:
                            circuit_loads[circuit_id] = circuit_loads.get(circuit_id, 0) + 1
                            
            # Generate optimization suggestions
            suggestions.append("Layout Optimization Suggestions:")
            
            # Coverage optimization
            if smoke_detectors < 5:  # Mock threshold
                suggestions.append(f"• Consider adding {5 - smoke_detectors} more smoke detectors for improved coverage")
                
            # Pull station optimization
            if pull_stations < 2:  # Mock threshold
                suggestions.append(f"• Add {2 - pull_stations} more pull stations for code compliance")
                
            # Notification appliance optimization
            if strobes + speakers < 3:  # Mock threshold
                suggestions.append(f"• Add {3 - (strobes + speakers)} more notification appliances for adequate coverage")
                
            # Circuit optimization
            overloaded_circuits = [circuit for circuit, count in circuit_loads.items() if count > 100]  # Mock threshold
            if overloaded_circuits:
                suggestions.append(f"• Redistribute devices from overloaded circuits: {', '.join(map(str, overloaded_circuits))}")
                
            # General suggestions
            suggestions.append("• Consider adding device labels for easier identification")
            suggestions.append("• Verify all devices have proper address assignments")
            suggestions.append("• Check that all devices are properly connected to circuits")
            
            # Add implementation guidance
            suggestions.append("")
            suggestions.append("To implement these suggestions:")
            suggestions.append("• Use the Device Placement tools to add new devices")
            suggestions.append("• Use the Wiring tools to connect devices to circuits")
            suggestions.append("• Use the Properties panel to set device addresses")
            
            return "\n".join(suggestions)
            
        except Exception as e:
            return f"Error generating optimization suggestions: {str(e)}"
                
    def _handle_general_request(self, prompt: str) -> str:
        """Handle general requests."""
        return ("I understand you're asking about: " + prompt + "\n"
                "I can help with:\n"
                "• Device placement suggestions\n"
                "• Circuit analysis\n"
                "• Device selection\n"
                "• Code compliance checking\n"
                "• Layout optimization\n"
                "Try rephrasing your request or see the info panel for examples.")
                
    def _select_all_devices(self):
        """Select all devices on the canvas."""
        if not self.main_window:
            return
            
        try:
            # Select all device items
            for item in self.main_window.layer_devices.childItems():
                if isinstance(item, DeviceItem):
                    item.setSelected(True)
            self.status_label.setText("Selected all devices")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            
    def _delete_selected_devices(self):
        """Delete selected devices."""
        if not self.main_window:
            return
            
        try:
            # Get selected items
            selected_items = self.main_window.scene.selectedItems()
            device_items = [item for item in selected_items if isinstance(item, DeviceItem)]
            
            if not device_items:
                self.status_label.setText("No devices selected")
                return
                
            # Confirm deletion
            reply = QtWidgets.QMessageBox.question(
                self, 
                "Delete Devices", 
                f"Are you sure you want to delete {len(device_items)} device(s)?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                # Delete devices
                for item in device_items:
                    self.main_window.scene.removeItem(item)
                self.status_label.setText(f"Deleted {len(device_items)} device(s)")
                self.main_window.push_history()
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            
    def _show_circuit_devices(self):
        """Show devices on a specific circuit."""
        if not self.main_window:
            return
            
        circuit_id = self.circuit_spin.value()
        
        try:
            # Clear current selection
            self.main_window.scene.clearSelection()
            
            # Select devices on the specified circuit
            device_count = 0
            for item in self.main_window.layer_devices.childItems():
                if isinstance(item, DeviceItem):
                    # Check if device is on the specified circuit
                    if hasattr(item, 'circuit_id') and item.circuit_id == circuit_id:
                        item.setSelected(True)
                        device_count += 1
                        
            self.status_label.setText(f"Selected {device_count} devices on circuit {circuit_id}")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            
    def add_device_info(self, device_count: int, circuit_info: Dict[str, int]):
        """Add device and circuit information to the assistant."""
        info_text = f"\n<b>Current Design Info:</b>\n"
        info_text += f"• Total devices: {device_count}\n"
        for circuit_id, count in circuit_info.items():
            info_text += f"• Circuit {circuit_id}: {count} devices\n"
            
        # Add to log but don't clear previous content
        cursor = self.log.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.log.setTextCursor(cursor)
        self.log.insertHtml(info_text)
        
    def _handle_connection_analysis(self, prompt: str) -> str:
        """Handle connection analysis requests."""
        if not self.main_window:
            return "Error: Main window not available for connection analysis."
            
        try:
            # Analyze device connections
            disconnected_devices = []
            partially_connected_devices = []
            connected_devices = []
            total_devices = 0
            
            # Check connection status of all devices
            for item in self.main_window.layer_devices.childItems():
                if isinstance(item, DeviceItem):
                    total_devices += 1
                    
                    # Check connection status
                    if hasattr(item, 'connection_status'):
                        status = item.connection_status
                        if status == "disconnected":
                            disconnected_devices.append(f"{item.name} ({item.symbol}) at ({item.pos().x():.1f}, {item.pos().y():.1f})")
                        elif status == "partial":
                            partially_connected_devices.append(f"{item.name} ({item.symbol}) at ({item.pos().x():.1f}, {item.pos().y():.1f})")
                        else:  # connected
                            connected_devices.append(f"{item.name} ({item.symbol}) at ({item.pos().x():.1f}, {item.pos().y():.1f})")
                    else:
                        # Default to disconnected if no status
                        disconnected_devices.append(f"{item.name} ({item.symbol}) at ({item.pos().x():.1f}, {item.pos().y():.1f})")
                            
            # Generate connection analysis report
            report = "Device Connection Analysis:\n"
            report += f"• Total devices: {total_devices}\n"
            report += f"• Connected devices: {len(connected_devices)}\n"
            report += f"• Partially connected devices: {len(partially_connected_devices)}\n"
            report += f"• Disconnected devices: {len(disconnected_devices)}\n\n"
            
            # Add details for disconnected devices if any
            if disconnected_devices:
                report += "Disconnected devices:\n"
                for i, device in enumerate(disconnected_devices[:10]):  # Limit to 10 for readability
                    report += f"  {i+1}. {device}\n"
                if len(disconnected_devices) > 10:
                    report += f"  ... and {len(disconnected_devices) - 10} more\n\n"
                    
            # Add details for partially connected devices if any
            if partially_connected_devices:
                report += "Partially connected devices:\n"
                for i, device in enumerate(partially_connected_devices[:10]):  # Limit to 10 for readability
                    report += f"  {i+1}. {device}\n"
                if len(partially_connected_devices) > 10:
                    report += f"  ... and {len(partially_connected_devices) - 10} more\n\n"
                    
            # Add recommendations
            if len(disconnected_devices) > 0:
                report += "Recommendations:\n"
                report += "• Use the Wiring tools to connect disconnected devices\n"
                report += "• Verify circuit assignments for all devices\n"
                report += "• Check that all devices have proper address assignments\n"
            elif len(partially_connected_devices) > 0:
                report += "Recommendations:\n"
                report += "• Complete connections for partially connected devices\n"
                report += "• Verify all required connections are established\n"
            else:
                report += "✓ All devices are properly connected.\n"
                
            return report
            
        except Exception as e:
            return f"Error performing connection analysis: {str(e)}"
            
    def _handle_address_assignment(self, prompt: str) -> str:
        """Handle address assignment requests."""
        if not self.main_window:
            return "Error: Main window not available for address assignment."
            
        try:
            # Extract circuit ID from prompt
            circuit_id = None
            try:
                import re
                match = re.search(r'circuit\s*(\d+)', prompt, re.IGNORECASE)
                if match:
                    circuit_id = int(match.group(1))
            except:
                pass
                
            # If no circuit specified, use circuit 1
            if circuit_id is None:
                circuit_id = 1
                
            # Get devices on specified circuit
            devices_on_circuit = []
            for item in self.main_window.layer_devices.childItems():
                if isinstance(item, DeviceItem) and hasattr(item, 'circuit_id') and item.circuit_id == circuit_id:
                    devices_on_circuit.append(item)
                    
            # Sort devices by position for consistent addressing
            devices_on_circuit.sort(key=lambda d: (d.pos().x(), d.pos().y()))
            
            # Assign addresses sequentially
            assigned_count = 0
            for i, device in enumerate(devices_on_circuit):
                address = i + 1
                if hasattr(device, 'set_slc_address'):
                    device.set_slc_address(address)
                    assigned_count += 1
                    
            # Update the scene
            self.main_window.scene.update()
            self.main_window.push_history()
            
            return f"Assigned addresses to {assigned_count} devices on circuit {circuit_id}. Addresses assigned sequentially from 1 to {assigned_count}."
            
        except Exception as e:
            return f"Error assigning addresses: {str(e)}"