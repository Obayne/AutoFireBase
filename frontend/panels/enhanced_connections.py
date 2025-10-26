"""
Enhanced Connections Panel with Live Calculations - Professional Edition
 
Provides a hierarchical tree/riser view of all circuits with integrated
live voltage drop calculations, battery sizing, and compliance checking.
Enhanced with AutoFire professional design system.
"""

import logging
from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QGroupBox, QLabel, QSplitter, QPushButton, QFrame, QTextEdit,
    QCheckBox
)
from PySide6.QtGui import QFont, QColor

from cad_core.calculations.live_engine import LiveCalculationsEngine, WireSegment

# Design system imports
try:
    from frontend.design_system import (
        AutoFireColor, AutoFireIconTheme, AutoFireSpacing, AutoFireStyleSheet,
        create_title_font, create_professional_font, get_circuit_color,
        get_compliance_color
    )
    DESIGN_SYSTEM_AVAILABLE = True
except ImportError:
    DESIGN_SYSTEM_AVAILABLE = False
    logging.warning("Design system not available - using fallback styling")

logger = logging.getLogger(__name__)


class CircuitTreeItem(QTreeWidgetItem):
    """Custom tree item for circuit display with live calculation data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.circuit_id = None
        self.analysis = None
        self.battery_calc = None
        self.item_type = "unknown"  # panel, circuit, device, segment
        
    def update_from_analysis(self, analysis):
        """Update display from circuit analysis."""
        self.analysis = analysis
        self._update_display()
    
    def update_from_battery_calc(self, battery_calc):
        """Update display from battery calculation."""
        self.battery_calc = battery_calc
        self._update_display()
    
    def _update_display(self):
        """Update the visual display based on current data."""
        if self.item_type == "circuit" and self.analysis:
            # Update circuit display with live calculations
            vd_text = f"{self.analysis.voltage_drop_percent:.1f}%"
            compliance_icon = "✅" if self.analysis.compliance_status == "PASS" else "⚠️"
            
            self.setText(1, f"{self.analysis.device_count} devices")
            self.setText(2, f"{self.analysis.total_length_ft:.0f} ft")
            self.setText(3, f"{self.analysis.current_draw_a:.3f} A")
            self.setText(4, vd_text)
            self.setText(5, compliance_icon)
            
            # Set colors based on compliance
            if self.analysis.compliance_status == "FAIL":
                self.setBackground(4, QColor(255, 200, 200))  # Light red
            elif self.analysis.compliance_status == "WARN":
                self.setBackground(4, QColor(255, 255, 200))  # Light yellow
            else:
                self.setBackground(4, QColor(200, 255, 200))  # Light green
                
        elif self.item_type == "panel" and self.battery_calc:
            # Update panel display with battery information
            self.setText(1, f"{self.battery_calc.recommended_ah} AH")
            self.setText(2, f"{self.battery_calc.standby_current_a:.3f} A")
            self.setText(3, f"{self.battery_calc.alarm_current_a:.3f} A")
            self.setText(4, self.battery_calc.battery_sku or "N/A")


class EnhancedConnectionsPanel(QWidget):
    """
    Enhanced connections panel with hierarchical circuit display and live calculations.
    
    Features:
    - Tree/riser view of panels, circuits, and devices
    - Live voltage drop calculations per circuit
    - Battery sizing display per panel
    - NFPA 72 compliance indicators
    - Real-time updates as design changes
    """
    
    # Signals for integration with main UI
    circuit_selected = Signal(str)
    device_selected = Signal(str)
    calculations_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.calc_engine = LiveCalculationsEngine()
        self.setup_ui()
        self.setup_connections()
        self.apply_professional_styling()
        
        # Update timer for live calculations
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._perform_calculations_update)
        
        logger.info("Enhanced Connections Panel initialized with professional styling")
    
    def setup_ui(self):
        """Setup the professional user interface."""
        layout = QVBoxLayout(self)
        spacing = AutoFireSpacing.MD if DESIGN_SYSTEM_AVAILABLE else 8
        layout.setContentsMargins(spacing, spacing, spacing, spacing)
        layout.setSpacing(spacing)
        
        # Professional header
        self.setup_professional_header(layout)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Top section: Circuit tree view
        self.setup_circuit_tree(splitter)
        
        # Bottom section: Calculation details
        self.setup_calculation_details(splitter)
        
        # Control buttons
        self.setup_control_buttons(layout)
        
        # Set splitter proportions
        splitter.setSizes([400, 200])
    
    def setup_professional_header(self, parent_layout):
        """Setup professional header with AutoFire styling."""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title with professional icon
        title_icon = (AutoFireIconTheme.get_icon('circuit_slc') 
                     if DESIGN_SYSTEM_AVAILABLE else "🔗")
        title_label = QLabel(f"{title_icon} Enhanced Connections")
        if DESIGN_SYSTEM_AVAILABLE:
            title_label.setFont(create_title_font())
            title_label.setStyleSheet(f"color: {AutoFireColor.TEXT_PRIMARY.value};")
        else:
            title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Professional status indicator
        self.header_status = QLabel("⏳ Calculating...")
        if DESIGN_SYSTEM_AVAILABLE:
            self.header_status.setStyleSheet(f"color: {AutoFireColor.TEXT_SECONDARY.value};")
        header_layout.addWidget(self.header_status)
        
        parent_layout.addWidget(header_frame)
    
    def apply_professional_styling(self):
        """Apply professional AutoFire styling to the panel."""
        if not DESIGN_SYSTEM_AVAILABLE:
            return
        
        # Main panel styling
        self.setStyleSheet(AutoFireStyleSheet.get_panel_style())
        
        logger.info("Professional styling applied to Enhanced Connections Panel")
    
    def setup_circuit_tree(self, parent):
        """Setup the hierarchical circuit tree view with professional styling."""
        # Professional group box
        tree_icon = (AutoFireIconTheme.get_icon('circuit_slc') 
                    if DESIGN_SYSTEM_AVAILABLE else "🌳")
        tree_group = QGroupBox(f"{tree_icon} Circuit Hierarchy & Live Calculations")
        if DESIGN_SYSTEM_AVAILABLE:
            tree_group.setStyleSheet(AutoFireStyleSheet.get_panel_style())
        tree_layout = QVBoxLayout(tree_group)
        
        # Create professional tree widget
        self.circuit_tree = QTreeWidget()
        
        # Professional headers with icons
        if DESIGN_SYSTEM_AVAILABLE:
            headers = [
                f"{AutoFireIconTheme.get_icon('circuit_slc')} Circuit/Device",
                f"{AutoFireIconTheme.get_icon('detector')} Count/Capacity", 
                f"{AutoFireIconTheme.get_icon('measure')} Length/Standby",
                f"{AutoFireIconTheme.get_icon('calculate')} Current/Alarm", 
                "Voltage Drop/SKU",
                f"{AutoFireIconTheme.get_icon('status_pass')} Status"
            ]
        else:
            headers = [
                "Circuit/Device", "Count/Capacity", "Length/Standby", 
                "Current/Alarm", "Voltage Drop/SKU", "Status"
            ]
        
        self.circuit_tree.setHeaderLabels(headers)
        
        # Professional column widths and styling
        self.circuit_tree.setColumnWidth(0, 250)  # Wider for icons
        self.circuit_tree.setColumnWidth(1, 120)
        self.circuit_tree.setColumnWidth(2, 120)
        self.circuit_tree.setColumnWidth(3, 120)
        self.circuit_tree.setColumnWidth(4, 140)
        self.circuit_tree.setColumnWidth(5, 100)
        
        # Professional tree styling
        self.circuit_tree.setSelectionMode(self.circuit_tree.SelectionMode.SingleSelection)
        self.circuit_tree.setAlternatingRowColors(True)
        self.circuit_tree.setRootIsDecorated(True)
        self.circuit_tree.setUniformRowHeights(True)
        
        # Apply professional table styling
        if DESIGN_SYSTEM_AVAILABLE:
            self.circuit_tree.setStyleSheet(AutoFireStyleSheet.get_table_style())
        
        # Connect signals
        self.circuit_tree.itemClicked.connect(self._on_tree_item_clicked)
        self.circuit_tree.itemExpanded.connect(self._on_tree_expanded)
        
        tree_layout.addWidget(self.circuit_tree)
        parent.addWidget(tree_group)
    
    def setup_calculation_details(self, parent):
        """Setup the calculation details panel."""
        details_group = QGroupBox("Calculation Details")
        details_layout = QVBoxLayout(details_group)
        
        # Compliance summary
        compliance_frame = QFrame()
        compliance_layout = QHBoxLayout(compliance_frame)
        compliance_layout.setContentsMargins(0, 0, 0, 0)
        
        self.compliance_status = QLabel("System Status: Calculating...")
        self.compliance_status.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        compliance_layout.addWidget(self.compliance_status)
        
        compliance_layout.addStretch()
        
        self.nfpa_indicator = QLabel("NFPA 72: ⏳")
        compliance_layout.addWidget(self.nfpa_indicator)
        
        details_layout.addWidget(compliance_frame)
        
        # Detailed calculation display
        self.calc_details = QTextEdit()
        self.calc_details.setMaximumHeight(120)
        self.calc_details.setReadOnly(True)
        self.calc_details.setFont(QFont("Consolas", 9))
        details_layout.addWidget(self.calc_details)
        
        parent.addWidget(details_group)
    
    def setup_control_buttons(self, parent_layout):
        """Setup professional control buttons for the panel."""
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # Professional refresh button
        refresh_icon = (AutoFireIconTheme.get_icon('refresh') 
                       if DESIGN_SYSTEM_AVAILABLE else "🔄")
        self.refresh_button = QPushButton(f"{refresh_icon} Refresh Calculations")
        self.refresh_button.clicked.connect(self.refresh_all_calculations)
        if DESIGN_SYSTEM_AVAILABLE:
            self.refresh_button.setStyleSheet(
                AutoFireStyleSheet.get_button_style(AutoFireColor.BUTTON_PRIMARY.value))
        controls_layout.addWidget(self.refresh_button)
        
        # Professional export button
        export_icon = (AutoFireIconTheme.get_icon('export') 
                      if DESIGN_SYSTEM_AVAILABLE else "📊")
        self.export_button = QPushButton(f"{export_icon} Export Report")
        self.export_button.clicked.connect(self._export_calculations)
        if DESIGN_SYSTEM_AVAILABLE:
            self.export_button.setStyleSheet(
                AutoFireStyleSheet.get_button_style(AutoFireColor.BUTTON_SECONDARY.value))
        controls_layout.addWidget(self.export_button)
        
        controls_layout.addStretch()
        
        # Professional auto-update toggle
        self.auto_update_checkbox = QCheckBox("Auto-update calculations")
        self.auto_update_checkbox.setChecked(True)
        if DESIGN_SYSTEM_AVAILABLE:
            self.auto_update_checkbox.setStyleSheet(AutoFireStyleSheet.get_input_style())
        controls_layout.addWidget(self.auto_update_checkbox)
        
        parent_layout.addWidget(controls_frame)
    
    def setup_connections(self):
        """Setup signal connections."""
        # Connect calculation engine signals if available
        if hasattr(self.calc_engine, 'calculation_updated'):
            self.calc_engine.calculation_updated.connect(self._schedule_update)
    
    def add_wire_segment(self, from_device: str, to_device: str, length_ft: float,
                        wire_gauge: str, current_a: float, circuit_type: str):
        """Add a wire segment to the live calculations."""
        segment = WireSegment(
            from_device=from_device,
            to_device=to_device,
            length_ft=length_ft,
            wire_gauge=wire_gauge,
            current_a=current_a,
            circuit_type=circuit_type
        )
        
        self.calc_engine.add_wire_segment(segment)
        self._schedule_update()
        
        logger.debug("Added wire segment: %s -> %s (%.1f ft)", 
                    from_device, to_device, length_ft)
    
    def update_device_current(self, device_id: str, current_a: float):
        """Update the current draw for a device."""
        self.calc_engine.update_device_load(device_id, current_a)
        self._schedule_update()
    
    def remove_wire_segment(self, from_device: str, to_device: str, length_ft: float,
                           wire_gauge: str, current_a: float, circuit_type: str):
        """Remove a wire segment from calculations."""
        segment = WireSegment(
            from_device=from_device,
            to_device=to_device,
            length_ft=length_ft,
            wire_gauge=wire_gauge,
            current_a=current_a,
            circuit_type=circuit_type
        )
        
        self.calc_engine.remove_wire_segment(segment)
        self._schedule_update()
    
    def refresh_all_calculations(self):
        """Force refresh of all calculations and display."""
        self._perform_calculations_update()
        
    def _schedule_update(self):
        """Schedule a calculation update (debounced)."""
        if self.auto_update_checkbox.isChecked():
            self.update_timer.start(500)  # 500ms delay for debouncing
    
    def _perform_calculations_update(self):
        """Perform the actual calculation update."""
        try:
            # Get all circuit analyses
            analyses = self.calc_engine.get_all_circuit_analyses()
            
            # Update the tree display
            self._update_circuit_tree(analyses)
            
            # Update calculation details
            self._update_calculation_details(analyses)
            
            # Update compliance status
            self._update_compliance_status(analyses)
            
            self.calculations_updated.emit()
            
        except Exception as e:
            logger.error("Error updating calculations: %s", e)
            self.compliance_status.setText("Calculation Error")
            self.calc_details.setText(f"Error: {e}")
    
    def _update_circuit_tree(self, analyses):
        """Update the circuit tree with current analysis data."""
        self.circuit_tree.clear()
        
        # Group analyses by panel
        panels = {}
        for circuit_id, analysis in analyses.items():
            # Extract panel name from circuit ID
            if "_" in circuit_id:
                circuit_type, panel_name = circuit_id.split("_", 1)
                panel_key = panel_name
            else:
                panel_key = "UNKNOWN"
            
            if panel_key not in panels:
                panels[panel_key] = []
            panels[panel_key].append((circuit_id, analysis))
        
        # Build tree structure
        for panel_name, circuit_list in panels.items():
            # Create panel node
            panel_item = CircuitTreeItem(self.circuit_tree)
            panel_item.item_type = "panel"
            panel_item.setText(0, f"📋 {panel_name}")
            
            # Calculate battery requirements for this panel
            try:
                battery_calc = self.calc_engine.calculate_battery_requirements(panel_name)
                panel_item.update_from_battery_calc(battery_calc)
            except Exception as e:
                logger.debug("Could not calculate battery for %s: %s", panel_name, e)
            
            # Add circuit children
            for circuit_id, analysis in circuit_list:
                circuit_item = CircuitTreeItem(panel_item)
                circuit_item.item_type = "circuit"
                circuit_item.circuit_id = circuit_id
                
                # Set circuit icon based on type
                circuit_type = analysis.circuit_type
                if circuit_type == "SLC":
                    icon = "🔗"
                elif circuit_type == "NAC":
                    icon = "🔊"
                elif circuit_type == "POWER":
                    icon = "⚡"
                else:
                    icon = "🔧"
                
                circuit_item.setText(0, f"{icon} {circuit_type} Circuit")
                circuit_item.update_from_analysis(analysis)
                
                # Add device children (simplified for now)
                if hasattr(self.calc_engine, 'circuits') and circuit_id in self.calc_engine.circuits:
                    segments = self.calc_engine.circuits[circuit_id]
                    devices = set()
                    for segment in segments:
                        devices.add(segment.to_device)
                    
                    for device_name in sorted(devices):
                        if not device_name.startswith("PANEL"):
                            device_item = CircuitTreeItem(circuit_item)
                            device_item.item_type = "device"
                            device_item.setText(0, f"📍 {device_name}")
                            
                            # Show device current if available
                            current = self.calc_engine.device_loads.get(device_name, 0.0)
                            device_item.setText(3, f"{current:.3f} A")
        
        # Expand all panel nodes by default
        self.circuit_tree.expandAll()
    
    def _update_calculation_details(self, analyses):
        """Update the detailed calculation display."""
        details_text = []
        
        details_text.append("🔥 LIVE FIRE ALARM CALCULATIONS")
        details_text.append("=" * 50)
        
        # Summary statistics
        total_circuits = len(analyses)
        total_devices = sum(a.device_count for a in analyses.values())
        total_length = sum(a.total_length_ft for a in analyses.values())
        total_current = sum(a.current_draw_a for a in analyses.values())
        
        details_text.append(f"📊 System Summary:")
        details_text.append(f"   Circuits: {total_circuits}")
        details_text.append(f"   Devices: {total_devices}")
        details_text.append(f"   Total Wire: {total_length:.0f} ft")
        details_text.append(f"   Total Current: {total_current:.3f} A")
        details_text.append("")
        
        # Circuit-by-circuit details
        for circuit_id, analysis in analyses.items():
            status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(
                analysis.compliance_status, "❓"
            )
            
            details_text.append(f"{status_icon} {circuit_id}:")
            details_text.append(f"   Voltage Drop: {analysis.total_voltage_drop:.3f}V "
                              f"({analysis.voltage_drop_percent:.1f}%)")
            details_text.append(f"   Load: {analysis.current_draw_a:.3f}A, "
                              f"Length: {analysis.total_length_ft:.0f}ft")
            
            if analysis.warnings:
                for warning in analysis.warnings:
                    details_text.append(f"   ⚠️  {warning}")
            details_text.append("")
        
        self.calc_details.setText("\n".join(details_text))
    
    def _update_compliance_status(self, analyses):
        """Update the overall compliance status."""
        total_circuits = len(analyses)
        if total_circuits == 0:
            self.compliance_status.setText("System Status: No circuits defined")
            self.nfpa_indicator.setText("NFPA 72: N/A")
            return
        
        # Count compliance status
        pass_count = sum(1 for a in analyses.values() if a.compliance_status == "PASS")
        warn_count = sum(1 for a in analyses.values() if a.compliance_status == "WARN")
        fail_count = sum(1 for a in analyses.values() if a.compliance_status == "FAIL")
        
        # Overall status
        if fail_count > 0:
            status_text = f"System Status: ❌ {fail_count} FAILED, {warn_count} warned, {pass_count} passed"
            self.compliance_status.setStyleSheet("color: red; font-weight: bold;")
            nfpa_status = "NFPA 72: ❌ NON-COMPLIANT"
        elif warn_count > 0:
            status_text = f"System Status: ⚠️ {warn_count} warnings, {pass_count} passed"
            self.compliance_status.setStyleSheet("color: orange; font-weight: bold;")
            nfpa_status = "NFPA 72: ⚠️ REVIEW REQUIRED"
        else:
            status_text = f"System Status: ✅ All {pass_count} circuits compliant"
            self.compliance_status.setStyleSheet("color: green; font-weight: bold;")
            nfpa_status = "NFPA 72: ✅ COMPLIANT"
        
        self.compliance_status.setText(status_text)
        self.nfpa_indicator.setText(nfpa_status)
    
    def _on_tree_item_clicked(self, item, column):
        """Handle tree item selection."""
        if item.item_type == "circuit" and item.circuit_id:
            self.circuit_selected.emit(item.circuit_id)
        elif item.item_type == "device":
            device_name = item.text(0).replace("📍 ", "")
            self.device_selected.emit(device_name)
    
    def _on_tree_expanded(self, item):
        """Handle tree expansion."""
        # Could add lazy loading here if needed
        pass
    
    def _export_calculations(self):
        """Export calculation results to a report."""
        # This would integrate with the Reports system (Section 10)
        logger.info("Exporting calculation report (placeholder)")
        
        # For now, just show a message
        self.calc_details.append("\n📄 Export functionality will integrate with Reports system...")


def create_enhanced_connections_tab(parent_widget):
    """Factory function to create the enhanced connections tab for the main UI."""
    connections_panel = EnhancedConnectionsPanel()
    
    # Example: Add some demo data
    connections_panel.add_wire_segment(
        "PANEL1", "SMOKE_001", 85.0, "14", 0.020, "SLC"
    )
    connections_panel.add_wire_segment(
        "SMOKE_001", "SMOKE_002", 45.0, "14", 0.020, "SLC"
    )
    connections_panel.add_wire_segment(
        "PANEL1", "HORN_001", 120.0, "12", 0.150, "NAC"
    )
    
    # Trigger initial calculation
    connections_panel.refresh_all_calculations()
    
    return connections_panel