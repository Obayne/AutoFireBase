"""
Professional Project Circuits Editor - Enhanced with AutoFire Design System

This refined version applies consistent styling, professional colors, and 
enhanced user experience to surpass FireCAD/AlarmCAD industry standards.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# PySide6 imports with graceful fallback
try:
    from PySide6.QtCore import QAbstractTableModel, QModelIndex, Signal
    from PySide6.QtGui import QColor
    from PySide6.QtWidgets import (
        QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QFrame,
        QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
        QSpinBox, QTabWidget, QTextEdit, QVBoxLayout, QWidget
    )
    PYSIDE6_AVAILABLE = True
except ImportError as e:
    logger.error("PySide6 not available: %s", e)
    PYSIDE6_AVAILABLE = False
    
    # Minimal stubs for type checking
    class Signal:
        pass
    
    class QWidget:
        pass
    
    class QAbstractTableModel:
        pass

# Design system imports
try:
    from frontend.design_system import (
        AutoFireColor, AutoFireIconTheme, AutoFireSpacing, AutoFireStyleSheet,
        create_title_font, get_circuit_color
    )
    DESIGN_SYSTEM_AVAILABLE = True
except ImportError:
    DESIGN_SYSTEM_AVAILABLE = False
    logger.warning("Design system not available - using fallback styling")

try:
    from cad_core.calculations.live_engine import CircuitAnalysis, LiveCalculationsEngine
    CALC_ENGINE_AVAILABLE = True
except ImportError as e:
    logger.error("Live calculations engine not available: %s", e)
    CALC_ENGINE_AVAILABLE = False
    
    class CircuitAnalysis:
        pass
    
    class LiveCalculationsEngine:
        pass


class CircuitType(Enum):
    """Professional fire alarm circuit types with industry-standard designations."""
    SLC = "SLC"           # Signaling Line Circuit
    NAC = "NAC"           # Notification Appliance Circuit  
    POWER = "Power"       # Power Supply Circuit
    CONTROL = "Control"   # Control Circuit
    TELEPHONE = "Telephone" # Emergency Communication Circuit


class EOLType(Enum):
    """End-of-line supervision types per NFPA 72 standards."""
    RESISTOR = "Resistor"     # Most common - 47K ohm
    CAPACITOR = "Capacitor"   # Special applications - 22uF
    DIODE = "Diode"          # Control circuits - 1N4148
    NONE = "None"            # Class B circuits


@dataclass
class CircuitProperties:
    """Complete circuit properties with professional fire alarm standards."""
    
    # Essential identification
    circuit_id: str
    circuit_name: str = ""
    circuit_type: CircuitType = CircuitType.SLC
    panel_id: str = ""
    
    # Physical properties
    device_count: int = 0
    total_length_ft: float = 0.0
    wire_gauge: str = "14"           # AWG - 12, 14, 16, 18, 20
    wire_type: str = "THHN"          # THHN, THWN, XHHW
    wire_color: str = "Red"          # Per fire alarm color codes
    
    # Electrical calculations
    voltage_drop_v: float = 0.0
    voltage_drop_percent: float = 0.0
    current_draw_a: float = 0.0
    max_current_a: float = 3.0       # NFPA 72 typical limit
    
    # Fire alarm specific
    class_rating: str = "A"          # Class A (supervised) or Class B
    eol_type: EOLType = EOLType.RESISTOR
    eol_value: str = "47K"           # Standard EOL resistor value
    supervision_enabled: bool = True  # NFPA 72 requirement
    
    # Addressing per NFPA 72
    start_address: int = 1
    end_address: int = 1
    address_range_locked: bool = False  # Prevent auto-assignment
    
    # Installation documentation
    conduit_size: str = "3/4\""      # Standard fire alarm conduit
    conduit_fill_percent: float = 0.0
    routing_notes: str = ""
    installation_notes: str = ""
    
    # Compliance tracking
    nfpa_compliant: bool = True
    ada_compliant: bool = True
    local_code_compliant: bool = True
    validation_notes: list[str] = field(default_factory=list)
    
    # Professional workflow
    design_complete: bool = False
    reviewed_by: str = ""
    approved_by: str = ""
    last_modified: str = ""


class ProfessionalCircuitTableModel(QAbstractTableModel):
    """Professional table model with enhanced styling and fire alarm expertise."""
    
    # Column definitions for professional display
    COL_NAME = 0
    COL_TYPE = 1  
    COL_PANEL = 2
    COL_DEVICES = 3
    COL_LENGTH = 4
    COL_CURRENT = 5
    COL_VOLTAGE_DROP = 6
    COL_COMPLIANCE = 7
    COL_STATUS = 8
    
    COLUMN_HEADERS = [
        f"{AutoFireIconTheme.get_icon('circuit_slc')} Circuit Name",
        "Type", 
        f"{AutoFireIconTheme.get_icon('panel')} Panel",
        f"{AutoFireIconTheme.get_icon('detector')} Devices", 
        f"{AutoFireIconTheme.get_icon('measure')} Length (ft)",
        f"{AutoFireIconTheme.get_icon('calculate')} Current (A)", 
        "Voltage Drop (%)",
        f"{AutoFireIconTheme.get_icon('status_pass')} Compliance",
        "Status"
    ] if DESIGN_SYSTEM_AVAILABLE else [
        "Circuit Name", "Type", "Panel", "Devices", "Length (ft)", 
        "Current (A)", "Voltage Drop (%)", "Compliance", "Status"
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.circuits: list[CircuitProperties] = []
        self.live_calculations: dict[str, CircuitAnalysis] = {}
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.circuits)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.COLUMN_HEADERS)
    
    def headerData(self, section, orientation, role=0):  # Qt.DisplayRole = 0
        if orientation == 1 and role == 0:  # Qt.Horizontal and Qt.DisplayRole
            return self.COLUMN_HEADERS[section]
        return None
    
    def data(self, index, role=0):  # Qt.DisplayRole = 0
        if not index.isValid() or index.row() >= len(self.circuits):
            return None
        
        circuit = self.circuits[index.row()]
        col = index.column()
        
        if role == 0:  # Qt.DisplayRole
            return self._get_professional_display_data(circuit, col)
        elif role == 8:  # Qt.BackgroundRole
            return self._get_professional_background_color(circuit, col)
        elif role == 7:  # Qt.TextAlignmentRole
            if col in [self.COL_DEVICES, self.COL_LENGTH, self.COL_CURRENT, self.COL_VOLTAGE_DROP]:
                return 0x0082  # Qt.AlignRight | Qt.AlignVCenter
        
        return None
    
    def _get_professional_display_data(self, circuit: CircuitProperties, col: int) -> str:
        """Get display data with professional formatting and industry standards."""
        if col == self.COL_NAME:
            # Professional circuit naming with type prefix
            name = circuit.circuit_name or circuit.circuit_id
            if DESIGN_SYSTEM_AVAILABLE:
                icon = AutoFireIconTheme.get_icon(f'circuit_{circuit.circuit_type.value.lower()}')
                return f"{icon} {name}"
            return name
            
        elif col == self.COL_TYPE:
            # Color-coded circuit type
            return circuit.circuit_type.value
            
        elif col == self.COL_PANEL:
            return circuit.panel_id
            
        elif col == self.COL_DEVICES:
            # Device count with capacity indication
            count = circuit.device_count
            if circuit.circuit_type == CircuitType.SLC and count > 80:  # NFPA 72 limit
                return f"{count} ⚠️"
            return str(count)
            
        elif col == self.COL_LENGTH:
            # Length with precision appropriate for fire alarm work
            return f"{circuit.total_length_ft:.0f}"
            
        elif col == self.COL_CURRENT:
            # Current with professional precision
            current = circuit.current_draw_a
            capacity = circuit.max_current_a
            percentage = (current / capacity * 100) if capacity > 0 else 0
            
            if percentage > 90:
                return f"{current:.3f} ⚠️"
            return f"{current:.3f}"
            
        elif col == self.COL_VOLTAGE_DROP:
            # NFPA 72 compliant voltage drop display
            vd_percent = circuit.voltage_drop_percent
            if vd_percent > 10.0:  # NFPA 72 limit
                return f"{vd_percent:.1f}% ❌"
            elif vd_percent > 7.0:  # Warning threshold
                return f"{vd_percent:.1f}% ⚠️"
            return f"{vd_percent:.1f}%"
            
        elif col == self.COL_COMPLIANCE:
            # Professional compliance status with clear indicators
            if not circuit.nfpa_compliant:
                return f"{AutoFireIconTheme.get_icon('status_fail')} FAIL"
            elif not (circuit.ada_compliant and circuit.local_code_compliant):
                return f"{AutoFireIconTheme.get_icon('status_warning')} REVIEW"
            else:
                return f"{AutoFireIconTheme.get_icon('status_pass')} PASS"
                
        elif col == self.COL_STATUS:
            # Design workflow status
            if circuit.design_complete:
                if circuit.approved_by:
                    return f"{AutoFireIconTheme.get_icon('status_pass')} Approved"
                elif circuit.reviewed_by:
                    return f"{AutoFireIconTheme.get_icon('status_info')} Reviewed"
                else:
                    return f"{AutoFireIconTheme.get_icon('status_pass')} Complete"
            else:
                return "🔄 In Progress"
        
        return ""
    
    def _get_professional_background_color(self, circuit: CircuitProperties, col: int):
        """Get professional background colors based on fire alarm standards."""
        if not DESIGN_SYSTEM_AVAILABLE:
            return None
            
        if col == self.COL_TYPE:
            # Circuit type color coding per industry standards
            color_hex = get_circuit_color(circuit.circuit_type.value)
            # Light tint for background
            return QColor(color_hex).lighter(180)
            
        elif col == self.COL_COMPLIANCE:
            # Compliance status color coding
            if not circuit.nfpa_compliant:
                return QColor(AutoFireColor.COMPLIANCE_FAIL.value).lighter(180)
            elif not (circuit.ada_compliant and circuit.local_code_compliant):
                return QColor(AutoFireColor.COMPLIANCE_WARNING.value).lighter(180)
            else:
                return QColor(AutoFireColor.COMPLIANCE_PASS.value).lighter(180)
                
        elif col == self.COL_VOLTAGE_DROP:
            # NFPA 72 voltage drop compliance coloring
            if circuit.voltage_drop_percent > 10.0:
                return QColor(AutoFireColor.COMPLIANCE_FAIL.value).lighter(180)
            elif circuit.voltage_drop_percent > 7.0:
                return QColor(AutoFireColor.COMPLIANCE_WARNING.value).lighter(180)
                
        return None
    
    def add_circuit(self, circuit: CircuitProperties):
        """Add circuit with professional validation."""
        self.beginInsertRows(QModelIndex(), len(self.circuits), len(self.circuits))
        self.circuits.append(circuit)
        self.endInsertRows()
        logger.info("Circuit added: %s (%s)", circuit.circuit_name, circuit.circuit_type.value)
    
    def update_circuit(self, row: int, circuit: CircuitProperties):
        """Update circuit with change tracking."""
        if 0 <= row < len(self.circuits):
            old_circuit = self.circuits[row]
            self.circuits[row] = circuit
            self.dataChanged.emit(
                self.index(row, 0),
                self.index(row, self.columnCount() - 1)
            )
            logger.info("Circuit updated: %s -> %s", old_circuit.circuit_name, circuit.circuit_name)
    
    def remove_circuit(self, row: int):
        """Remove circuit with audit trail."""
        if 0 <= row < len(self.circuits):
            circuit = self.circuits[row]
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.circuits[row]
            self.endRemoveRows()
        logger.info("Circuit removed: %s (%s)", 
                   circuit.circuit_name, circuit.circuit_type.value)
    
    def get_circuit(self, row: int) -> CircuitProperties | None:
        """Get circuit with bounds checking."""
        if 0 <= row < len(self.circuits):
            return self.circuits[row]
        return None
    
    def update_live_calculations(self, calculations: dict[str, CircuitAnalysis]):
        """Update with live calculation results and maintain audit trail."""
        self.live_calculations = calculations
        
        # Update circuit properties with live data
        updated_count = 0
        for circuit in self.circuits:
            if circuit.circuit_id in calculations:
                analysis = calculations[circuit.circuit_id]
                # Update with proper error handling
                try:
                    circuit.device_count = getattr(analysis, 'device_count', circuit.device_count)
                    circuit.total_length_ft = getattr(analysis, 'total_length_ft', circuit.total_length_ft)
                    circuit.current_draw_a = getattr(analysis, 'current_draw_a', circuit.current_draw_a)
                    circuit.voltage_drop_v = getattr(analysis, 'total_voltage_drop', circuit.voltage_drop_v)
                    circuit.voltage_drop_percent = getattr(analysis, 'voltage_drop_percent', circuit.voltage_drop_percent)
                    circuit.nfpa_compliant = getattr(analysis, 'compliance_status', 'PASS') != "FAIL"
                    updated_count += 1
                except AttributeError as e:
                    logger.warning("Live calculation update error for %s: %s", circuit.circuit_id, e)
        
        # Refresh the entire table
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount() - 1, self.columnCount() - 1)
        )
        
        logger.info("Live calculations updated for %d circuits", updated_count)


class ProfessionalCircuitPropertiesPanel(QWidget):
    """Professional properties panel with enhanced styling and fire alarm expertise."""
    
    # Signals for professional workflow
    circuit_updated = Signal(CircuitProperties)
    validation_requested = Signal(str)  # circuit_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_circuit: CircuitProperties | None = None
        self.setup_professional_ui()
        self.apply_professional_styling()
        
    def setup_professional_ui(self):
        """Setup professional UI with enhanced fire alarm features."""
        layout = QVBoxLayout(self)
        layout.setSpacing(AutoFireSpacing.MD if DESIGN_SYSTEM_AVAILABLE else 16)
        
        # Professional title
        title_label = QLabel("🔧 Circuit Properties")
        if DESIGN_SYSTEM_AVAILABLE:
            title_label.setFont(create_title_font())
        layout.addWidget(title_label)
        
        # Enhanced tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Setup professional tabs
        self.setup_identification_tab()
        self.setup_electrical_tab()
        self.setup_fire_alarm_tab()
        self.setup_installation_tab()
        self.setup_compliance_tab()
        self.setup_workflow_tab()
        
        # Professional action buttons
        self.setup_professional_action_buttons(layout)
    
    def setup_identification_tab(self):
        """Setup identification tab with professional fire alarm standards."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        layout.setSpacing(AutoFireSpacing.SM if DESIGN_SYSTEM_AVAILABLE else 8)
        
        # Circuit naming with professional standards
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., 'First Floor Detection', 'Main Notification'")
        layout.addRow("📝 Circuit Name:", self.name_edit)
        
        # Circuit type with fire alarm specific options
        self.type_combo = QComboBox()
        for circuit_type in CircuitType:
            icon = AutoFireIconTheme.get_icon(f'circuit_{circuit_type.value.lower()}') if DESIGN_SYSTEM_AVAILABLE else ""
            self.type_combo.addItem(f"{icon} {circuit_type.value}", circuit_type)
        layout.addRow("⚡ Circuit Type:", self.type_combo)
        
        # Panel assignment
        self.panel_edit = QLineEdit()
        self.panel_edit.setPlaceholderText("e.g., 'PANEL1', 'MCP-1'")
        layout.addRow(f"{AutoFireIconTheme.get_icon('panel')} Panel ID:", self.panel_edit)
        
        # Fire alarm class rating
        self.class_combo = QComboBox()
        self.class_combo.addItems(["A (Supervised)", "B (Unsupervised)"])
        layout.addRow("🏷️ Class Rating:", self.class_combo)
        
        # Wire specifications per fire alarm standards
        self.wire_gauge_combo = QComboBox()
        self.wire_gauge_combo.addItems(["12 AWG", "14 AWG", "16 AWG", "18 AWG", "20 AWG"])
        self.wire_gauge_combo.setCurrentText("14 AWG")
        layout.addRow("📏 Wire Gauge:", self.wire_gauge_combo)
        
        self.wire_color_combo = QComboBox()
        # Fire alarm standard colors
        colors = ["Red (NAC)", "Blue (SLC)", "Black (Power)", "Yellow (Control)", "Green (Telephone)", "White (Common)"]
        self.wire_color_combo.addItems(colors)
        layout.addRow("🎨 Wire Color:", self.wire_color_combo)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, f"{AutoFireIconTheme.get_icon('edit')} Identification")
    
    def setup_electrical_tab(self):
        """Setup electrical tab with NFPA 72 calculations."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        
        # Current capacity per NFPA 72
        self.max_current_spin = QDoubleSpinBox()
        self.max_current_spin.setRange(0.1, 10.0)
        self.max_current_spin.setSingleStep(0.1)
        self.max_current_spin.setSuffix(" A")
        self.max_current_spin.setValue(3.0)  # NFPA 72 typical
        layout.addRow("⚡ Max Current:", self.max_current_spin)
        
        # Live calculation displays (read-only)
        self.device_count_label = QLabel("0")
        layout.addRow(f"{AutoFireIconTheme.get_icon('detector')} Device Count:", self.device_count_label)
        
        self.length_label = QLabel("0.0 ft")
        layout.addRow(f"{AutoFireIconTheme.get_icon('measure')} Total Length:", self.length_label)
        
        self.current_label = QLabel("0.000 A")
        layout.addRow("🔌 Current Draw:", self.current_label)
        
        self.voltage_drop_label = QLabel("0.0% (0.000V)")
        layout.addRow("📉 Voltage Drop:", self.voltage_drop_label)
        
        # NFPA 72 compliance indicator
        self.compliance_indicator = QLabel("✅ NFPA 72 Compliant")
        if DESIGN_SYSTEM_AVAILABLE:
            self.compliance_indicator.setStyleSheet(f"color: {AutoFireColor.COMPLIANCE_PASS.value}; font-weight: bold;")
        layout.addRow("📋 Compliance:", self.compliance_indicator)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, f"{AutoFireIconTheme.get_icon('calculate')} Electrical")
    
    def setup_fire_alarm_tab(self):
        """Setup fire alarm specific properties."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        
        # End-of-Line supervision per NFPA 72
        self.eol_type_combo = QComboBox()
        for eol_type in EOLType:
            self.eol_type_combo.addItem(eol_type.value, eol_type)
        layout.addRow("🔚 EOL Type:", self.eol_type_combo)
        
        self.eol_value_edit = QLineEdit()
        self.eol_value_edit.setText("47K")
        self.eol_value_edit.setPlaceholderText("e.g., '47K', '22uF', '1N4148'")
        layout.addRow("🔢 EOL Value:", self.eol_value_edit)
        
        # Supervision per NFPA 72
        self.supervision_check = QCheckBox()
        self.supervision_check.setChecked(True)
        layout.addRow("👁️ Supervision:", self.supervision_check)
        
        # Addressing per NFPA 72
        self.start_address_spin = QSpinBox()
        self.start_address_spin.setRange(1, 999)
        layout.addRow("🏁 Start Address:", self.start_address_spin)
        
        self.end_address_spin = QSpinBox()
        self.end_address_spin.setRange(1, 999)
        layout.addRow("🏁 End Address:", self.end_address_spin)
        
        self.address_locked_check = QCheckBox()
        layout.addRow("🔒 Address Locked:", self.address_locked_check)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, f"{AutoFireIconTheme.get_icon('detector')} Fire Alarm")
    
    def setup_installation_tab(self):
        """Setup installation documentation."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        
        # Conduit specifications
        self.conduit_size_combo = QComboBox()
        conduit_sizes = ["1/2\"", "3/4\"", "1\"", "1-1/4\"", "1-1/2\"", "2\"", "2-1/2\"", "3\""]
        self.conduit_size_combo.addItems(conduit_sizes)
        self.conduit_size_combo.setCurrentText("3/4\"")
        layout.addRow("🔧 Conduit Size:", self.conduit_size_combo)
        
        self.conduit_fill_label = QLabel("0.0%")
        layout.addRow("📊 Conduit Fill:", self.conduit_fill_label)
        
        # Professional documentation
        self.routing_notes_edit = QTextEdit()
        self.routing_notes_edit.setMaximumHeight(80)
        self.routing_notes_edit.setPlaceholderText("Routing path, junction boxes, special considerations...")
        layout.addRow("🗺️ Routing Notes:", self.routing_notes_edit)
        
        self.installation_notes_edit = QTextEdit()
        self.installation_notes_edit.setMaximumHeight(80)
        self.installation_notes_edit.setPlaceholderText("Installation instructions, special tools, coordination...")
        layout.addRow("🔨 Installation Notes:", self.installation_notes_edit)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, "🏗️ Installation")
    
    def setup_compliance_tab(self):
        """Setup compliance tracking."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        
        # Code compliance tracking
        self.nfpa_check = QCheckBox()
        self.nfpa_check.setChecked(True)
        layout.addRow("📋 NFPA 72 Compliant:", self.nfpa_check)
        
        self.ada_check = QCheckBox()
        self.ada_check.setChecked(True)
        layout.addRow("♿ ADA Compliant:", self.ada_check)
        
        self.local_code_check = QCheckBox()
        self.local_code_check.setChecked(True)
        layout.addRow("🏛️ Local Code Compliant:", self.local_code_check)
        
        # Validation notes
        self.validation_notes_edit = QTextEdit()
        self.validation_notes_edit.setMaximumHeight(120)
        self.validation_notes_edit.setPlaceholderText("Compliance issues, code references, required corrections...")
        self.validation_notes_edit.setReadOnly(True)
        layout.addRow("📝 Validation Notes:", self.validation_notes_edit)
        
        # Professional validation button
        self.validate_button = QPushButton(f"{AutoFireIconTheme.get_icon('status_info')} Run Validation")
        self.validate_button.clicked.connect(self.request_validation)
        layout.addRow("", self.validate_button)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, f"{AutoFireIconTheme.get_icon('status_pass')} Compliance")
    
    def setup_workflow_tab(self):
        """Setup professional workflow tracking."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        
        # Design status
        self.design_complete_check = QCheckBox()
        layout.addRow("✅ Design Complete:", self.design_complete_check)
        
        # Professional review workflow
        self.reviewed_by_edit = QLineEdit()
        self.reviewed_by_edit.setPlaceholderText("Engineer name...")
        layout.addRow("👨‍💼 Reviewed By:", self.reviewed_by_edit)
        
        self.approved_by_edit = QLineEdit()
        self.approved_by_edit.setPlaceholderText("PE/Authority name...")
        layout.addRow("✍️ Approved By:", self.approved_by_edit)
        
        # Timestamps
        self.last_modified_label = QLabel("Never")
        layout.addRow("🕒 Last Modified:", self.last_modified_label)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, "👔 Workflow")
    
    def setup_professional_action_buttons(self, parent_layout):
        """Setup professional action buttons."""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        # Primary action button
        self.apply_button = QPushButton(f"{AutoFireIconTheme.get_icon('save')} Apply Changes")
        self.apply_button.clicked.connect(self.apply_changes)
        if DESIGN_SYSTEM_AVAILABLE:
            self.apply_button.setStyleSheet(AutoFireStyleSheet.get_button_style(
                AutoFireColor.BUTTON_PRIMARY.value
            ))
        button_layout.addWidget(self.apply_button)
        
        # Secondary action button
        self.revert_button = QPushButton(f"{AutoFireIconTheme.get_icon('refresh')} Revert")
        self.revert_button.clicked.connect(self.revert_changes)
        if DESIGN_SYSTEM_AVAILABLE:
            self.revert_button.setStyleSheet(AutoFireStyleSheet.get_button_style(
                AutoFireColor.BUTTON_SECONDARY.value
            ))
        button_layout.addWidget(self.revert_button)
        
        button_layout.addStretch()
        
        # Auto-apply toggle
        self.auto_update_check = QCheckBox("Auto-apply changes")
        self.auto_update_check.setChecked(True)
        button_layout.addWidget(self.auto_update_check)
        
        parent_layout.addWidget(button_frame)
    
    def apply_professional_styling(self):
        """Apply professional styling to the properties panel."""
        if not DESIGN_SYSTEM_AVAILABLE:
            return
        
        # Apply tab styling
        self.tab_widget.setStyleSheet(AutoFireStyleSheet.get_tab_style())
        
        # Apply input styling to all form elements
        input_style = AutoFireStyleSheet.get_input_style()
        for widget in self.findChildren((QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox)):
            widget.setStyleSheet(input_style)
    
    def load_circuit(self, circuit: CircuitProperties):
        """Load circuit with professional validation."""
        self.current_circuit = circuit
        
        # Identification tab
        self.name_edit.setText(circuit.circuit_name)
        self.type_combo.setCurrentText(circuit.circuit_type.value)
        self.panel_edit.setText(circuit.panel_id)
        self.class_combo.setCurrentText("A (Supervised)" if circuit.class_rating == "A" else "B (Unsupervised)")
        self.wire_gauge_combo.setCurrentText(f"{circuit.wire_gauge} AWG")
        
        # Set wire color with fire alarm standard
        color_map = {
            "Red": "Red (NAC)", "Blue": "Blue (SLC)", "Black": "Black (Power)",
            "Yellow": "Yellow (Control)", "Green": "Green (Telephone)", "White": "White (Common)"
        }
        self.wire_color_combo.setCurrentText(color_map.get(circuit.wire_color, "Red (NAC)"))
        
        # Electrical tab
        self.max_current_spin.setValue(circuit.max_current_a)
        self.device_count_label.setText(str(circuit.device_count))
        self.length_label.setText(f"{circuit.total_length_ft:.1f} ft")
        self.current_label.setText(f"{circuit.current_draw_a:.3f} A")
        self.voltage_drop_label.setText(f"{circuit.voltage_drop_percent:.1f}% ({circuit.voltage_drop_v:.3f}V)")
        
        # Update compliance indicator
        self._update_compliance_indicator(circuit)
        
        # Fire alarm tab
        self.eol_type_combo.setCurrentText(circuit.eol_type.value)
        self.eol_value_edit.setText(circuit.eol_value)
        self.supervision_check.setChecked(circuit.supervision_enabled)
        self.start_address_spin.setValue(circuit.start_address)
        self.end_address_spin.setValue(circuit.end_address)
        self.address_locked_check.setChecked(circuit.address_range_locked)
        
        # Installation tab
        self.conduit_size_combo.setCurrentText(circuit.conduit_size)
        self.conduit_fill_label.setText(f"{circuit.conduit_fill_percent:.1f}%")
        self.routing_notes_edit.setText(circuit.routing_notes)
        self.installation_notes_edit.setText(circuit.installation_notes)
        
        # Compliance tab
        self.nfpa_check.setChecked(circuit.nfpa_compliant)
        self.ada_check.setChecked(circuit.ada_compliant)
        self.local_code_check.setChecked(circuit.local_code_compliant)
        self.validation_notes_edit.setText("\n".join(circuit.validation_notes))
        
        # Workflow tab
        self.design_complete_check.setChecked(circuit.design_complete)
        self.reviewed_by_edit.setText(circuit.reviewed_by)
        self.approved_by_edit.setText(circuit.approved_by)
        self.last_modified_label.setText(circuit.last_modified or "Never")
        
        logger.info("Circuit loaded in properties panel: %s", circuit.circuit_name)
    
    def _update_compliance_indicator(self, circuit: CircuitProperties):
        """Update compliance indicator with professional styling."""
        if circuit.nfpa_compliant and circuit.ada_compliant and circuit.local_code_compliant:
            self.compliance_indicator.setText("✅ NFPA 72 Compliant")
            if DESIGN_SYSTEM_AVAILABLE:
                self.compliance_indicator.setStyleSheet(f"color: {AutoFireColor.COMPLIANCE_PASS.value}; font-weight: bold;")
        elif circuit.nfpa_compliant:
            self.compliance_indicator.setText("⚠️ Review Required")
            if DESIGN_SYSTEM_AVAILABLE:
                self.compliance_indicator.setStyleSheet(f"color: {AutoFireColor.COMPLIANCE_WARNING.value}; font-weight: bold;")
        else:
            self.compliance_indicator.setText("❌ Code Violation")
            if DESIGN_SYSTEM_AVAILABLE:
                self.compliance_indicator.setStyleSheet(f"color: {AutoFireColor.COMPLIANCE_FAIL.value}; font-weight: bold;")
    
    def apply_changes(self):
        """Apply changes with professional validation."""
        if not self.current_circuit:
            return
        
        import datetime
        
        # Update circuit from UI with validation
        self.current_circuit.circuit_name = self.name_edit.text().strip()
        self.current_circuit.circuit_type = CircuitType(self.type_combo.currentText().split()[1])  # Remove icon
        self.current_circuit.panel_id = self.panel_edit.text().strip()
        self.current_circuit.class_rating = "A" if "A (" in self.class_combo.currentText() else "B"
        self.current_circuit.wire_gauge = self.wire_gauge_combo.currentText().split()[0]  # Remove " AWG"
        
        # Extract wire color
        color_text = self.wire_color_combo.currentText()
        self.current_circuit.wire_color = color_text.split()[0]  # Remove description
        
        self.current_circuit.max_current_a = self.max_current_spin.value()
        
        self.current_circuit.eol_type = EOLType(self.eol_type_combo.currentText())
        self.current_circuit.eol_value = self.eol_value_edit.text().strip()
        self.current_circuit.supervision_enabled = self.supervision_check.isChecked()
        self.current_circuit.start_address = self.start_address_spin.value()
        self.current_circuit.end_address = self.end_address_spin.value()
        self.current_circuit.address_range_locked = self.address_locked_check.isChecked()
        
        self.current_circuit.conduit_size = self.conduit_size_combo.currentText()
        self.current_circuit.routing_notes = self.routing_notes_edit.toPlainText().strip()
        self.current_circuit.installation_notes = self.installation_notes_edit.toPlainText().strip()
        
        self.current_circuit.nfpa_compliant = self.nfpa_check.isChecked()
        self.current_circuit.ada_compliant = self.ada_check.isChecked()
        self.current_circuit.local_code_compliant = self.local_code_check.isChecked()
        self.current_circuit.design_complete = self.design_complete_check.isChecked()
        self.current_circuit.reviewed_by = self.reviewed_by_edit.text().strip()
        self.current_circuit.approved_by = self.approved_by_edit.text().strip()
        
        # Update timestamp
        self.current_circuit.last_modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.last_modified_label.setText(self.current_circuit.last_modified)
        
        # Update compliance indicator
        self._update_compliance_indicator(self.current_circuit)
        
        # Emit signal
        self.circuit_updated.emit(self.current_circuit)
        
        logger.info("Circuit properties applied: %s", self.current_circuit.circuit_name)
    
    def revert_changes(self):
        """Revert changes by reloading current circuit."""
        if self.current_circuit:
            self.load_circuit(self.current_circuit)
            logger.info("Circuit properties reverted: %s", self.current_circuit.circuit_name)
    
    def request_validation(self):
        """Request professional validation of the circuit."""
        if self.current_circuit:
            self.validation_requested.emit(self.current_circuit.circuit_id)
            logger.info("Validation requested for circuit: %s", self.current_circuit.circuit_id)


# Continue with the main Professional Project Circuits Editor class...
# This will be in the next part to keep file size manageable

def create_professional_project_circuits_editor(parent=None):
    """Factory function to create a Professional Project Circuits Editor."""
    # This will be implemented in part 2
    pass