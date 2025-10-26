"""
Live Calculations Integration for Circuit Manager
Per Master Specification Section 7: Calculations (Live)

This module bridges the CircuitManager GUI with the LiveCalculationsEngine
to provide real-time calculation updates as the user designs circuits.
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtWidgets import QGroupBox, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QFont, QColor

from cad_core.calculations.live_engine import (
    LiveCalculationsEngine,
    WireSegment,
    CircuitAnalysis,
    BatteryCalculation,
)

if TYPE_CHECKING:
    from frontend.widgets.circuit_manager import CircuitManager

logger = logging.getLogger(__name__)


class LiveCalculationsIntegration(QObject):
    """
    Integrates live calculations with the circuit manager GUI.
    
    Listens for circuit changes and updates calculations in real-time.
    Provides visual feedback for compliance issues and calculation results.
    """
    
    # Signals for calculation updates
    circuit_analysis_updated = Signal(str, object)  # circuit_id, CircuitAnalysis
    battery_calculation_updated = Signal(str, object)  # panel_id, BatteryCalculation
    compliance_warning = Signal(str, str)  # circuit_id, warning_message
    
    def __init__(self, circuit_manager: "CircuitManager", parent=None):
        super().__init__(parent)
        self.circuit_manager = circuit_manager
        self.calc_engine = LiveCalculationsEngine()
        
        # Debounce timer to avoid excessive recalculations
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._perform_calculations)
        self.update_timer.setInterval(500)  # 500ms debounce
        
        self._connect_circuit_signals()
        logger.info("Live calculations integration initialized")
    
    def _connect_circuit_signals(self):
        """Connect to circuit manager signals for automatic updates."""
        # Connect to wire/device changes
        if hasattr(self.circuit_manager, 'wire_added'):
            self.circuit_manager.wire_added.connect(self._on_wire_added)
        if hasattr(self.circuit_manager, 'wire_removed'):
            self.circuit_manager.wire_removed.connect(self._on_wire_removed)
        if hasattr(self.circuit_manager, 'device_current_changed'):
            self.circuit_manager.device_current_changed.connect(self._on_device_current_changed)
            
        logger.debug("Connected to circuit manager signals")
    
    def _on_wire_added(self, wire_data: dict):
        """Handle wire addition from circuit manager."""
        try:
            segment = WireSegment(
                from_device=wire_data.get('from_device', 'unknown'),
                to_device=wire_data.get('to_device', 'unknown'),
                length_ft=wire_data.get('length_ft', 0.0),
                wire_gauge=wire_data.get('wire_gauge', '14'),
                current_a=wire_data.get('current_a', 0.020),
                circuit_type=wire_data.get('circuit_type', 'SLC')
            )
            
            self.calc_engine.add_wire_segment(segment)
            self._schedule_update()
            
        except (ValueError, KeyError, AttributeError) as e:
            logger.error("Error adding wire segment: %s", e)
    
    def _on_wire_removed(self, wire_data: dict):
        """Handle wire removal from circuit manager."""
        try:
            segment = WireSegment(
                from_device=wire_data.get('from_device', 'unknown'),
                to_device=wire_data.get('to_device', 'unknown'),
                length_ft=wire_data.get('length_ft', 0.0),
                wire_gauge=wire_data.get('wire_gauge', '14'),
                current_a=wire_data.get('current_a', 0.020),
                circuit_type=wire_data.get('circuit_type', 'SLC')
            )
            
            self.calc_engine.remove_wire_segment(segment)
            self._schedule_update()
            
        except (ValueError, KeyError, AttributeError) as e:
            logger.error("Error removing wire segment: %s", e)
    
    def _on_device_current_changed(self, device_id: str, current_a: float):
        """Handle device current change from circuit manager."""
        try:
            self.calc_engine.update_device_load(device_id, current_a)
            self._schedule_update()
            
        except (ValueError, KeyError, AttributeError) as e:
            logger.error("Error updating device current: %s", e)
    
    def _schedule_update(self):
        """Schedule a debounced calculation update."""
        self.update_timer.start()  # Restart timer (debounce)
    
    def _perform_calculations(self):
        """Perform all live calculations and emit signals."""
        try:
            # Get all circuit analyses
            analyses = self.calc_engine.get_all_circuit_analyses()
            
            for circuit_id, analysis in analyses.items():
                # Emit circuit analysis update
                self.circuit_analysis_updated.emit(circuit_id, analysis)
                
                # Emit compliance warnings
                for warning in analysis.warnings:
                    self.compliance_warning.emit(circuit_id, warning)
            
            # Calculate battery requirements for each panel
            panel_ids = set()
            for circuit_id in analyses.keys():
                # Extract panel ID from circuit ID
                panel_id = circuit_id.split('_')[1] if '_' in circuit_id else 'PANEL1'
                panel_ids.add(panel_id)
            
            for panel_id in panel_ids:
                battery_calc = self.calc_engine.calculate_battery_requirements(panel_id)
                self.battery_calculation_updated.emit(panel_id, battery_calc)
                
        except (ValueError, KeyError, AttributeError) as e:
            logger.error("Error performing live calculations: %s", e)
    
    def get_circuit_analysis(self, circuit_id: str) -> CircuitAnalysis:
        """Get current analysis for a specific circuit."""
        return self.calc_engine.calculate_circuit_voltage_drop(circuit_id)
    
    def get_battery_calculation(self, panel_id: str) -> BatteryCalculation:
        """Get current battery calculation for a panel."""
        return self.calc_engine.calculate_battery_requirements(panel_id)


class LiveCalculationsWidget(QWidget):
    """
    Widget displaying live calculation results in the UI.
    
    Shows real-time voltage drop, battery requirements, and compliance status.
    Updates automatically as the user modifies the circuit design.
    """
    
    def __init__(self, calc_integration: LiveCalculationsIntegration, parent=None):
        super().__init__(parent)
        self.calc_integration = calc_integration
        self.circuit_analyses = {}
        self.battery_calculations = {}
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Setup the calculations display UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Live Calculations")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Circuit Analysis Section
        self.circuit_group = QGroupBox("Circuit Analysis")
        circuit_layout = QVBoxLayout(self.circuit_group)
        
        self.circuit_table = QTableWidget()
        self.circuit_table.setColumnCount(6)
        self.circuit_table.setHorizontalHeaderLabels([
            "Circuit", "Type", "Voltage Drop", "Status", "Devices", "Length"
        ])
        self.circuit_table.horizontalHeader().setStretchLastSection(True)
        circuit_layout.addWidget(self.circuit_table)
        
        layout.addWidget(self.circuit_group)
        
        # Battery Calculation Section
        self.battery_group = QGroupBox("Battery Requirements")
        battery_layout = QVBoxLayout(self.battery_group)
        
        self.battery_table = QTableWidget()
        self.battery_table.setColumnCount(5)
        self.battery_table.setHorizontalHeaderLabels([
            "Panel", "Standby (A)", "Alarm (A)", "Required (AH)", "Recommended"
        ])
        self.battery_table.horizontalHeader().setStretchLastSection(True)
        battery_layout.addWidget(self.battery_table)
        
        layout.addWidget(self.battery_group)
        
        # Compliance Summary
        self.compliance_group = QGroupBox("Compliance Status")
        compliance_layout = QVBoxLayout(self.compliance_group)
        
        self.compliance_label = QLabel("All circuits compliant")
        self.compliance_label.setStyleSheet("color: green; font-weight: bold;")
        compliance_layout.addWidget(self.compliance_label)
        
        layout.addWidget(self.compliance_group)
    
    def _connect_signals(self):
        """Connect to calculation integration signals."""
        self.calc_integration.circuit_analysis_updated.connect(self._update_circuit_analysis)
        self.calc_integration.battery_calculation_updated.connect(self._update_battery_calculation)
        self.calc_integration.compliance_warning.connect(self._update_compliance_status)
    
    def _update_circuit_analysis(self, circuit_id: str, analysis: CircuitAnalysis):
        """Update circuit analysis display."""
        self.circuit_analyses[circuit_id] = analysis
        self._refresh_circuit_table()
    
    def _update_battery_calculation(self, panel_id: str, calculation: BatteryCalculation):
        """Update battery calculation display."""
        self.battery_calculations[panel_id] = calculation
        self._refresh_battery_table()
    
    def _update_compliance_status(self, _circuit_id: str, warning: str):
        """Update compliance status display."""
        self.compliance_label.setText(f"Warning: {warning}")
        self.compliance_label.setStyleSheet("color: orange; font-weight: bold;")
    
    def _refresh_circuit_table(self):
        """Refresh the circuit analysis table."""
        self.circuit_table.setRowCount(len(self.circuit_analyses))
        
        for row, (circuit_id, analysis) in enumerate(self.circuit_analyses.items()):
            self.circuit_table.setItem(row, 0, QTableWidgetItem(circuit_id))
            self.circuit_table.setItem(row, 1, QTableWidgetItem(analysis.circuit_type))
            
            # Voltage drop with color coding
            vd_item = QTableWidgetItem(f"{analysis.voltage_drop_percent:.1f}%")
            if analysis.compliance_status == "FAIL":
                vd_item.setBackground(QColor(255, 200, 200))  # Light red
            elif analysis.compliance_status == "WARN":
                vd_item.setBackground(QColor(255, 255, 200))  # Light yellow
            else:
                vd_item.setBackground(QColor(200, 255, 200))  # Light green
            self.circuit_table.setItem(row, 2, vd_item)
            
            self.circuit_table.setItem(row, 3, QTableWidgetItem(analysis.compliance_status))
            self.circuit_table.setItem(row, 4, QTableWidgetItem(str(analysis.device_count)))
            self.circuit_table.setItem(row, 5, QTableWidgetItem(f"{analysis.total_length_ft:.0f}ft"))
    
    def _refresh_battery_table(self):
        """Refresh the battery calculation table."""
        self.battery_table.setRowCount(len(self.battery_calculations))
        
        for row, (panel_id, calc) in enumerate(self.battery_calculations.items()):
            self.battery_table.setItem(row, 0, QTableWidgetItem(panel_id))
            self.battery_table.setItem(row, 1, QTableWidgetItem(f"{calc.standby_current_a:.3f}"))
            self.battery_table.setItem(row, 2, QTableWidgetItem(f"{calc.alarm_current_a:.3f}"))
            self.battery_table.setItem(row, 3, QTableWidgetItem(f"{calc.total_required_ah:.1f}"))
            self.battery_table.setItem(row, 4, QTableWidgetItem(f"{calc.recommended_ah}AH"))