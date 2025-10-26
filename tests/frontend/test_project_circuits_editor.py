"""
Test suite for Project Circuits Editor

Tests the centralized circuit management interface including:
- Circuit table model functionality
- Properties panel editing
- Live calculations integration  
- Batch operations
- Export functionality
"""

import pytest
import logging
from unittest.mock import Mock, patch

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    pytest.skip("PySide6 not available", allow_module_level=True)

from frontend.panels.project_circuits_editor import (
    ProjectCircuitsEditor, CircuitProperties, CircuitType, EOLType,
    CircuitTableModel, CircuitPropertiesPanel, create_project_circuits_editor
)

logger = logging.getLogger(__name__)


class TestCircuitProperties:
    """Test circuit properties data structure."""
    
    def test_circuit_properties_defaults(self):
        """Test default circuit properties values."""
        circuit = CircuitProperties(circuit_id="TEST_001")
        
        assert circuit.circuit_id == "TEST_001"
        assert circuit.circuit_name == ""
        assert circuit.circuit_type == CircuitType.SLC
        assert circuit.panel_id == ""
        assert circuit.device_count == 0
        assert circuit.total_length_ft == 0.0
        assert circuit.wire_gauge == "14"
        assert circuit.wire_color == "Red"
        assert circuit.max_current_a == 3.0
        assert circuit.class_rating == "A"
        assert circuit.eol_type == EOLType.RESISTOR
        assert circuit.eol_value == "47K"
        assert circuit.supervision_enabled is True
        assert circuit.nfpa_compliant is True
        assert circuit.design_complete is False
        assert circuit.validation_notes == []
    
    def test_circuit_properties_custom_values(self):
        """Test circuit properties with custom values."""
        circuit = CircuitProperties(
            circuit_id="NAC_002",
            circuit_name="Main Floor Notification",
            circuit_type=CircuitType.NAC,
            panel_id="PANEL1",
            device_count=12,
            total_length_ft=385.5,
            wire_gauge="12",
            wire_color="Blue",
            max_current_a=2.0,
            class_rating="B",
            eol_type=EOLType.CAPACITOR,
            eol_value="22uF"
        )
        
        assert circuit.circuit_id == "NAC_002"
        assert circuit.circuit_name == "Main Floor Notification"
        assert circuit.circuit_type == CircuitType.NAC
        assert circuit.panel_id == "PANEL1"
        assert circuit.device_count == 12
        assert circuit.total_length_ft == 385.5
        assert circuit.wire_gauge == "12"
        assert circuit.wire_color == "Blue"
        assert circuit.max_current_a == 2.0
        assert circuit.class_rating == "B"
        assert circuit.eol_type == EOLType.CAPACITOR
        assert circuit.eol_value == "22uF"


@pytest.fixture
def mock_app():
    """Create a mock QApplication for testing."""
    if not QApplication.instance():
        app = QApplication([])
        yield app
        app.quit()
    else:
        yield QApplication.instance()


class TestCircuitTableModel:
    """Test circuit table model functionality."""
    
    def test_table_model_initialization(self, mock_app):
        """Test table model initialization."""
        model = CircuitTableModel()
        
        assert model.rowCount() == 0
        assert model.columnCount() == len(model.COLUMN_HEADERS)
        assert len(model.circuits) == 0
        assert len(model.live_calculations) == 0
    
    def test_add_circuit(self, mock_app):
        """Test adding circuits to the model."""
        model = CircuitTableModel()
        
        circuit1 = CircuitProperties(circuit_id="SLC_001", circuit_name="Test Circuit 1")
        circuit2 = CircuitProperties(circuit_id="NAC_001", circuit_name="Test Circuit 2")
        
        model.add_circuit(circuit1)
        assert model.rowCount() == 1
        assert model.get_circuit(0) == circuit1
        
        model.add_circuit(circuit2)
        assert model.rowCount() == 2
        assert model.get_circuit(1) == circuit2
    
    def test_remove_circuit(self, mock_app):
        """Test removing circuits from the model."""
        model = CircuitTableModel()
        
        circuit1 = CircuitProperties(circuit_id="SLC_001")
        circuit2 = CircuitProperties(circuit_id="NAC_001")
        
        model.add_circuit(circuit1)
        model.add_circuit(circuit2)
        assert model.rowCount() == 2
        
        model.remove_circuit(0)
        assert model.rowCount() == 1
        assert model.get_circuit(0) == circuit2
        
        model.remove_circuit(0)
        assert model.rowCount() == 0
    
    def test_update_circuit(self, mock_app):
        """Test updating circuits in the model."""
        model = CircuitTableModel()
        
        circuit = CircuitProperties(circuit_id="SLC_001", circuit_name="Original")
        model.add_circuit(circuit)
        
        updated_circuit = CircuitProperties(circuit_id="SLC_001", circuit_name="Updated")
        model.update_circuit(0, updated_circuit)
        
        assert model.get_circuit(0).circuit_name == "Updated"
    
    def test_table_data_display(self, mock_app):
        """Test table data display values."""
        model = CircuitTableModel()
        
        circuit = CircuitProperties(
            circuit_id="SLC_001",
            circuit_name="Test Circuit",
            circuit_type=CircuitType.SLC,
            panel_id="PANEL1",
            device_count=5,
            total_length_ft=125.5,
            current_draw_a=0.150,
            voltage_drop_percent=2.3
        )
        model.add_circuit(circuit)
        
        # Test display data for different columns
        index = model.index(0, model.COL_NAME)
        assert model.data(index, Qt.ItemDataRole.DisplayRole) == "Test Circuit"
        
        index = model.index(0, model.COL_TYPE)
        assert model.data(index, Qt.ItemDataRole.DisplayRole) == "SLC"
        
        index = model.index(0, model.COL_PANEL)
        assert model.data(index, Qt.ItemDataRole.DisplayRole) == "PANEL1"
        
        index = model.index(0, model.COL_DEVICES)
        assert model.data(index, Qt.ItemDataRole.DisplayRole) == "5"
        
        index = model.index(0, model.COL_LENGTH)
        assert model.data(index, Qt.ItemDataRole.DisplayRole) == "126"
        
        index = model.index(0, model.COL_CURRENT)
        assert model.data(index, Qt.ItemDataRole.DisplayRole) == "0.150"
        
        index = model.index(0, model.COL_VOLTAGE_DROP)
        assert model.data(index, Qt.ItemDataRole.DisplayRole) == "2.3%"
    
    def test_compliance_status_display(self, mock_app):
        """Test compliance status display and coloring."""
        model = CircuitTableModel()
        
        # Test PASS status
        circuit_pass = CircuitProperties(
            circuit_id="SLC_001",
            nfpa_compliant=True,
            ada_compliant=True, 
            local_code_compliant=True
        )
        model.add_circuit(circuit_pass)
        
        index = model.index(0, model.COL_COMPLIANCE)
        assert "PASS" in model.data(index, Qt.ItemDataRole.DisplayRole)
        
        # Test FAIL status
        circuit_fail = CircuitProperties(
            circuit_id="SLC_002",
            nfpa_compliant=False,
            ada_compliant=True,
            local_code_compliant=True
        )
        model.add_circuit(circuit_fail)
        
        index = model.index(1, model.COL_COMPLIANCE)
        assert "FAIL" in model.data(index, Qt.ItemDataRole.DisplayRole)
        
        # Test REVIEW status
        circuit_review = CircuitProperties(
            circuit_id="SLC_003", 
            nfpa_compliant=True,
            ada_compliant=False,
            local_code_compliant=True
        )
        model.add_circuit(circuit_review)
        
        index = model.index(2, model.COL_COMPLIANCE)
        assert "REVIEW" in model.data(index, Qt.ItemDataRole.DisplayRole)


class TestCircuitPropertiesPanel:
    """Test circuit properties editing panel."""
    
    def test_properties_panel_initialization(self, mock_app):
        """Test properties panel initialization."""
        panel = CircuitPropertiesPanel()
        
        assert panel.current_circuit is None
        assert hasattr(panel, 'tab_widget')
        assert hasattr(panel, 'name_edit')
        assert hasattr(panel, 'type_combo')
        assert hasattr(panel, 'apply_button')
        assert hasattr(panel, 'revert_button')
    
    def test_load_circuit_into_panel(self, mock_app):
        """Test loading circuit properties into the panel."""
        panel = CircuitPropertiesPanel()
        
        circuit = CircuitProperties(
            circuit_id="SLC_001",
            circuit_name="Test Circuit",
            circuit_type=CircuitType.NAC,
            panel_id="PANEL1",
            wire_gauge="12",
            wire_color="Blue",
            max_current_a=2.5,
            eol_value="22K",
            start_address=10,
            end_address=25
        )
        
        panel.load_circuit(circuit)
        
        assert panel.current_circuit == circuit
        assert panel.name_edit.text() == "Test Circuit"
        assert panel.type_combo.currentText() == "NAC"
        assert panel.panel_edit.text() == "PANEL1"
        assert panel.wire_gauge_combo.currentText() == "12"
        assert panel.wire_color_combo.currentText() == "Blue"
        assert panel.max_current_spin.value() == 2.5
        assert panel.eol_value_edit.text() == "22K"
        assert panel.start_address_spin.value() == 10
        assert panel.end_address_spin.value() == 25


class TestProjectCircuitsEditor:
    """Test main project circuits editor widget."""
    
    def test_editor_initialization(self, mock_app):
        """Test editor initialization."""
        editor = ProjectCircuitsEditor()
        
        assert editor.calc_engine is None
        assert hasattr(editor, 'table_model')
        assert hasattr(editor, 'table_view')
        assert hasattr(editor, 'properties_panel')
        assert hasattr(editor, 'new_circuit_button')
        assert hasattr(editor, 'duplicate_button')
        assert hasattr(editor, 'delete_button')
        assert hasattr(editor, 'refresh_button')
        assert hasattr(editor, 'export_button')
    
    def test_create_new_circuit(self, mock_app):
        """Test creating a new circuit."""
        editor = ProjectCircuitsEditor()
        initial_count = editor.table_model.rowCount()
        
        editor.create_new_circuit()
        
        assert editor.table_model.rowCount() == initial_count + 1
        circuit = editor.table_model.get_circuit(initial_count)
        assert circuit is not None
        assert circuit.circuit_id.startswith("CIRCUIT_")
        assert "New Circuit" in circuit.circuit_name
    
    def test_duplicate_circuit(self, mock_app):
        """Test duplicating a circuit."""
        editor = ProjectCircuitsEditor()
        
        # Add a circuit first
        original = CircuitProperties(
            circuit_id="SLC_001",
            circuit_name="Original Circuit",
            wire_gauge="12",
            panel_id="PANEL1"
        )
        editor.table_model.add_circuit(original)
        
        # Select the circuit and duplicate
        editor.table_view.selectRow(0)
        initial_count = editor.table_model.rowCount()
        
        editor.duplicate_selected_circuit()
        
        assert editor.table_model.rowCount() == initial_count + 1
        duplicate = editor.table_model.get_circuit(1)
        assert duplicate is not None
        assert "Copy" in duplicate.circuit_name
        assert duplicate.wire_gauge == original.wire_gauge
        assert duplicate.panel_id == original.panel_id
        assert duplicate.circuit_id != original.circuit_id
    
    def test_filter_circuits(self, mock_app):
        """Test circuit filtering functionality."""
        editor = ProjectCircuitsEditor()
        
        # Add test circuits
        circuits = [
            CircuitProperties(circuit_id="SLC_001", circuit_name="Detection Zone 1"),
            CircuitProperties(circuit_id="NAC_001", circuit_name="Notification Zone 1"),
            CircuitProperties(circuit_id="SLC_002", circuit_name="Detection Zone 2"),
        ]
        
        for circuit in circuits:
            editor.table_model.add_circuit(circuit)
        
        # Test filtering
        editor.filter_circuits("Detection")
        
        # Should show SLC circuits but hide NAC
        assert not editor.table_view.isRowHidden(0)  # SLC_001 
        assert editor.table_view.isRowHidden(1)      # NAC_001 (hidden)
        assert not editor.table_view.isRowHidden(2)  # SLC_002
        
        # Clear filter
        editor.filter_circuits("")
        
        # All should be visible
        for row in range(3):
            assert not editor.table_view.isRowHidden(row)
    
    @patch('frontend.panels.project_circuits_editor.LiveCalculationsEngine')
    def test_live_calculations_integration(self, mock_engine_class, mock_app):
        """Test integration with live calculations engine."""
        editor = ProjectCircuitsEditor()
        
        # Create mock engine
        mock_engine = Mock()
        mock_calculations = {
            "SLC_001": Mock(
                device_count=5,
                total_length_ft=150.0,
                current_draw_a=0.125,
                total_voltage_drop=0.5,
                voltage_drop_percent=2.1,
                compliance_status="PASS"
            )
        }
        mock_engine.get_all_circuit_analyses.return_value = mock_calculations
        
        # Set engine and add circuit
        editor.set_live_calculations_engine(mock_engine)
        circuit = CircuitProperties(circuit_id="SLC_001")
        editor.table_model.add_circuit(circuit)
        
        # Refresh calculations
        editor.refresh_calculations()
        
        # Verify integration
        mock_engine.get_all_circuit_analyses.assert_called_once()
        updated_circuit = editor.table_model.get_circuit(0)
        assert updated_circuit.device_count == 5
        assert updated_circuit.total_length_ft == 150.0
        assert updated_circuit.current_draw_a == 0.125
    
    def test_factory_function(self, mock_app):
        """Test factory function for creating editor."""
        editor = create_project_circuits_editor()
        
        assert isinstance(editor, ProjectCircuitsEditor)
        assert editor.table_model.rowCount() > 0  # Should have sample circuits
        
        # Verify sample circuits are loaded
        circuit = editor.table_model.get_circuit(0)
        assert circuit is not None
        assert circuit.circuit_id != ""
        assert circuit.circuit_name != ""


class TestCircuitEnums:
    """Test circuit enumeration types."""
    
    def test_circuit_type_enum(self):
        """Test CircuitType enumeration."""
        assert CircuitType.SLC.value == "SLC"
        assert CircuitType.NAC.value == "NAC"
        assert CircuitType.POWER.value == "Power"
        assert CircuitType.CONTROL.value == "Control"
        assert CircuitType.TELEPHONE.value == "Telephone"
    
    def test_eol_type_enum(self):
        """Test EOLType enumeration."""
        assert EOLType.RESISTOR.value == "Resistor"
        assert EOLType.CAPACITOR.value == "Capacitor"
        assert EOLType.DIODE.value == "Diode"
        assert EOLType.NONE.value == "None"


class TestProjectCircuitsEditorIntegration:
    """Integration tests for the complete Project Circuits Editor."""
    
    def test_complete_workflow(self, mock_app):
        """Test complete circuit management workflow."""
        editor = ProjectCircuitsEditor()
        
        # 1. Create new circuit
        editor.create_new_circuit()
        assert editor.table_model.rowCount() >= 1
        
        # 2. Select and edit circuit
        editor.table_view.selectRow(0)
        circuit = editor.table_model.get_circuit(0)
        
        # Simulate editing in properties panel
        editor.properties_panel.load_circuit(circuit)
        editor.properties_panel.name_edit.setText("Edited Circuit")
        editor.properties_panel.apply_changes()
        
        # 3. Verify changes applied
        updated_circuit = editor.table_model.get_circuit(0)
        assert updated_circuit.circuit_name == "Edited Circuit"
        
        # 4. Duplicate circuit
        editor.duplicate_selected_circuit()
        assert editor.table_model.rowCount() >= 2
        
        # 5. Test filtering
        editor.filter_circuits("Edited")
        # First circuit should be visible, sample circuits might be hidden
        
        # 6. Test deletion
        initial_count = editor.table_model.rowCount()
        editor.table_view.selectRow(0)
        with patch('PySide6.QtWidgets.QMessageBox.question', return_value=0x00004000):  # Yes
            editor.delete_selected_circuit()
        assert editor.table_model.rowCount() == initial_count - 1
    
    def test_master_spec_compliance(self, mock_app):
        """Test compliance with Master Specification Section 6 requirements."""
        editor = ProjectCircuitsEditor()
        
        # Test Section 6 requirements:
        
        # 1. Circuit table with panel, loop, device count, voltage drop, AH load
        table_headers = editor.table_model.COLUMN_HEADERS
        assert "Panel" in table_headers
        assert "Devices" in table_headers  
        assert "Voltage Drop" in table_headers
        assert "Current" in table_headers  # AH load equivalent
        
        # 2. Circuit naming and properties editor
        assert hasattr(editor.properties_panel, 'name_edit')
        assert hasattr(editor.properties_panel, 'tab_widget')  # Multiple property categories
        
        # 3. Batch circuit operations
        assert hasattr(editor, 'new_circuit_button')
        assert hasattr(editor, 'duplicate_button')
        assert hasattr(editor, 'delete_button')
        
        # 4. Integration with live calculations engine
        assert hasattr(editor, 'calc_engine')
        assert hasattr(editor, 'refresh_calculations')
        assert hasattr(editor, 'set_live_calculations_engine')
        
        logger.info("✅ Project Circuits Editor meets Master Specification Section 6 requirements")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])