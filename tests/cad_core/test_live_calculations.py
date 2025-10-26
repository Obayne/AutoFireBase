"""
Test Live Calculations Engine
Per Master Specification Section 7: Calculations (Live)

Tests the live calculation engine for voltage drop, battery sizing,
and real-time updates as circuit design changes.
"""

import pytest

from cad_core.calculations.live_engine import (
    BatteryCalculation,
    CircuitAnalysis,
    LiveCalculationsEngine,
    WireSegment,
)


class TestLiveCalculationsEngine:
    """Test the core live calculations engine functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.engine = LiveCalculationsEngine()
    
    def test_wire_segment_resistance_calculation(self):
        """Test that wire segments calculate resistance correctly."""
        segment = WireSegment(
            from_device="PANEL1",
            to_device="SMOKE_001",
            length_ft=100.0,
            wire_gauge="14",
            current_a=0.020,
            circuit_type="SLC"
        )
        
        # 14 AWG = 3.19 ohm/1000ft, so 100ft = 0.319 ohm
        expected_resistance = (3.19 / 1000.0) * 100.0
        assert abs(segment.resistance_ohm - expected_resistance) < 0.001
    
    def test_add_wire_segment(self):
        """Test adding wire segments to the engine."""
        segment = WireSegment(
            from_device="PANEL1",
            to_device="SMOKE_001",
            length_ft=50.0,
            wire_gauge="14",
            current_a=0.020,
            circuit_type="SLC"
        )
        
        self.engine.add_wire_segment(segment)
        
        # Check that circuit was created
        circuit_id = "SLC_PANEL1"
        assert circuit_id in self.engine.circuits
        assert len(self.engine.circuits[circuit_id]) == 1
        assert self.engine.circuits[circuit_id][0] == segment
    
    def test_circuit_voltage_drop_calculation(self):
        """Test voltage drop calculation for a complete circuit."""
        # Add multiple segments to create a circuit
        segments = [
            WireSegment("PANEL1", "SMOKE_001", 50.0, "14", 0.020, "SLC"),
            WireSegment("SMOKE_001", "SMOKE_002", 30.0, "14", 0.020, "SLC"),
            WireSegment("SMOKE_002", "SMOKE_003", 40.0, "14", 0.020, "SLC"),
        ]
        
        for segment in segments:
            self.engine.add_wire_segment(segment)
        
        # Calculate circuit analysis
        circuit_id = "SLC_PANEL1"
        analysis = self.engine.calculate_circuit_voltage_drop(circuit_id)
        
        assert isinstance(analysis, CircuitAnalysis)
        assert analysis.circuit_id == circuit_id
        assert analysis.circuit_type == "SLC"
        assert analysis.device_count == 3  # 3 smoke detectors
        assert analysis.total_length_ft == 120.0  # 50 + 30 + 40
        assert analysis.total_voltage_drop > 0
        assert analysis.compliance_status in ["PASS", "WARN", "FAIL"]
    
    def test_voltage_drop_compliance_checking(self):
        """Test that voltage drop compliance is properly checked."""
        # Create a circuit that exceeds voltage drop limits
        long_segment = WireSegment(
            from_device="PANEL1",
            to_device="SMOKE_001",
            length_ft=5000.0,  # Very long run
            wire_gauge="18",   # Small wire
            current_a=0.100,   # High current
            circuit_type="SLC"
        )
        
        self.engine.add_wire_segment(long_segment)
        
        circuit_id = "SLC_PANEL1"
        analysis = self.engine.calculate_circuit_voltage_drop(circuit_id)
        
        # Should fail compliance due to excessive voltage drop
        assert analysis.voltage_drop_percent > self.engine.max_voltage_drop_percent
        assert analysis.compliance_status == "FAIL"
        assert len(analysis.warnings) > 0
        assert "exceeds" in analysis.warnings[0].lower()
    
    def test_slc_device_count_limit_checking(self):
        """Test SLC device count limit compliance."""
        # Add many devices to exceed SLC limit
        self.engine.max_slc_devices = 5  # Set low limit for testing
        
        for i in range(6):  # Exceed limit
            segment = WireSegment(
                from_device=f"SPLICE_{i}",
                to_device=f"SMOKE_{i:03d}",
                length_ft=10.0,
                wire_gauge="14",
                current_a=0.020,
                circuit_type="SLC"
            )
            self.engine.add_wire_segment(segment)
        
        circuit_id = "SLC_CIRCUIT1"  # Updated to match new circuit naming
        analysis = self.engine.calculate_circuit_voltage_drop(circuit_id)
        
        # Should warn about device count
        assert analysis.device_count > self.engine.max_slc_devices
        assert any("device count" in warning.lower() for warning in analysis.warnings)
    
    def test_battery_calculation(self):
        """Test battery sizing calculation."""
        # Add some device loads
        self.engine.update_device_load("SMOKE_001", 0.020)  # 20mA
        self.engine.update_device_load("SMOKE_002", 0.020)  # 20mA
        self.engine.update_device_load("PULL_001", 0.001)   # 1mA
        
        # Add circuits connected to panel
        segments = [
            WireSegment("PANEL1", "SMOKE_001", 50.0, "14", 0.020, "SLC"),
            WireSegment("PANEL1", "SMOKE_002", 50.0, "14", 0.020, "SLC"),
            WireSegment("PANEL1", "PULL_001", 25.0, "14", 0.001, "SLC"),
        ]
        
        for segment in segments:
            self.engine.add_wire_segment(segment)
        
        # Calculate battery requirements
        battery_calc = self.engine.calculate_battery_requirements("PANEL1")
        
        assert isinstance(battery_calc, BatteryCalculation)
        assert battery_calc.standby_current_a > 0
        assert battery_calc.alarm_current_a > 0
        assert battery_calc.required_standby_ah > 0
        assert battery_calc.required_alarm_ah > 0
        assert battery_calc.recommended_ah > 0
        assert battery_calc.battery_sku is not None
        assert "AH" in battery_calc.battery_sku
    
    def test_device_load_update(self):
        """Test updating device current loads."""
        device_id = "SMOKE_001"
        initial_current = 0.020
        updated_current = 0.035
        
        # Set initial load
        self.engine.update_device_load(device_id, initial_current)
        assert self.engine.device_loads[device_id] == initial_current
        
        # Update load
        self.engine.update_device_load(device_id, updated_current)
        assert self.engine.device_loads[device_id] == updated_current
    
    def test_wire_segment_removal(self):
        """Test removing wire segments from calculations."""
        segment = WireSegment(
            from_device="PANEL1",
            to_device="SMOKE_001",
            length_ft=50.0,
            wire_gauge="14",
            current_a=0.020,
            circuit_type="SLC"
        )
        
        # Add then remove segment
        self.engine.add_wire_segment(segment)
        circuit_id = "SLC_PANEL1"
        assert len(self.engine.circuits[circuit_id]) == 1
        
        self.engine.remove_wire_segment(segment)
        assert len(self.engine.circuits[circuit_id]) == 0
    
    def test_multiple_circuit_types(self):
        """Test handling multiple circuit types (SLC, NAC, POWER)."""
        segments = [
            WireSegment("PANEL1", "SMOKE_001", 50.0, "14", 0.020, "SLC"),
            WireSegment("PANEL1", "HORN_001", 75.0, "12", 0.150, "NAC"),
            WireSegment("PANEL1", "RELAY_001", 25.0, "14", 0.050, "POWER"),
        ]
        
        for segment in segments:
            self.engine.add_wire_segment(segment)
        
        # Should create separate circuits for each type
        expected_circuits = ["SLC_PANEL1", "NAC_PANEL1", "POWER_PANEL1"]
        for circuit_id in expected_circuits:
            assert circuit_id in self.engine.circuits
            analysis = self.engine.calculate_circuit_voltage_drop(circuit_id)
            assert analysis.circuit_type in ["SLC", "NAC", "POWER"]
    
    def test_get_all_circuit_analyses(self):
        """Test getting analyses for all circuits."""
        # Add segments for multiple circuits
        segments = [
            WireSegment("PANEL1", "SMOKE_001", 50.0, "14", 0.020, "SLC"),
            WireSegment("PANEL2", "SMOKE_002", 60.0, "14", 0.020, "SLC"),
            WireSegment("PANEL1", "HORN_001", 40.0, "12", 0.150, "NAC"),
        ]
        
        for segment in segments:
            self.engine.add_wire_segment(segment)
        
        # Get all analyses
        all_analyses = self.engine.get_all_circuit_analyses()
        
        assert isinstance(all_analyses, dict)
        assert len(all_analyses) == 3  # SLC_PANEL1, SLC_PANEL2, NAC_PANEL1
        
        for circuit_id, analysis in all_analyses.items():
            assert isinstance(analysis, CircuitAnalysis)
            assert analysis.circuit_id == circuit_id
    
    def test_empty_circuit_analysis(self):
        """Test analysis of empty circuits."""
        circuit_id = "SLC_EMPTY"
        analysis = self.engine.calculate_circuit_voltage_drop(circuit_id)
        
        assert analysis.circuit_id == circuit_id
        assert analysis.circuit_type == "UNKNOWN"
        assert analysis.total_voltage_drop == 0.0
        assert analysis.device_count == 0
        assert analysis.total_length_ft == 0.0
        assert analysis.compliance_status == "UNKNOWN"
        assert "Circuit not found" in analysis.warnings


class TestWireSegment:
    """Test the WireSegment data class."""
    
    def test_wire_segment_creation(self):
        """Test creating a wire segment."""
        segment = WireSegment(
            from_device="PANEL1",
            to_device="SMOKE_001",
            length_ft=100.0,
            wire_gauge="14",
            current_a=0.020,
            circuit_type="SLC"
        )
        
        assert segment.from_device == "PANEL1"
        assert segment.to_device == "SMOKE_001"
        assert segment.length_ft == 100.0
        assert segment.wire_gauge == "14"
        assert segment.current_a == 0.020
        assert segment.circuit_type == "SLC"
    
    def test_wire_resistance_different_gauges(self):
        """Test wire resistance for different AWG sizes."""
        gauges_and_resistance = [
            ("12", 2.01 / 1000.0 * 100),  # 12 AWG
            ("14", 3.19 / 1000.0 * 100),  # 14 AWG
            ("16", 5.08 / 1000.0 * 100),  # 16 AWG
            ("18", 8.08 / 1000.0 * 100),  # 18 AWG
        ]
        
        for gauge, expected_resistance in gauges_and_resistance:
            segment = WireSegment(
                from_device="A",
                to_device="B",
                length_ft=100.0,
                wire_gauge=gauge,
                current_a=0.020,
                circuit_type="SLC"
            )
            
            assert abs(segment.resistance_ohm - expected_resistance) < 0.001


class TestCircuitAnalysis:
    """Test the CircuitAnalysis data class."""
    
    def test_voltage_drop_percentage_calculation(self):
        """Test voltage drop percentage calculation."""
        analysis = CircuitAnalysis(
            circuit_id="TEST_CIRCUIT",
            circuit_type="SLC",
            total_voltage_drop=2.4,  # 2.4V drop
            max_voltage_drop=10.0,
            device_count=5,
            total_length_ft=250.0,
            current_draw_a=0.100,
            compliance_status="PASS",
            warnings=[]
        )
        
        # 2.4V / 24V = 10%
        expected_percentage = (2.4 / 24.0) * 100.0
        assert abs(analysis.voltage_drop_percent - expected_percentage) < 0.1


class TestBatteryCalculation:
    """Test the BatteryCalculation data class."""
    
    def test_total_required_ah_calculation(self):
        """Test that total required AH is the larger of standby vs alarm."""
        battery_calc = BatteryCalculation(
            standby_current_a=0.500,
            alarm_current_a=0.750,
            required_standby_ah=12.0,
            required_alarm_ah=4.0,  # Alarm is shorter duration
            recommended_ah=18.0
        )
        
        # Should return the larger requirement (standby in this case)
        assert battery_calc.total_required_ah == 12.0
        
        # Test opposite case
        battery_calc.required_standby_ah = 3.0
        battery_calc.required_alarm_ah = 5.0
        assert battery_calc.total_required_ah == 5.0


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])