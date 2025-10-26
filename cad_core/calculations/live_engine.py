"""
Live Calculations Engine for AutoFire
Per Master Specification Section 7: Calculations (Live)

This module integrates all fire alarm calculations and provides real-time
updates as the design changes. Implements voltage drop, battery sizing,
SLC loop analysis, and conduit fill calculations.
"""

import logging
from dataclasses import dataclass

from cad_core.calculations.battery_sizing import required_ah
from cad_core.calculations.voltage_drop import total_voltage_drop

logger = logging.getLogger(__name__)


@dataclass
class WireSegment:
    """Represents a wire segment for calculations."""
    
    from_device: str
    to_device: str
    length_ft: float
    wire_gauge: str
    current_a: float
    circuit_type: str  # NAC, SLC, POWER
    
    @property
    def resistance_ohm(self) -> float:
        """Get wire resistance per foot based on gauge."""
        # Standard AWG resistance values per 1000ft at 75°C
        awg_resistance = {
            "12": 2.01,   # 12 AWG
            "14": 3.19,   # 14 AWG  
            "16": 5.08,   # 16 AWG
            "18": 8.08,   # 18 AWG
            "20": 12.8,   # 20 AWG
        }
        base_resistance = awg_resistance.get(self.wire_gauge, 3.19) / 1000.0
        return base_resistance * self.length_ft


@dataclass
class CircuitAnalysis:
    """Complete analysis of a fire alarm circuit."""
    
    circuit_id: str
    circuit_type: str
    total_voltage_drop: float
    max_voltage_drop: float
    device_count: int
    total_length_ft: float
    current_draw_a: float
    compliance_status: str  # PASS, WARN, FAIL
    warnings: list[str]
    
    @property
    def voltage_drop_percent(self) -> float:
        """Calculate voltage drop as percentage of supply voltage."""
        # Assume 24V nominal for fire alarm systems
        nominal_voltage = 24.0
        return (self.total_voltage_drop / nominal_voltage) * 100.0


@dataclass 
class BatteryCalculation:
    """Battery sizing calculation results."""
    
    standby_current_a: float
    alarm_current_a: float
    required_standby_ah: float
    required_alarm_ah: float
    recommended_ah: float
    battery_sku: str | None = None
    derating_factor: float = 0.8
    
    @property
    def total_required_ah(self) -> float:
        """Total AH requirement (larger of standby vs alarm)."""
        return max(self.required_standby_ah, self.required_alarm_ah)


class LiveCalculationsEngine:
    """
    Real-time calculations engine for fire alarm design.
    
    Monitors circuit changes and automatically updates:
    - Voltage drop calculations per segment
    - Battery sizing with proper derating
    - SLC loop length and device count limits
    - Conduit fill analysis
    - NFPA compliance checking
    """
    
    def __init__(self):
        self.circuits: dict[str, list[WireSegment]] = {}
        self.device_loads: dict[str, float] = {}  # device_id -> current_draw
        self.panel_loads: dict[str, float] = {}   # panel_id -> total_load
        self.device_connections: dict[str, set[str]] = {}  # Track device connectivity
        
        # NFPA 72 compliance limits
        self.max_voltage_drop_percent = 10.0  # 10% max per NFPA 72
        self.max_slc_devices = 252  # Typical SLC limit
        self.max_slc_length_ft = 10000  # Typical SLC wire length limit
        
        logger.info("Live Calculations Engine initialized")
    
    def add_wire_segment(self, segment: WireSegment) -> None:
        """Add a wire segment to the calculation model."""
        # Find which circuit this segment belongs to by following connections
        circuit_id = self._find_circuit_for_segment(segment)
        
        if circuit_id not in self.circuits:
            self.circuits[circuit_id] = []
            
        self.circuits[circuit_id].append(segment)
        
        # Update device connectivity graph
        self._update_device_connections(segment)
        
        logger.debug("Added wire segment to %s: %.1fft", circuit_id, segment.length_ft)
        
        # Trigger recalculation
        self._recalculate_circuit(circuit_id)
    
    def _find_circuit_for_segment(self, segment: WireSegment) -> str:
        """Find which circuit a segment belongs to based on device connectivity."""
        # If either device is a panel, use that panel ID
        if "PANEL" in segment.from_device.upper():
            panel_id = (
                segment.from_device.split('_')[0] 
                if '_' in segment.from_device 
                else segment.from_device
            )
            return f"{segment.circuit_type}_{panel_id}"
        
        if "PANEL" in segment.to_device.upper():
            panel_id = (
                segment.to_device.split('_')[0] 
                if '_' in segment.to_device 
                else segment.to_device
            )
            return f"{segment.circuit_type}_{panel_id}"
        
        # Check if either device is already connected to a circuit
        for circuit_id, existing_segments in self.circuits.items():
            if circuit_id.startswith(segment.circuit_type):
                for existing_segment in existing_segments:
                    from_connected = segment.from_device in [
                        existing_segment.from_device, 
                        existing_segment.to_device
                    ]
                    to_connected = segment.to_device in [
                        existing_segment.from_device, 
                        existing_segment.to_device
                    ]
                    if from_connected or to_connected:
                        return circuit_id
        
        # No existing circuit found, create new one
        # Use the circuit type and first device as identifier
        return f"{segment.circuit_type}_CIRCUIT1"
    
    def _update_device_connections(self, segment: WireSegment) -> None:
        """Update the device connectivity graph."""
        from_device = segment.from_device
        to_device = segment.to_device
        
        if from_device not in self.device_connections:
            self.device_connections[from_device] = set()
        if to_device not in self.device_connections:
            self.device_connections[to_device] = set()
        
        self.device_connections[from_device].add(to_device)
        self.device_connections[to_device].add(from_device)
    
    def remove_wire_segment(self, segment: WireSegment) -> None:
        """Remove a wire segment from calculations."""
        # Find which circuit contains this segment
        circuit_id = None
        for cid, segments in self.circuits.items():
            if segment in segments:
                circuit_id = cid
                break
        
        if circuit_id and segment in self.circuits[circuit_id]:
            self.circuits[circuit_id].remove(segment)
            logger.debug("Removed wire segment from %s", circuit_id)
            self._recalculate_circuit(circuit_id)
    
    def update_device_load(self, device_id: str, current_a: float) -> None:
        """Update the current draw for a device."""
        self.device_loads[device_id] = current_a
        logger.debug("Updated device load: %s = %.3fA", device_id, current_a)
        
        # Recalculate affected circuits
        self._recalculate_all_circuits()
    
    def calculate_circuit_voltage_drop(self, circuit_id: str) -> CircuitAnalysis:
        """Calculate complete voltage drop analysis for a circuit."""
        if circuit_id not in self.circuits:
            return CircuitAnalysis(
                circuit_id=circuit_id,
                circuit_type="UNKNOWN",
                total_voltage_drop=0.0,
                max_voltage_drop=self.max_voltage_drop_percent,
                device_count=0,
                total_length_ft=0.0,
                current_draw_a=0.0,
                compliance_status="UNKNOWN",
                warnings=["Circuit not found"]
            )
        
        segments = self.circuits[circuit_id]
        if not segments:
            return CircuitAnalysis(
                circuit_id=circuit_id,
                circuit_type="EMPTY",
                total_voltage_drop=0.0,
                max_voltage_drop=self.max_voltage_drop_percent,
                device_count=0,
                total_length_ft=0.0,
                current_draw_a=0.0,
                compliance_status="PASS",
                warnings=[]
            )
        
        # Calculate total voltage drop
        voltage_segments = [(seg.current_a, seg.resistance_ohm) for seg in segments]
        total_vd = total_voltage_drop(voltage_segments)
        
        # Circuit statistics
        total_length = sum(seg.length_ft for seg in segments)
        total_current = sum(seg.current_a for seg in segments)
        device_count = len(set(seg.to_device for seg in segments))
        circuit_type = segments[0].circuit_type if segments else "UNKNOWN"
        
        # Voltage drop percentage
        vd_percent = (total_vd / 24.0) * 100.0  # Assuming 24V system
        
        # Compliance checking
        warnings = []
        if vd_percent > self.max_voltage_drop_percent:
            warnings.append(
                f"Voltage drop {vd_percent:.1f}% exceeds {self.max_voltage_drop_percent}% limit"
            )
        
        if circuit_type == "SLC":
            if device_count > self.max_slc_devices:
                warnings.append(
                    f"SLC device count {device_count} exceeds {self.max_slc_devices} limit"
                )
            if total_length > self.max_slc_length_ft:
                warnings.append(
                    f"SLC length {total_length:.0f}ft exceeds {self.max_slc_length_ft}ft limit"
                )
        
        # Determine compliance status
        if warnings:
            compliance_status = "FAIL" if vd_percent > self.max_voltage_drop_percent else "WARN"
        else:
            compliance_status = "PASS"
        
        return CircuitAnalysis(
            circuit_id=circuit_id,
            circuit_type=circuit_type,
            total_voltage_drop=total_vd,
            max_voltage_drop=self.max_voltage_drop_percent,
            device_count=device_count,
            total_length_ft=total_length,
            current_draw_a=total_current,
            compliance_status=compliance_status,
            warnings=warnings
        )
    
    def calculate_battery_requirements(self, panel_id: str) -> BatteryCalculation:
        """Calculate battery requirements for a panel."""
        # Get all device loads connected to this panel
        panel_circuits = [cid for cid in self.circuits.keys() if panel_id in cid]
        
        standby_loads = []
        alarm_loads = []
        
        for circuit_id in panel_circuits:
            segments = self.circuits[circuit_id]
            for segment in segments:
                device_id = segment.to_device
                current = self.device_loads.get(device_id, 0.020)  # Default 20mA
                
                # Fire alarm devices typically have different standby vs alarm currents
                if segment.circuit_type == "NAC":
                    # NAC devices only draw current during alarm
                    standby_loads.append(0.001)  # Minimal standby
                    alarm_loads.append(current)
                elif segment.circuit_type == "SLC":
                    # SLC devices have constant standby current
                    standby_loads.append(current)
                    alarm_loads.append(current * 1.2)  # Slight increase during alarm
                else:
                    # Power circuits 
                    standby_loads.append(current)
                    alarm_loads.append(current)
        
        # Add panel self-consumption
        panel_standby = 0.100  # 100mA typical panel standby
        panel_alarm = 0.150    # 150mA panel during alarm
        standby_loads.append(panel_standby)
        alarm_loads.append(panel_alarm)
        
        # Calculate required AH for 24 hour standby + 5 minute alarm
        standby_ah = required_ah(standby_loads, 24.0, derate=0.8)
        alarm_ah = required_ah(alarm_loads, 5.0/60.0, derate=0.8)  # 5 minutes in hours
        
        # Recommend next standard battery size
        total_required = max(standby_ah, alarm_ah)
        standard_sizes = [7, 12, 18, 26, 40, 55, 75, 100]
        recommended = next((size for size in standard_sizes if size >= total_required), 100)
        
        return BatteryCalculation(
            standby_current_a=sum(standby_loads),
            alarm_current_a=sum(alarm_loads),
            required_standby_ah=standby_ah,
            required_alarm_ah=alarm_ah,
            recommended_ah=recommended,
            battery_sku=f"12V-{recommended}AH",  # Standard nomenclature
            derating_factor=0.8
        )
    
    def get_all_circuit_analyses(self) -> dict[str, CircuitAnalysis]:
        """Get voltage drop analysis for all circuits."""
        analyses = {}
        for circuit_id in self.circuits.keys():
            analyses[circuit_id] = self.calculate_circuit_voltage_drop(circuit_id)
        return analyses
    
    def _recalculate_circuit(self, circuit_id: str) -> None:
        """Recalculate analysis for a specific circuit."""
        analysis = self.calculate_circuit_voltage_drop(circuit_id)
        logger.debug(
            "Circuit %s: %s (%.1f%% VD)",
            circuit_id,
            analysis.compliance_status,
            analysis.voltage_drop_percent,
        )
    
    def _recalculate_all_circuits(self) -> None:
        """Recalculate all circuit analyses."""
        for circuit_id in self.circuits.keys():
            self._recalculate_circuit(circuit_id)