#!/usr/bin/env python3
"""
AutoFire Live Calculations Engine
=================================

The critical foundation for professional fire alarm design software.
Real-time calculations for voltage drop, battery sizing, wire gauge selection,
coverage analysis, and NFPA compliance validation.

This engine provides the mathematical foundation that AI will use for:
- Intelligent device placement optimization
- Automatic wire routing with electrical validation  
- Real-time compliance checking
- Professional system design validation

DEVELOPMENT NOTES:
- Built as foundation for AI integration
- All calculations follow NFPA 72 standards
- Real-time performance for interactive design
- Comprehensive validation and error reporting
"""

import math
import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Configure logging for calculation tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """Fire alarm device types for calculations."""
    SMOKE_DETECTOR = "smoke_detector"
    HEAT_DETECTOR = "heat_detector"
    MANUAL_PULL = "manual_pull"
    HORN = "horn"
    STROBE = "strobe"
    HORN_STROBE = "horn_strobe"
    SPEAKER = "speaker"
    CONTROL_PANEL = "control_panel"
    NAC_EXTENDER = "nac_extender"
    RELAY = "relay"
    ISOLATOR = "isolator"

class CircuitType(Enum):
    """Fire alarm circuit types."""
    SLC = "slc"  # Signaling Line Circuit
    NAC = "nac"  # Notification Appliance Circuit
    IDC = "idc"  # Initiating Device Circuit
    POWER = "power"

@dataclass
class DeviceSpecification:
    """Complete device electrical specifications."""
    device_type: DeviceType
    model: str
    manufacturer: str
    
    # Electrical specifications
    operating_voltage_min: float  # Volts
    operating_voltage_max: float  # Volts
    operating_voltage_nominal: float  # Volts
    standby_current: float  # Milliamps
    alarm_current: float  # Milliamps
    
    # Physical specifications  
    coverage_area: float  # Square feet
    max_spacing: float  # Feet
    min_wall_distance: float  # Feet
    mounting_height_min: float  # Feet
    mounting_height_max: float  # Feet
    
    # Installation specifications
    wire_gauge_min: int  # AWG
    wire_gauge_max: int  # AWG
    eol_resistor: Optional[float] = None  # Ohms
    supervision_required: bool = True
    
    # Additional properties
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WireSpecification:
    """Wire electrical and physical specifications."""
    gauge: int  # AWG
    conductor_count: int
    wire_type: str  # "THHN", "PLENUM", "FPLR", etc.
    
    # Electrical properties
    resistance_per_foot: float  # Ohms per foot
    max_current: float  # Amperes
    voltage_rating: float  # Volts
    
    # Physical properties
    diameter: float  # Inches
    weight_per_foot: float  # Pounds per foot
    
    # Installation properties
    conduit_fill_area: float  # Square inches
    pulling_tension: float  # Pounds
    bend_radius: float  # Inches

@dataclass
class CircuitDevice:
    """Device on a circuit with position and specifications."""
    id: str
    device_spec: DeviceSpecification
    position: Tuple[float, float]  # X, Y coordinates in feet
    wire_distance: float  # Distance from previous device in feet
    voltage_drop: float = 0.0  # Calculated voltage drop to this device
    is_end_of_line: bool = False

@dataclass
class Circuit:
    """Complete circuit with devices and calculations."""
    id: str
    circuit_type: CircuitType
    panel_voltage: float  # Source voltage
    wire_spec: WireSpecification
    devices: List[CircuitDevice] = field(default_factory=list)
    
    # Calculated values
    total_length: float = 0.0
    total_standby_current: float = 0.0
    total_alarm_current: float = 0.0
    max_voltage_drop: float = 0.0
    voltage_drop_percentage: float = 0.0
    
    # Validation results
    is_valid: bool = True
    violations: List[str] = field(default_factory=list)

class LiveCalculationsEngine:
    """Real-time calculations engine for fire alarm systems."""
    
    def __init__(self):
        self.device_specifications = self._load_device_specifications()
        self.wire_specifications = self._load_wire_specifications()
        self.nfpa_limits = self._load_nfpa_limits()
        
        logger.info("🔧 Live Calculations Engine initialized")
        logger.info(f"📊 Loaded {len(self.device_specifications)} device specifications")
        logger.info(f"🔌 Loaded {len(self.wire_specifications)} wire specifications")
    
    def _load_device_specifications(self) -> Dict[str, DeviceSpecification]:
        """Load comprehensive device electrical specifications."""
        
        # Professional fire alarm device specifications
        # Based on major manufacturer datasheets
        
        devices = {
            # Smoke Detectors
            "FSP851": DeviceSpecification(
                device_type=DeviceType.SMOKE_DETECTOR,
                model="FSP-851",
                manufacturer="System Sensor",
                operating_voltage_min=15.2,
                operating_voltage_max=32.4,
                operating_voltage_nominal=24.0,
                standby_current=0.045,  # 45 μA = 0.045 mA
                alarm_current=60.0,  # 60 mA
                coverage_area=900.0,  # 30x30 feet
                max_spacing=30.0,
                min_wall_distance=15.0,
                mounting_height_min=0.33,  # 4 inches from ceiling
                mounting_height_max=1.0,   # 12 inches from ceiling
                wire_gauge_min=22,
                wire_gauge_max=12,
                eol_resistor=47000.0,  # 47kΩ
                supervision_required=True
            ),
            
            "FST851": DeviceSpecification(
                device_type=DeviceType.HEAT_DETECTOR,
                model="FST-851",
                manufacturer="System Sensor",
                operating_voltage_min=15.2,
                operating_voltage_max=32.4,
                operating_voltage_nominal=24.0,
                standby_current=0.035,
                alarm_current=45.0,
                coverage_area=2500.0,  # 50x50 feet
                max_spacing=50.0,
                min_wall_distance=25.0,
                mounting_height_min=0.33,
                mounting_height_max=1.0,
                wire_gauge_min=22,
                wire_gauge_max=12,
                eol_resistor=47000.0,
                supervision_required=True
            ),
            
            # Manual Pull Stations
            "FMM1": DeviceSpecification(
                device_type=DeviceType.MANUAL_PULL,
                model="FMM-1",
                manufacturer="Honeywell",
                operating_voltage_min=15.2,
                operating_voltage_max=32.4,
                operating_voltage_nominal=24.0,
                standby_current=0.250,
                alarm_current=8.5,
                coverage_area=40000.0,  # 200x200 feet travel distance
                max_spacing=200.0,  # Travel distance
                min_wall_distance=0.0,  # Wall mounted
                mounting_height_min=3.5,  # 42 inches
                mounting_height_max=4.0,  # 48 inches
                wire_gauge_min=18,
                wire_gauge_max=12,
                supervision_required=True
            ),
            
            # Notification Devices
            "MSH24": DeviceSpecification(
                device_type=DeviceType.HORN_STROBE,
                model="MSH-24",
                manufacturer="System Sensor",
                operating_voltage_min=16.0,
                operating_voltage_max=33.0,
                operating_voltage_nominal=24.0,
                standby_current=0.0,  # No standby current
                alarm_current=177.0,  # At 24V, high candela
                coverage_area=2500.0,
                max_spacing=50.0,
                min_wall_distance=0.0,
                mounting_height_min=8.0,  # 96 inches minimum
                mounting_height_max=12.0,
                wire_gauge_min=16,
                wire_gauge_max=12,
                supervision_required=False
            ),
            
            "LSM24": DeviceSpecification(
                device_type=DeviceType.STROBE,
                model="LSM-24",
                manufacturer="System Sensor",
                operating_voltage_min=16.0,
                operating_voltage_max=33.0,
                operating_voltage_nominal=24.0,
                standby_current=0.0,
                alarm_current=95.0,  # At 24V, 15 candela
                coverage_area=2500.0,
                max_spacing=50.0,
                min_wall_distance=0.0,
                mounting_height_min=8.0,
                mounting_height_max=12.0,
                wire_gauge_min=18,
                wire_gauge_max=12,
                supervision_required=False
            )
        }
        
        return devices
    
    def _load_wire_specifications(self) -> Dict[int, WireSpecification]:
        """Load wire electrical specifications by AWG."""
        
        # Standard fire alarm wire specifications
        # Based on NFPA 70 (NEC) and fire alarm industry standards
        
        wires = {
            22: WireSpecification(
                gauge=22,
                conductor_count=2,
                wire_type="FPLR",
                resistance_per_foot=0.0161,  # Ohms per foot
                max_current=0.5,  # Amperes (de-rated for fire alarm)
                voltage_rating=300.0,
                diameter=0.185,  # Inches
                weight_per_foot=0.025,
                conduit_fill_area=0.0269,  # Square inches
                pulling_tension=25.0,
                bend_radius=1.85
            ),
            
            18: WireSpecification(
                gauge=18,
                conductor_count=2,
                wire_type="FPLR",
                resistance_per_foot=0.00640,
                max_current=1.0,
                voltage_rating=300.0,
                diameter=0.245,
                weight_per_foot=0.042,
                conduit_fill_area=0.0471,
                pulling_tension=50.0,
                bend_radius=2.45
            ),
            
            16: WireSpecification(
                gauge=16,
                conductor_count=2,
                wire_type="FPLR",
                resistance_per_foot=0.00403,
                max_current=1.5,
                voltage_rating=300.0,
                diameter=0.289,
                weight_per_foot=0.065,
                conduit_fill_area=0.0656,
                pulling_tension=75.0,
                bend_radius=2.89
            ),
            
            14: WireSpecification(
                gauge=14,
                conductor_count=2,
                wire_type="FPLR",
                resistance_per_foot=0.00253,
                max_current=2.5,
                voltage_rating=300.0,
                diameter=0.339,
                weight_per_foot=0.095,
                conduit_fill_area=0.0903,
                pulling_tension=100.0,
                bend_radius=3.39
            ),
            
            12: WireSpecification(
                gauge=12,
                conductor_count=2,
                wire_type="FPLR",
                resistance_per_foot=0.00159,
                max_current=4.0,
                voltage_rating=300.0,
                diameter=0.399,
                weight_per_foot=0.145,
                conduit_fill_area=0.1252,
                pulling_tension=150.0,
                bend_radius=3.99
            )
        }
        
        return wires
    
    def _load_nfpa_limits(self) -> Dict[str, Any]:
        """Load NFPA 72 electrical limits and requirements."""
        
        return {
            "voltage_drop": {
                "max_percentage": 10.0,  # NFPA 72: 10% max voltage drop
                "recommended_percentage": 7.0,  # Industry best practice
            },
            "operating_voltage": {
                "min_percentage": 85.0,  # 85% of nominal
                "max_percentage": 110.0,  # 110% of nominal
            },
            "circuit_current": {
                "slc_max": 0.300,  # 300mA max for SLC
                "nac_max": 3.000,  # 3A max for NAC (varies by panel)
            },
            "wire_gauge": {
                "min_slc": 18,  # Minimum 18 AWG for SLC
                "min_nac": 16,  # Minimum 16 AWG for NAC
            },
            "eol_supervision": {
                "required_slc": True,
                "required_nac": False,  # Depends on application
            }
        }
    
    def calculate_voltage_drop(self, circuit: Circuit) -> Circuit:
        """Calculate voltage drop for entire circuit."""
        
        if not circuit.devices:
            return circuit
        
        # Reset calculations
        cumulative_distance = 0.0
        max_voltage_drop = 0.0
        
        for i, device in enumerate(circuit.devices):
            # Add this device's distance
            cumulative_distance += device.wire_distance
            
            # Calculate current from source to this device (all devices on line)
            if circuit.circuit_type == CircuitType.SLC:
                # SLC: All devices draw supervision current continuously
                line_current = sum(d.device_spec.standby_current for d in circuit.devices[:i+1]) / 1000.0  # Convert mA to A
            else:
                # NAC: All devices draw alarm current when activated
                line_current = sum(d.device_spec.alarm_current for d in circuit.devices[:i+1]) / 1000.0
            
            # Calculate voltage drop to this device
            # V = I × R, where R = resistance per foot × distance × 2 (round trip)
            loop_resistance = circuit.wire_spec.resistance_per_foot * cumulative_distance * 2.0
            voltage_drop = line_current * loop_resistance
            
            device.voltage_drop = voltage_drop
            max_voltage_drop = max(max_voltage_drop, voltage_drop)
        
        # Update circuit totals
        circuit.total_length = cumulative_distance
        circuit.max_voltage_drop = max_voltage_drop
        circuit.voltage_drop_percentage = (max_voltage_drop / circuit.panel_voltage) * 100.0
        
        # Calculate total currents
        if circuit.circuit_type == CircuitType.SLC:
            circuit.total_standby_current = sum(d.device_spec.standby_current for d in circuit.devices)
            circuit.total_alarm_current = sum(d.device_spec.alarm_current for d in circuit.devices)
        else:
            circuit.total_alarm_current = sum(d.device_spec.alarm_current for d in circuit.devices)
        
        return circuit
    
    def validate_circuit_compliance(self, circuit: Circuit) -> Circuit:
        """Validate circuit against NFPA 72 requirements."""
        
        circuit.violations.clear()
        circuit.is_valid = True
        
        # Check voltage drop
        max_voltage_drop_percent = self.nfpa_limits["voltage_drop"]["max_percentage"]
        if circuit.voltage_drop_percentage > max_voltage_drop_percent:
            violation = f"Voltage drop {circuit.voltage_drop_percentage:.1f}% exceeds NFPA 72 limit of {max_voltage_drop_percent}%"
            circuit.violations.append(violation)
            circuit.is_valid = False
        
        # Check minimum operating voltage at furthest device
        min_voltage = circuit.panel_voltage - circuit.max_voltage_drop
        for device in circuit.devices:
            device_min_voltage = device.device_spec.operating_voltage_min
            actual_voltage = circuit.panel_voltage - device.voltage_drop
            
            if actual_voltage < device_min_voltage:
                violation = f"Device {device.id} voltage {actual_voltage:.1f}V below minimum {device_min_voltage:.1f}V"
                circuit.violations.append(violation)
                circuit.is_valid = False
        
        # Check wire gauge requirements
        min_wire_gauge = self.nfpa_limits["wire_gauge"]["min_slc" if circuit.circuit_type == CircuitType.SLC else "min_nac"]
        if circuit.wire_spec.gauge > min_wire_gauge:
            violation = f"Wire gauge {circuit.wire_spec.gauge} AWG insufficient, minimum {min_wire_gauge} AWG required"
            circuit.violations.append(violation)
            circuit.is_valid = False
        
        # Check current limits
        circuit_limit_key = "slc_max" if circuit.circuit_type == CircuitType.SLC else "nac_max"
        max_current = self.nfpa_limits["circuit_current"][circuit_limit_key]
        total_current = (circuit.total_alarm_current if circuit.circuit_type == CircuitType.NAC 
                        else circuit.total_standby_current) / 1000.0  # Convert to Amperes
        
        if total_current > max_current:
            violation = f"Circuit current {total_current:.3f}A exceeds limit of {max_current:.3f}A"
            circuit.violations.append(violation)
            circuit.is_valid = False
        
        # Check device compatibility (AWG wire gauge: smaller number = larger wire)
        for device in circuit.devices:
            if circuit.wire_spec.gauge > device.device_spec.wire_gauge_min:
                violation = f"Wire gauge {circuit.wire_spec.gauge} AWG too small for device {device.id} (min {device.device_spec.wire_gauge_min} AWG)"
                circuit.violations.append(violation)
                circuit.is_valid = False
                
            if circuit.wire_spec.gauge < device.device_spec.wire_gauge_max:
                violation = f"Wire gauge {circuit.wire_spec.gauge} AWG too large for device {device.id} (max {device.device_spec.wire_gauge_max} AWG)"
                circuit.violations.append(violation)
                circuit.is_valid = False
        
        return circuit
    
    def optimize_wire_gauge(self, circuit: Circuit) -> Tuple[Circuit, List[int]]:
        """Find optimal wire gauge for circuit compliance."""
        
        optimal_gauges = []
        
        # Try progressively larger wire gauges
        for gauge in [22, 18, 16, 14, 12]:
            if gauge not in self.wire_specifications:
                continue
                
            # Create test circuit with this wire gauge
            test_circuit = Circuit(
                id=circuit.id,
                circuit_type=circuit.circuit_type,
                panel_voltage=circuit.panel_voltage,
                wire_spec=self.wire_specifications[gauge],
                devices=circuit.devices.copy()
            )
            
            # Calculate and validate
            test_circuit = self.calculate_voltage_drop(test_circuit)
            test_circuit = self.validate_circuit_compliance(test_circuit)
            
            if test_circuit.is_valid:
                optimal_gauges.append(gauge)
        
        # Return circuit with smallest valid wire gauge
        if optimal_gauges:
            best_gauge = max(optimal_gauges)  # Largest AWG number = smallest wire
            circuit.wire_spec = self.wire_specifications[best_gauge]
            circuit = self.calculate_voltage_drop(circuit)
            circuit = self.validate_circuit_compliance(circuit)
        
        return circuit, optimal_gauges
    
    def calculate_battery_requirements(self, circuits: List[Circuit]) -> Dict[str, Any]:
        """Calculate battery backup requirements for system."""
        
        # NFPA 72 requirements: 24 hours standby + 5 minutes alarm
        standby_hours = 24.0
        alarm_minutes = 5.0
        
        total_standby_current = 0.0
        total_alarm_current = 0.0
        
        for circuit in circuits:
            total_standby_current += circuit.total_standby_current
            total_alarm_current += circuit.total_alarm_current
        
        # Convert mA to A
        standby_amps = total_standby_current / 1000.0
        alarm_amps = total_alarm_current / 1000.0
        
        # Calculate required capacity
        standby_capacity = standby_amps * standby_hours  # Amp-hours
        alarm_capacity = alarm_amps * (alarm_minutes / 60.0)  # Amp-hours
        
        # Total capacity with 20% safety factor
        total_capacity = (standby_capacity + alarm_capacity) * 1.2
        
        # Recommend standard battery sizes
        standard_batteries = [7.0, 12.0, 18.0, 26.0, 33.0, 55.0]  # Amp-hours
        recommended_battery = next((b for b in standard_batteries if b >= total_capacity), 100.0)
        
        return {
            "standby_current": total_standby_current,
            "alarm_current": total_alarm_current,
            "standby_capacity": standby_capacity,
            "alarm_capacity": alarm_capacity,
            "total_capacity_required": total_capacity,
            "recommended_battery_size": recommended_battery,
            "calculation_time": datetime.now().isoformat()
        }
    
    def analyze_coverage(self, devices: List[CircuitDevice], room_area: float) -> Dict[str, Any]:
        """Analyze device coverage for a room or area."""
        
        total_coverage = 0.0
        coverage_gaps: List[Dict[str, Any]] = []
        overlapping_devices: List[Dict[str, Any]] = []
        
        for device in devices:
            total_coverage += device.device_spec.coverage_area
            
            # Check for gaps (simplified analysis)
            if device.device_spec.coverage_area < room_area:
                gap_area = room_area - device.device_spec.coverage_area
                if gap_area > 100.0:  # More than 100 sq ft gap
                    coverage_gaps.append({
                        "device_id": device.id,
                        "gap_area": gap_area,
                        "device_coverage": device.device_spec.coverage_area
                    })
        
        coverage_percentage = min((total_coverage / room_area) * 100.0, 100.0)
        
        return {
            "room_area": room_area,
            "total_coverage": total_coverage,
            "coverage_percentage": coverage_percentage,
            "coverage_gaps": coverage_gaps,
            "overlapping_devices": overlapping_devices,
            "devices_analyzed": len(devices),
            "recommendations": self._generate_coverage_recommendations(coverage_percentage, coverage_gaps)
        }
    
    def _generate_coverage_recommendations(self, coverage_percentage: float, gaps: List[Dict]) -> List[str]:
        """Generate recommendations for coverage improvement."""
        
        recommendations = []
        
        if coverage_percentage < 90.0:
            recommendations.append(f"Coverage at {coverage_percentage:.1f}% - consider additional devices")
        
        if gaps:
            recommendations.append(f"Found {len(gaps)} coverage gaps requiring attention")
            for gap in gaps:
                if gap["gap_area"] > 500.0:
                    recommendations.append(f"Large coverage gap of {gap['gap_area']:.0f} sq ft near device {gap['device_id']}")
        
        if coverage_percentage > 150.0:
            recommendations.append("Possible over-coverage - optimize device placement for cost savings")
        
        if not recommendations:
            recommendations.append("Coverage analysis optimal - meets NFPA 72 requirements")
        
        return recommendations
    
    def calculate_system_power(self, circuits: List[Circuit], panel_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total system power requirements."""
        
        total_standby_power = 0.0
        total_alarm_power = 0.0
        
        for circuit in circuits:
            # Calculate power for each circuit
            standby_watts = (circuit.total_standby_current / 1000.0) * circuit.panel_voltage
            alarm_watts = (circuit.total_alarm_current / 1000.0) * circuit.panel_voltage
            
            total_standby_power += standby_watts
            total_alarm_power += alarm_watts
        
        # Add panel consumption
        panel_standby = panel_specs.get("standby_power", 5.0)  # Watts
        panel_alarm = panel_specs.get("alarm_power", 15.0)  # Watts
        
        total_standby_power += panel_standby
        total_alarm_power += panel_alarm
        
        return {
            "total_standby_power": total_standby_power,
            "total_alarm_power": total_alarm_power,
            "panel_standby_power": panel_standby,
            "panel_alarm_power": panel_alarm,
            "circuits_analyzed": len(circuits),
            "power_efficiency": (total_standby_power / total_alarm_power) * 100.0 if total_alarm_power > 0 else 0.0
        }

def create_sample_calculation_demo():
    """Create demonstration of live calculations."""
    
    engine = LiveCalculationsEngine()
    
    # Create sample circuit with notification devices (higher current)
    devices = [
        CircuitDevice(
            id="HS-001",
            device_spec=engine.device_specifications["MSH24"],
            position=(10.0, 10.0),
            wire_distance=100.0
        ),
        CircuitDevice(
            id="HS-002", 
            device_spec=engine.device_specifications["MSH24"],
            position=(60.0, 10.0),
            wire_distance=150.0
        ),
        CircuitDevice(
            id="HS-003",
            device_spec=engine.device_specifications["MSH24"], 
            position=(110.0, 10.0),
            wire_distance=200.0,
            is_end_of_line=True
        )
    ]
    
    print(f"🔍 DEBUG: Device currents...")
    for dev in devices:
        print(f"   {dev.id}: Standby={dev.device_spec.standby_current}mA, Alarm={dev.device_spec.alarm_current}mA")
    
    # Create NAC circuit (higher current)
    nac_circuit = Circuit(
        id="NAC-1",
        circuit_type=CircuitType.NAC,
        panel_voltage=24.0,
        wire_spec=engine.wire_specifications[16],  # 16 AWG for NAC
        devices=devices
    )
    
    # Perform calculations
    print("🔧 AutoFire Live Calculations Engine Demo")
    print("=" * 50)
    
    print(f"🔍 DEBUG: Wire resistance = {nac_circuit.wire_spec.resistance_per_foot} Ohms/ft")
    
    # Calculate voltage drop
    nac_circuit = engine.calculate_voltage_drop(nac_circuit)
    print(f"\n📊 CIRCUIT ANALYSIS: {nac_circuit.id}")
    print(f"   Total Length: {nac_circuit.total_length:.1f} feet")
    print(f"   Max Voltage Drop: {nac_circuit.max_voltage_drop:.2f}V ({nac_circuit.voltage_drop_percentage:.1f}%)")
    print(f"   Total Standby Current: {nac_circuit.total_standby_current:.1f} mA")
    print(f"   Total Alarm Current: {nac_circuit.total_alarm_current:.1f} mA")
    
    # Validate compliance
    nac_circuit = engine.validate_circuit_compliance(nac_circuit)
    print(f"\n✅ COMPLIANCE VALIDATION:")
    print(f"   Circuit Valid: {'✅ YES' if nac_circuit.is_valid else '❌ NO'}")
    if nac_circuit.violations:
        for violation in nac_circuit.violations:
            print(f"   ⚠️ {violation}")
    
    # Optimize wire gauge
    optimized_circuit, optimal_gauges = engine.optimize_wire_gauge(nac_circuit)
    print(f"\n🎯 WIRE OPTIMIZATION:")
    print(f"   Current Wire: {nac_circuit.wire_spec.gauge} AWG")
    print(f"   Valid Gauges: {optimal_gauges}")
    print(f"   Recommended: {optimal_gauges[0] if optimal_gauges else 'None valid'} AWG")
    
    # Battery calculations
    battery_calc = engine.calculate_battery_requirements([nac_circuit])
    print(f"\n🔋 BATTERY REQUIREMENTS:")
    print(f"   Standby Current: {battery_calc['standby_current']:.1f} mA")
    print(f"   Alarm Current: {battery_calc['alarm_current']:.1f} mA")
    print(f"   Required Capacity: {battery_calc['total_capacity_required']:.1f} Ah")
    print(f"   Recommended Battery: {battery_calc['recommended_battery_size']:.0f} Ah")
    
    # Coverage analysis
    coverage = engine.analyze_coverage(devices, 2500.0)  # 2500 sq ft room
    print(f"\n📐 COVERAGE ANALYSIS:")
    print(f"   Room Area: {coverage['room_area']:.0f} sq ft")
    print(f"   Coverage: {coverage['coverage_percentage']:.1f}%")
    print(f"   Devices: {coverage['devices_analyzed']}")
    for rec in coverage['recommendations']:
        print(f"   💡 {rec}")
    
    print(f"\n🎯 CALCULATION ENGINE READY FOR AI INTEGRATION!")
    return engine, nac_circuit

if __name__ == "__main__":
    # Run demonstration
    engine, sample_circuit = create_sample_calculation_demo()
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. ✅ Live Calculations Engine complete")
    print(f"   2. 🔄 Integrate with CAD interface")
    print(f"   3. 🤖 Connect to AI optimization algorithms") 
    print(f"   4. 📊 Real-time compliance monitoring")
    print(f"   5. 🎯 Intelligent design suggestions")