"""
Project Circuits Editor - Centralized Circuit Management Interface

Per Master Specification Section 6, provides comprehensive circuit management
with table view, naming, properties, batch operations, and live calculations.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# PySide6 imports (using try/except for graceful fallback)
try:
    from PySide6.QtCore import QAbstractTableModel, QModelIndex, Signal
    from PySide6.QtGui import QColor, QFont
    from PySide6.QtWidgets import (
        QAbstractItemView, QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QGroupBox,
        QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QScrollArea,
        QSpinBox, QSplitter, QTabWidget, QTableView, QTextEdit, QVBoxLayout,
        QWidget
    )
    PYSIDE6_AVAILABLE = True
except ImportError as e:
    logger.error("Failed to import PySide6: %s", e)
    PYSIDE6_AVAILABLE = False
    
    # Minimal stubs for type checking
    class Signal: pass
    class QWidget: pass
    class QAbstractTableModel: pass
    class Qt: pass
    class QModelIndex: pass
    class QVariant: pass

try:
    from cad_core.calculations.live_engine import CircuitAnalysis, LiveCalculationsEngine
except ImportError as e:
    logger.error("Failed to import live calculations engine: %s", e)
    class CircuitAnalysis: pass
    class LiveCalculationsEngine: pass

logger = logging.getLogger(__name__)


class CircuitType(Enum):
    """Standard fire alarm circuit types."""
    SLC = "SLC"
    NAC = "NAC" 
    POWER = "Power"
    CONTROL = "Control"
    TELEPHONE = "Telephone"


class EOLType(Enum):
    """End-of-line termination types."""
    RESISTOR = "Resistor"
    CAPACITOR = "Capacitor"
    DIODE = "Diode"
    NONE = "None"


@dataclass
class CircuitProperties:
    """Complete circuit properties for the Project Circuits Editor."""
    
    # Basic identification
    circuit_id: str
    circuit_name: str = ""
    circuit_type: CircuitType = CircuitType.SLC
    panel_id: str = ""
    
    # Physical properties
    device_count: int = 0
    total_length_ft: float = 0.0
    wire_gauge: str = "14"
    wire_type: str = "THHN"
    wire_color: str = "Red"
    
    # Electrical properties
    voltage_drop_v: float = 0.0
    voltage_drop_percent: float = 0.0
    current_draw_a: float = 0.0
    max_current_a: float = 3.0
    
    # Fire alarm specific
    class_rating: str = "A"  # Class A or Class B
    eol_type: EOLType = EOLType.RESISTOR
    eol_value: str = "47K"
    supervision_enabled: bool = True
    
    # Addressing
    start_address: int = 1
    end_address: int = 1
    address_range_locked: bool = False
    
    # Path and installation
    conduit_size: str = "3/4\""
    conduit_fill_percent: float = 0.0
    routing_notes: str = ""
    installation_notes: str = ""
    
    # Compliance and validation
    nfpa_compliant: bool = True
    ada_compliant: bool = True
    local_code_compliant: bool = True
    validation_notes: list[str] = field(default_factory=list)
    
    # Status and workflow
    design_complete: bool = False
    reviewed_by: str = ""
    approved_by: str = ""
    last_modified: str = ""


class CircuitTableModel(QAbstractTableModel):
    """Table model for displaying circuits in the Project Circuits Editor."""
    
    # Define column indices
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
        "Circuit Name", "Type", "Panel", "Devices", "Length (ft)", 
        "Current", "Voltage Drop", "Compliance", "Status"
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
            return self._get_display_data(circuit, col)
        elif role == 8:  # Qt.BackgroundRole
            return self._get_background_color(circuit, col)
        elif role == 7:  # Qt.TextAlignmentRole
            if col in [self.COL_DEVICES, self.COL_LENGTH, self.COL_CURRENT, self.COL_VOLTAGE_DROP]:
                return 0x0082  # Qt.AlignRight | Qt.AlignVCenter
        
        return None
    
    def _get_display_data(self, circuit: CircuitProperties, col: int) -> str:
        """Get display data for a specific circuit and column."""
        if col == self.COL_NAME:
            return circuit.circuit_name or circuit.circuit_id
        elif col == self.COL_TYPE:
            return circuit.circuit_type.value
        elif col == self.COL_PANEL:
            return circuit.panel_id
        elif col == self.COL_DEVICES:
            return str(circuit.device_count)
        elif col == self.COL_LENGTH:
            return f"{circuit.total_length_ft:.0f}"
        elif col == self.COL_CURRENT:
            return f"{circuit.current_draw_a:.3f}"
        elif col == self.COL_VOLTAGE_DROP:
            return f"{circuit.voltage_drop_percent:.1f}%"
        elif col == self.COL_COMPLIANCE:
            if circuit.nfpa_compliant and circuit.ada_compliant and circuit.local_code_compliant:
                return "✅ PASS"
            elif circuit.nfpa_compliant:
                return "⚠️ REVIEW"
            else:
                return "❌ FAIL"
        elif col == self.COL_STATUS:
            if circuit.design_complete:
                return "✅ Complete"
            else:
                return "🔄 In Progress"
        return ""
    
    def _get_background_color(self, circuit: CircuitProperties, col: int):
        """Get background color for compliance status."""
        if col == self.COL_COMPLIANCE:
            if not circuit.nfpa_compliant:
                return QColor(255, 200, 200)  # Light red
            elif not (circuit.ada_compliant and circuit.local_code_compliant):
                return QColor(255, 255, 200)  # Light yellow
            else:
                return QColor(200, 255, 200)  # Light green
        elif col == self.COL_VOLTAGE_DROP:
            if circuit.voltage_drop_percent > 10.0:  # NFPA 72 limit
                return QColor(255, 200, 200)  # Light red
            elif circuit.voltage_drop_percent > 7.0:  # Warning threshold
                return QColor(255, 255, 200)  # Light yellow
        return None
    
    def add_circuit(self, circuit: CircuitProperties):
        """Add a new circuit to the model."""
        self.beginInsertRows(QModelIndex(), len(self.circuits), len(self.circuits))
        self.circuits.append(circuit)
        self.endInsertRows()
    
    def update_circuit(self, row: int, circuit: CircuitProperties):
        """Update an existing circuit."""
        if 0 <= row < len(self.circuits):
            self.circuits[row] = circuit
            self.dataChanged.emit(
                self.index(row, 0),
                self.index(row, self.columnCount() - 1)
            )
    
    def remove_circuit(self, row: int):
        """Remove a circuit from the model."""
        if 0 <= row < len(self.circuits):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.circuits[row]
            self.endRemoveRows()
    
    def get_circuit(self, row: int) -> CircuitProperties | None:
        """Get circuit at the specified row."""
        if 0 <= row < len(self.circuits):
            return self.circuits[row]
        return None
    
    def update_live_calculations(self, calculations: dict[str, CircuitAnalysis]):
        """Update with live calculation results."""
        self.live_calculations = calculations
        
        # Update circuit properties with live data
        for circuit in self.circuits:
            if circuit.circuit_id in calculations:
                analysis = calculations[circuit.circuit_id]
                circuit.device_count = analysis.device_count
                circuit.total_length_ft = analysis.total_length_ft
                circuit.current_draw_a = analysis.current_draw_a
                circuit.voltage_drop_v = analysis.total_voltage_drop
                circuit.voltage_drop_percent = analysis.voltage_drop_percent
                circuit.nfpa_compliant = analysis.compliance_status != "FAIL"
        
        # Refresh the entire table
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount() - 1, self.columnCount() - 1)
        )


class CircuitPropertiesPanel(QWidget):
    """Panel for editing detailed circuit properties."""
    
    # Signals
    circuit_updated = Signal(CircuitProperties)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_circuit: CircuitProperties | None = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the properties panel UI."""
        layout = QVBoxLayout(self)
        
        # Create tab widget for organized properties
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Basic properties tab
        self.setup_basic_tab()
        
        # Electrical properties tab
        self.setup_electrical_tab()
        
        # Fire alarm specific tab
        self.setup_fire_alarm_tab()
        
        # Installation tab
        self.setup_installation_tab()
        
        # Compliance tab
        self.setup_compliance_tab()
        
        # Action buttons
        self.setup_action_buttons(layout)
    
    def setup_basic_tab(self):
        """Setup basic circuit properties tab."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter circuit name...")
        layout.addRow("Circuit Name:", self.name_edit)
        
        self.type_combo = QComboBox()
        for circuit_type in CircuitType:
            self.type_combo.addItem(circuit_type.value, circuit_type)
        layout.addRow("Circuit Type:", self.type_combo)
        
        self.panel_edit = QLineEdit()
        layout.addRow("Panel ID:", self.panel_edit)
        
        self.class_combo = QComboBox()
        self.class_combo.addItems(["A", "B"])
        layout.addRow("Class Rating:", self.class_combo)
        
        self.wire_gauge_combo = QComboBox()
        self.wire_gauge_combo.addItems(["12", "14", "16", "18", "20"])
        self.wire_gauge_combo.setCurrentText("14")
        layout.addRow("Wire Gauge:", self.wire_gauge_combo)
        
        self.wire_color_combo = QComboBox()
        self.wire_color_combo.addItems(["Red", "Blue", "Black", "White", "Yellow", "Green"])
        layout.addRow("Wire Color:", self.wire_color_combo)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, "Basic")
    
    def setup_electrical_tab(self):
        """Setup electrical properties tab."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        
        self.max_current_spin = QDoubleSpinBox()
        self.max_current_spin.setRange(0.1, 10.0)
        self.max_current_spin.setSingleStep(0.1)
        self.max_current_spin.setSuffix(" A")
        self.max_current_spin.setValue(3.0)
        layout.addRow("Max Current:", self.max_current_spin)
        
        # Read-only calculated values
        self.device_count_label = QLabel("0")
        layout.addRow("Device Count:", self.device_count_label)
        
        self.length_label = QLabel("0.0 ft")
        layout.addRow("Total Length:", self.length_label)
        
        self.current_label = QLabel("0.000 A")
        layout.addRow("Current Draw:", self.current_label)
        
        self.voltage_drop_label = QLabel("0.0% (0.000V)")
        layout.addRow("Voltage Drop:", self.voltage_drop_label)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, "Electrical")
    
    def setup_fire_alarm_tab(self):
        """Setup fire alarm specific properties tab."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        
        self.eol_type_combo = QComboBox()
        for eol_type in EOLType:
            self.eol_type_combo.addItem(eol_type.value, eol_type)
        layout.addRow("EOL Type:", self.eol_type_combo)
        
        self.eol_value_edit = QLineEdit()
        self.eol_value_edit.setText("47K")
        layout.addRow("EOL Value:", self.eol_value_edit)
        
        self.supervision_check = QCheckBox()
        self.supervision_check.setChecked(True)
        layout.addRow("Supervision:", self.supervision_check)
        
        self.start_address_spin = QSpinBox()
        self.start_address_spin.setRange(1, 999)
        layout.addRow("Start Address:", self.start_address_spin)
        
        self.end_address_spin = QSpinBox()
        self.end_address_spin.setRange(1, 999)
        layout.addRow("End Address:", self.end_address_spin)
        
        self.address_locked_check = QCheckBox()
        layout.addRow("Address Locked:", self.address_locked_check)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, "Fire Alarm")
    
    def setup_installation_tab(self):
        """Setup installation properties tab."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        
        self.conduit_size_combo = QComboBox()
        self.conduit_size_combo.addItems([
            "1/2\"", "3/4\"", "1\"", "1-1/4\"", "1-1/2\"", "2\"", "2-1/2\"", "3\""
        ])
        self.conduit_size_combo.setCurrentText("3/4\"")
        layout.addRow("Conduit Size:", self.conduit_size_combo)
        
        self.conduit_fill_label = QLabel("0.0%")
        layout.addRow("Conduit Fill:", self.conduit_fill_label)
        
        self.routing_notes_edit = QTextEdit()
        self.routing_notes_edit.setMaximumHeight(80)
        self.routing_notes_edit.setPlaceholderText("Enter routing notes...")
        layout.addRow("Routing Notes:", self.routing_notes_edit)
        
        self.installation_notes_edit = QTextEdit()
        self.installation_notes_edit.setMaximumHeight(80)
        self.installation_notes_edit.setPlaceholderText("Enter installation notes...")
        layout.addRow("Installation Notes:", self.installation_notes_edit)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, "Installation")
    
    def setup_compliance_tab(self):
        """Setup compliance properties tab."""
        widget = QScrollArea()
        content = QWidget()
        layout = QFormLayout(content)
        
        self.nfpa_check = QCheckBox()
        self.nfpa_check.setChecked(True)
        layout.addRow("NFPA 72 Compliant:", self.nfpa_check)
        
        self.ada_check = QCheckBox()
        self.ada_check.setChecked(True)
        layout.addRow("ADA Compliant:", self.ada_check)
        
        self.local_code_check = QCheckBox()
        self.local_code_check.setChecked(True)
        layout.addRow("Local Code Compliant:", self.local_code_check)
        
        self.validation_notes_edit = QTextEdit()
        self.validation_notes_edit.setMaximumHeight(100)
        self.validation_notes_edit.setPlaceholderText("Validation notes will appear here...")
        self.validation_notes_edit.setReadOnly(True)
        layout.addRow("Validation Notes:", self.validation_notes_edit)
        
        self.design_complete_check = QCheckBox()
        layout.addRow("Design Complete:", self.design_complete_check)
        
        self.reviewed_by_edit = QLineEdit()
        layout.addRow("Reviewed By:", self.reviewed_by_edit)
        
        self.approved_by_edit = QLineEdit()
        layout.addRow("Approved By:", self.approved_by_edit)
        
        widget.setWidget(content)
        widget.setWidgetResizable(True)
        self.tab_widget.addTab(widget, "Compliance")
    
    def setup_action_buttons(self, parent_layout):
        """Setup action buttons for the properties panel."""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_changes)
        button_layout.addWidget(self.apply_button)
        
        self.revert_button = QPushButton("Revert")
        self.revert_button.clicked.connect(self.revert_changes)
        button_layout.addWidget(self.revert_button)
        
        button_layout.addStretch()
        
        self.auto_update_check = QCheckBox("Auto-apply")
        self.auto_update_check.setChecked(True)
        button_layout.addWidget(self.auto_update_check)
        
        parent_layout.addWidget(button_frame)
    
    def load_circuit(self, circuit: CircuitProperties):
        """Load circuit properties into the editor."""
        self.current_circuit = circuit
        
        # Basic tab
        self.name_edit.setText(circuit.circuit_name)
        self.type_combo.setCurrentText(circuit.circuit_type.value)
        self.panel_edit.setText(circuit.panel_id)
        self.class_combo.setCurrentText(circuit.class_rating)
        self.wire_gauge_combo.setCurrentText(circuit.wire_gauge)
        self.wire_color_combo.setCurrentText(circuit.wire_color)
        
        # Electrical tab
        self.max_current_spin.setValue(circuit.max_current_a)
        self.device_count_label.setText(str(circuit.device_count))
        self.length_label.setText(f"{circuit.total_length_ft:.1f} ft")
        self.current_label.setText(f"{circuit.current_draw_a:.3f} A")
        self.voltage_drop_label.setText(
            f"{circuit.voltage_drop_percent:.1f}% ({circuit.voltage_drop_v:.3f}V)"
        )
        
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
        self.design_complete_check.setChecked(circuit.design_complete)
        self.reviewed_by_edit.setText(circuit.reviewed_by)
        self.approved_by_edit.setText(circuit.approved_by)
    
    def apply_changes(self):
        """Apply changes to the current circuit."""
        if not self.current_circuit:
            return
        
        # Update circuit properties from UI
        self.current_circuit.circuit_name = self.name_edit.text()
        self.current_circuit.circuit_type = CircuitType(self.type_combo.currentText())
        self.current_circuit.panel_id = self.panel_edit.text()
        self.current_circuit.class_rating = self.class_combo.currentText()
        self.current_circuit.wire_gauge = self.wire_gauge_combo.currentText()
        self.current_circuit.wire_color = self.wire_color_combo.currentText()
        
        self.current_circuit.max_current_a = self.max_current_spin.value()
        
        self.current_circuit.eol_type = EOLType(self.eol_type_combo.currentText())
        self.current_circuit.eol_value = self.eol_value_edit.text()
        self.current_circuit.supervision_enabled = self.supervision_check.isChecked()
        self.current_circuit.start_address = self.start_address_spin.value()
        self.current_circuit.end_address = self.end_address_spin.value()
        self.current_circuit.address_range_locked = self.address_locked_check.isChecked()
        
        self.current_circuit.conduit_size = self.conduit_size_combo.currentText()
        self.current_circuit.routing_notes = self.routing_notes_edit.toPlainText()
        self.current_circuit.installation_notes = self.installation_notes_edit.toPlainText()
        
        self.current_circuit.nfpa_compliant = self.nfpa_check.isChecked()
        self.current_circuit.ada_compliant = self.ada_check.isChecked()
        self.current_circuit.local_code_compliant = self.local_code_check.isChecked()
        self.current_circuit.design_complete = self.design_complete_check.isChecked()
        self.current_circuit.reviewed_by = self.reviewed_by_edit.text()
        self.current_circuit.approved_by = self.approved_by_edit.text()
        
        # Emit signal
        self.circuit_updated.emit(self.current_circuit)
    
    def revert_changes(self):
        """Revert changes by reloading the current circuit."""
        if self.current_circuit:
            self.load_circuit(self.current_circuit)


class ProjectCircuitsEditor(QWidget):
    """
    Complete Project Circuits Editor per Master Specification Section 6.
    
    Provides centralized circuit management with table view, properties editor,
    batch operations, and integration with live calculations engine.
    """
    
    # Signals
    circuit_selected = Signal(str)  # circuit_id
    circuits_modified = Signal()
    export_requested = Signal(str)  # export_type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.calc_engine: LiveCalculationsEngine | None = None
        self.setup_ui()
        self.setup_connections()
        
        logger.info("Project Circuits Editor initialized")
    
    def setup_ui(self):
        """Setup the main UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header with title and tools
        self.setup_header(layout)
        
        # Main content with splitter
        splitter = QSplitter()
        layout.addWidget(splitter)
        
        # Left side: Circuit table
        self.setup_circuit_table(splitter)
        
        # Right side: Properties panel
        self.setup_properties_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([700, 400])
        
        # Status bar
        self.setup_status_bar(layout)
    
    def setup_header(self, parent_layout):
        """Setup header with title and toolbar."""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title_label = QLabel("🔌 Project Circuits Editor")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Toolbar buttons
        self.new_circuit_button = QPushButton("➕ New Circuit")
        self.new_circuit_button.clicked.connect(self.create_new_circuit)
        header_layout.addWidget(self.new_circuit_button)
        
        self.duplicate_button = QPushButton("📋 Duplicate")
        self.duplicate_button.clicked.connect(self.duplicate_selected_circuit)
        self.duplicate_button.setEnabled(False)
        header_layout.addWidget(self.duplicate_button)
        
        self.delete_button = QPushButton("🗑️ Delete")
        self.delete_button.clicked.connect(self.delete_selected_circuit)
        self.delete_button.setEnabled(False)
        header_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.refresh_calculations)
        header_layout.addWidget(self.refresh_button)
        
        self.export_button = QPushButton("📊 Export")
        self.export_button.clicked.connect(self.show_export_menu)
        header_layout.addWidget(self.export_button)
        
        parent_layout.addWidget(header_frame)
    
    def setup_circuit_table(self, parent):
        """Setup the main circuit table."""
        table_group = QGroupBox("Circuit Overview")
        table_layout = QVBoxLayout(table_group)
        
        # Create table model and view
        self.table_model = CircuitTableModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)

        # Configure table
        # Use explicit enum for PySide6 API compatibility
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        
        # Configure columns
        header = self.table_view.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 150)  # Circuit Name
        header.resizeSection(1, 80)   # Type
        header.resizeSection(2, 80)   # Panel
        header.resizeSection(3, 80)   # Devices
        header.resizeSection(4, 100)  # Length
        header.resizeSection(5, 100)  # Current
        header.resizeSection(6, 120)  # Voltage Drop
        header.resizeSection(7, 100)  # Compliance
        
        table_layout.addWidget(self.table_view)
        
        # Table controls
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter circuits...")
        self.filter_edit.textChanged.connect(self.filter_circuits)
        controls_layout.addWidget(QLabel("Filter:"))
        controls_layout.addWidget(self.filter_edit)
        
        controls_layout.addStretch()
        
        self.circuit_count_label = QLabel("0 circuits")
        controls_layout.addWidget(self.circuit_count_label)
        
        table_layout.addWidget(controls_frame)
        parent.addWidget(table_group)
    
    def setup_properties_panel(self, parent):
        """Setup the circuit properties panel."""
        self.properties_panel = CircuitPropertiesPanel()
        parent.addWidget(self.properties_panel)
    
    def setup_status_bar(self, parent_layout):
        """Setup status bar."""
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.auto_refresh_check = QCheckBox("Auto-refresh calculations")
        self.auto_refresh_check.setChecked(True)
        status_layout.addWidget(self.auto_refresh_check)
        
        parent_layout.addWidget(status_frame)
    
    def setup_connections(self):
        """Setup signal connections."""
        # Table selection
        self.table_view.selectionModel().currentRowChanged.connect(self.on_circuit_selected)
        
        # Properties panel
        self.properties_panel.circuit_updated.connect(self.on_circuit_updated)
    
    def set_live_calculations_engine(self, engine: LiveCalculationsEngine):
        """Set the live calculations engine for real-time updates."""
        self.calc_engine = engine
    
    def create_new_circuit(self):
        """Create a new circuit."""
        circuit = CircuitProperties(
            circuit_id=f"CIRCUIT_{len(self.table_model.circuits) + 1:03d}",
            circuit_name=f"New Circuit {len(self.table_model.circuits) + 1}",
            panel_id="PANEL1"
        )
        
        self.table_model.add_circuit(circuit)
        self.update_circuit_count()
        self.status_label.setText("New circuit created")
    
    def duplicate_selected_circuit(self):
        """Duplicate the selected circuit."""
        current_row = self.table_view.currentIndex().row()
        if current_row >= 0:
            original = self.table_model.get_circuit(current_row)
            if original:
                new_circuit = CircuitProperties(
                    circuit_id=f"CIRCUIT_{len(self.table_model.circuits) + 1:03d}",
                    circuit_name=f"{original.circuit_name} (Copy)",
                    circuit_type=original.circuit_type,
                    panel_id=original.panel_id,
                    wire_gauge=original.wire_gauge,
                    wire_color=original.wire_color,
                    class_rating=original.class_rating,
                    eol_type=original.eol_type,
                    eol_value=original.eol_value,
                    max_current_a=original.max_current_a
                )
                
                self.table_model.add_circuit(new_circuit)
                self.update_circuit_count()
                self.status_label.setText("Circuit duplicated")
    
    def delete_selected_circuit(self):
        """Delete the selected circuit."""
        current_row = self.table_view.currentIndex().row()
        if current_row >= 0:
            circuit = self.table_model.get_circuit(current_row)
            if circuit:
                reply = QMessageBox.question(
                    self, "Delete Circuit",
                    f"Are you sure you want to delete circuit '{circuit.circuit_name}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.table_model.remove_circuit(current_row)
                    self.update_circuit_count()
                    self.status_label.setText("Circuit deleted")
    
    def on_circuit_selected(self, current, previous):
        """Handle circuit selection in the table."""
        if current.isValid():
            circuit = self.table_model.get_circuit(current.row())
            if circuit:
                self.properties_panel.load_circuit(circuit)
                self.circuit_selected.emit(circuit.circuit_id)
                
                # Enable/disable buttons
                self.duplicate_button.setEnabled(True)
                self.delete_button.setEnabled(True)
        else:
            self.duplicate_button.setEnabled(False)
            self.delete_button.setEnabled(False)
    
    def on_circuit_updated(self, circuit: CircuitProperties):
        """Handle circuit property updates."""
        current_row = self.table_view.currentIndex().row()
        if current_row >= 0:
            self.table_model.update_circuit(current_row, circuit)
            self.circuits_modified.emit()
            self.status_label.setText(f"Circuit '{circuit.circuit_name}' updated")
    
    def refresh_calculations(self):
        """Refresh calculations from the live engine."""
        if self.calc_engine:
            try:
                calculations = self.calc_engine.get_all_circuit_analyses()
                self.table_model.update_live_calculations(calculations)
                self.status_label.setText("Calculations refreshed")
            except Exception as e:
                logger.error("Error refreshing calculations: %s", e)
                self.status_label.setText("Error refreshing calculations")
    
    def filter_circuits(self, filter_text: str):
        """Filter circuits based on search text."""
        # Simple filtering - could be enhanced with proxy model
        filter_text = filter_text.lower()
        for row in range(self.table_model.rowCount()):
            circuit = self.table_model.get_circuit(row)
            if circuit:
                show_row = (
                    filter_text in circuit.circuit_name.lower() or
                    filter_text in circuit.circuit_id.lower() or
                    filter_text in circuit.panel_id.lower() or
                    filter_text in circuit.circuit_type.value.lower()
                )
                self.table_view.setRowHidden(row, not show_row)
    
    def update_circuit_count(self):
        """Update the circuit count display."""
        count = self.table_model.rowCount()
        self.circuit_count_label.setText(f"{count} circuit{'s' if count != 1 else ''}")
    
    def show_export_menu(self):
        """Show export options menu."""
        # This would integrate with the Reports system (Section 10)
        QMessageBox.information(
            self, "Export Circuits",
            "Circuit export functionality will integrate with the Reports system.\n\n"
            "Available exports:\n"
            "• Circuit Schedule (CSV/Excel)\n"
            "• Cable Schedule\n"
            "• Riser Diagrams\n"
            "• Compliance Report"
        )
    
    def load_sample_circuits(self):
        """Load sample circuits for demonstration."""
        sample_circuits = [
            CircuitProperties(
                circuit_id="SLC_001",
                circuit_name="First Floor Detection",
                circuit_type=CircuitType.SLC,
                panel_id="PANEL1",
                device_count=6,
                total_length_ft=285.0,
                current_draw_a=0.120,
                voltage_drop_percent=0.8,
                wire_gauge="14",
                wire_color="Red"
            ),
            CircuitProperties(
                circuit_id="NAC_001", 
                circuit_name="First Floor Notification",
                circuit_type=CircuitType.NAC,
                panel_id="PANEL1",
                device_count=8,
                total_length_ft=420.0,
                current_draw_a=1.200,
                voltage_drop_percent=3.2,
                wire_gauge="12",
                wire_color="Red"
            ),
            CircuitProperties(
                circuit_id="SLC_002",
                circuit_name="Second Floor Detection", 
                circuit_type=CircuitType.SLC,
                panel_id="PANEL1",
                device_count=4,
                total_length_ft=195.0,
                current_draw_a=0.080,
                voltage_drop_percent=0.6,
                wire_gauge="14",
                wire_color="Blue"
            )
        ]
        
        for circuit in sample_circuits:
            self.table_model.add_circuit(circuit)
        
        self.update_circuit_count()
        self.status_label.setText("Sample circuits loaded")


def create_project_circuits_editor(parent=None) -> ProjectCircuitsEditor:
    """Factory function to create a Project Circuits Editor."""
    editor = ProjectCircuitsEditor(parent)
    
    # Load sample data for demonstration
    editor.load_sample_circuits()
    
    return editor