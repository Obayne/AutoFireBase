"""
Automated circuit calculations for fire alarm systems.
Handles battery calculations, current calculations, voltage drop analysis,
and NFPA 72 compliance checking.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import math
import sqlite3
import json


class BatteryType(Enum):
    """Fire alarm battery types."""
    SEALED_LEAD_ACID = "Sealed Lead Acid"
    NICKEL_CADMIUM = "Nickel Cadmium"  
    LITHIUM = "Lithium"


class WireType(Enum):
    """Fire alarm wire types."""
    FPLR = "FPLR"  # Fire Power Limited Riser
    FPLP = "FPLP"  # Fire Power Limited Plenum
    FPL = "FPL"    # Fire Power Limited


@dataclass
class WireProperties:
    """Wire electrical properties for calculations."""
    gauge: str
    resistance_ohms_per_1000ft: float
    ampacity: float
    type: WireType = WireType.FPLR
    
    
# Standard fire alarm wire properties
WIRE_PROPERTIES = {
    "18 AWG": WireProperties("18 AWG", 6.385, 7.0),
    "16 AWG": WireProperties("16 AWG", 4.016, 10.0),
    "14 AWG": WireProperties("14 AWG", 2.525, 15.0),
    "12 AWG": WireProperties("12 AWG", 1.588, 20.0),
}


@dataclass
class CircuitLoad:
    """Represents electrical load on a circuit."""
    device_count: int = 0
    standby_current_a: float = 0.0
    alarm_current_a: float = 0.0
    wire_length_ft: float = 0.0
    voltage_drop_v: float = 0.0
    voltage_drop_percent: float = 0.0


@dataclass 
class BatteryCalculation:
    """Battery sizing calculation results."""
    standby_hours: float = 24.0  # NFPA 72 requirement
    alarm_minutes: float = 5.0   # NFPA 72 requirement (5 min or 15 min)
    standby_ah_required: float = 0.0
    alarm_ah_required: float = 0.0
    total_ah_required: float = 0.0
    safety_factor: float = 1.25  # 25% safety factor
    final_ah_required: float = 0.0
    recommended_battery_ah: float = 0.0
    battery_count: int = 1


@dataclass
class CircuitCompliance:
    """NFPA 72 compliance check results."""
    voltage_drop_compliant: bool = True
    current_compliant: bool = True
    wire_gauge_adequate: bool = True
    supervision_compliant: bool = True
    issues: List[str] | None = None
    warnings: List[str] | None = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.warnings is None:
            self.warnings = []


class CircuitCalculator:
    """Performs fire alarm circuit calculations per NFPA 72."""
    
    def __init__(self):
        self.nominal_voltage = 24.0  # VDC for most fire alarm systems
        self.max_voltage_drop_percent = 5.0  # NFPA 72 limit
        self.slc_current_limit = 3.0  # Amps for most SLC circuits
        
    def calculate_circuit_load(self, devices: List[Dict[str, Any]], 
                             wire_length_ft: float = 0.0,
                             wire_gauge: str = "18 AWG") -> CircuitLoad:
        """Calculate total circuit load from device list."""
        load = CircuitLoad()
        
        # Sum device currents
        for device in devices:
            load.device_count += 1
            load.standby_current_a += device.get('current_standby_ma', 0.0) / 1000.0
            load.alarm_current_a += device.get('current_alarm_ma', 0.0) / 1000.0
            
        load.wire_length_ft = wire_length_ft
        
        # Calculate voltage drop
        if wire_gauge in WIRE_PROPERTIES:
            wire_props = WIRE_PROPERTIES[wire_gauge]
            # Voltage drop = 2 * I * R * L / 1000 (factor of 2 for round trip)
            load.voltage_drop_v = (2 * load.alarm_current_a * 
                                 wire_props.resistance_ohms_per_1000ft * 
                                 wire_length_ft / 1000.0)
            load.voltage_drop_percent = (load.voltage_drop_v / self.nominal_voltage) * 100.0
            
        return load
        
    def calculate_battery_requirements(self, panels: List[Dict[str, Any]], 
                                     circuits: List[CircuitLoad],
                                     standby_hours: float = 24.0,
                                     alarm_minutes: float = 5.0) -> BatteryCalculation:
        """Calculate battery requirements per NFPA 72."""
        calc = BatteryCalculation()
        calc.standby_hours = standby_hours
        calc.alarm_minutes = alarm_minutes
        
        # Calculate panel standby current
        panel_standby_current = 0.0
        panel_alarm_current = 0.0
        
        for panel in panels:
            panel_standby_current += panel.get('standby_current', 0.0)
            panel_alarm_current += panel.get('alarm_current', 0.0)
            
        # Calculate circuit currents
        circuit_standby_current = sum(c.standby_current_a for c in circuits)
        circuit_alarm_current = sum(c.alarm_current_a for c in circuits)
        
        # Total system currents
        total_standby = panel_standby_current + circuit_standby_current
        total_alarm = panel_alarm_current + circuit_alarm_current
        
        # Calculate amp-hour requirements
        calc.standby_ah_required = total_standby * calc.standby_hours
        calc.alarm_ah_required = total_alarm * (calc.alarm_minutes / 60.0)
        calc.total_ah_required = calc.standby_ah_required + calc.alarm_ah_required
        
        # Apply safety factor
        calc.final_ah_required = calc.total_ah_required * calc.safety_factor
        
        # Recommend standard battery size
        calc.recommended_battery_ah = self._recommend_battery_size(calc.final_ah_required)
        calc.battery_count = self._calculate_battery_count(calc.recommended_battery_ah, self.nominal_voltage)
        
        return calc
        
    def check_nfpa_compliance(self, circuit_load: CircuitLoad, 
                            circuit_type: str = "SLC") -> CircuitCompliance:
        """Check circuit compliance with NFPA 72 requirements."""
        compliance = CircuitCompliance()
        if compliance.issues is None:
            compliance.issues = []
        if compliance.warnings is None:
            compliance.warnings = []
        
        # Check voltage drop
        if circuit_load.voltage_drop_percent > self.max_voltage_drop_percent:
            compliance.voltage_drop_compliant = False
            compliance.issues.append(
                f"Voltage drop ({circuit_load.voltage_drop_percent:.1f}%) exceeds "
                f"NFPA 72 limit of {self.max_voltage_drop_percent}%"
            )
            
        # Check current limits
        if circuit_type == "SLC" and circuit_load.alarm_current_a > self.slc_current_limit:
            compliance.current_compliant = False
            compliance.issues.append(
                f"SLC current ({circuit_load.alarm_current_a:.3f}A) exceeds "
                f"limit of {self.slc_current_limit}A"
            )
            
        # Check wire gauge adequacy
        max_current = max(circuit_load.standby_current_a, circuit_load.alarm_current_a)
        adequate_gauge = self._check_wire_adequacy(max_current, circuit_load.wire_length_ft)
        if not adequate_gauge:
            compliance.wire_gauge_adequate = False
            compliance.issues.append("Wire gauge may be inadequate for circuit load and length")
            
        # Warnings for high utilization
        if circuit_load.voltage_drop_percent > 3.0:
            compliance.warnings.append(
                f"Voltage drop ({circuit_load.voltage_drop_percent:.1f}%) is approaching limit"
            )
            
        return compliance
        
    def calculate_voltage_drop_by_distance(self, current_a: float, wire_gauge: str,
                                         distances_ft: List[float]) -> List[Tuple[float, float]]:
        """Calculate voltage drop at various distances."""
        if wire_gauge not in WIRE_PROPERTIES:
            return []
            
        wire_props = WIRE_PROPERTIES[wire_gauge]
        results = []
        
        for distance in distances_ft:
            voltage_drop = (2 * current_a * wire_props.resistance_ohms_per_1000ft * 
                          distance / 1000.0)
            voltage_drop_percent = (voltage_drop / self.nominal_voltage) * 100.0
            results.append((distance, voltage_drop_percent))
            
        return results
        
    def optimize_wire_gauge(self, current_a: float, distance_ft: float,
                          max_voltage_drop_percent: float | None = None) -> str:
        """Recommend optimal wire gauge for given current and distance."""
        if max_voltage_drop_percent is None:
            max_voltage_drop_percent = self.max_voltage_drop_percent
            
        # Try gauges from smallest to largest
        gauges = ["18 AWG", "16 AWG", "14 AWG", "12 AWG"]
        
        for gauge in gauges:
            if gauge in WIRE_PROPERTIES:
                wire_props = WIRE_PROPERTIES[gauge]
                voltage_drop = (2 * current_a * wire_props.resistance_ohms_per_1000ft * 
                              distance_ft / 1000.0)
                voltage_drop_percent = (voltage_drop / self.nominal_voltage) * 100.0
                
                if voltage_drop_percent <= max_voltage_drop_percent:
                    return gauge
                    
        return "12 AWG"  # Largest available if nothing else works
        
    def calculate_power_consumption(self, circuits: List[CircuitLoad]) -> Dict[str, float]:
        """Calculate total system power consumption."""
        total_standby_current = sum(c.standby_current_a for c in circuits)
        total_alarm_current = sum(c.alarm_current_a for c in circuits)
        
        return {
            'standby_power_w': total_standby_current * self.nominal_voltage,
            'alarm_power_w': total_alarm_current * self.nominal_voltage,
            'standby_current_a': total_standby_current,
            'alarm_current_a': total_alarm_current
        }
        
    def _recommend_battery_size(self, required_ah: float) -> float:
        """Recommend standard battery size."""
        standard_sizes = [7.0, 12.0, 18.0, 26.0, 33.0, 55.0, 75.0, 100.0]
        
        for size in standard_sizes:
            if size >= required_ah:
                return size
                
        # If larger than standard sizes, round up to nearest 25 AH
        return math.ceil(required_ah / 25.0) * 25.0
        
    def _calculate_battery_count(self, battery_ah: float, system_voltage: float) -> int:
        """Calculate number of batteries needed."""
        # Most fire alarm systems use 12V batteries in series for 24V
        if system_voltage <= 12.0:
            return 1
        elif system_voltage <= 24.0:
            return 2
        else:
            return math.ceil(system_voltage / 12.0)
            
    def _check_wire_adequacy(self, current_a: float, length_ft: float) -> bool:
        """Check if standard 18 AWG wire is adequate."""
        if "18 AWG" not in WIRE_PROPERTIES:
            return False
            
        wire_props = WIRE_PROPERTIES["18 AWG"]
        
        # Check ampacity
        if current_a > wire_props.ampacity:
            return False
            
        # Check voltage drop
        voltage_drop = (2 * current_a * wire_props.resistance_ohms_per_1000ft * 
                       length_ft / 1000.0)
        voltage_drop_percent = (voltage_drop / self.nominal_voltage) * 100.0
        
        return voltage_drop_percent <= self.max_voltage_drop_percent


class CircuitCalculationManager:
    """Manages circuit calculations for fire alarm projects."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.con = db_connection
        self.calculator = CircuitCalculator()
        
    def calculate_project_circuits(self, project_id: str) -> Dict[str, Any]:
        """Calculate all circuits for a project."""
        cur = self.con.cursor()
        
        # Get all SLC circuits for project
        cur.execute("""
            SELECT sc.*, COUNT(da.id) as device_count
            FROM slc_circuits sc
            LEFT JOIN device_addresses da ON sc.id = da.slc_circuit_id
            WHERE sc.panel_device_id IN (
                SELECT device_id FROM project_panels WHERE project_id = ?
            )
            GROUP BY sc.id
        """, (project_id,))
        
        circuits = cur.fetchall()
        circuit_loads = []
        
        for circuit in circuits:
            # Get devices on this circuit
            devices = self._get_circuit_devices(circuit['id'])
            
            # Calculate circuit load
            load = self.calculator.calculate_circuit_load(
                devices, 
                circuit.get('wire_length_feet', 0.0),
                circuit.get('wire_gauge', '18 AWG')
            )
            circuit_loads.append(load)
            
            # Update database with calculations
            self._update_circuit_calculations(circuit['id'], load)
            
        # Get panels for battery calculation
        panels = self._get_project_panels(project_id)
        
        # Calculate battery requirements
        battery_calc = self.calculator.calculate_battery_requirements(panels, circuit_loads)
        
        # Calculate total power consumption
        power_calc = self.calculator.calculate_power_consumption(circuit_loads)
        
        return {
            'circuit_loads': circuit_loads,
            'battery_calculation': battery_calc,
            'power_consumption': power_calc,
            'total_circuits': len(circuits),
            'total_devices': sum(len(self._get_circuit_devices(c['id'])) for c in circuits)
        }
        
    def _get_circuit_devices(self, circuit_id: int) -> List[Dict[str, Any]]:
        """Get devices on a circuit with their electrical specs."""
        cur = self.con.cursor()
        
        cur.execute("""
            SELECT fas.current_standby_ma, fas.current_alarm_ma, fas.voltage_nominal,
                   d.model, d.name, dt.code as device_type
            FROM device_addresses da
            JOIN devices d ON da.project_device_id = d.id
            JOIN device_types dt ON d.type_id = dt.id
            LEFT JOIN fire_alarm_specs fas ON d.id = fas.device_id
            WHERE da.slc_circuit_id = ?
        """, (circuit_id,))
        
        return [dict(row) for row in cur.fetchall()]
        
    def _get_project_panels(self, project_id: str) -> List[Dict[str, Any]]:
        """Get fire alarm panels for a project."""
        cur = self.con.cursor()
        
        cur.execute("""
            SELECT d.model, d.name, d.properties_json
            FROM project_panels pp
            JOIN devices d ON pp.device_id = d.id
            WHERE pp.project_id = ?
        """, (project_id,))
        
        panels = []
        for row in cur.fetchall():
            properties = json.loads(row['properties_json']) if row['properties_json'] else {}
            panel_data = {
                'model': row['model'],
                'name': row['name'],
                'standby_current': properties.get('standby_current', 0.0),
                'alarm_current': properties.get('alarm_current', 0.0)
            }
            panels.append(panel_data)
            
        return panels
        
    def _update_circuit_calculations(self, circuit_id: int, load: CircuitLoad):
        """Update circuit calculations in database."""
        cur = self.con.cursor()
        
        cur.execute("""
            UPDATE circuit_calculations 
            SET total_standby_current = ?, total_alarm_current = ?,
                voltage_drop_percent = ?, calculated_at = CURRENT_TIMESTAMP
            WHERE slc_circuit_id = ?
        """, (load.standby_current_a, load.alarm_current_a, 
              load.voltage_drop_percent, circuit_id))
        
        self.con.commit()
        
    def generate_calculation_report(self, project_id: str) -> str:
        """Generate detailed calculation report."""
        calculations = self.calculate_project_circuits(project_id)
        
        report = "FIRE ALARM SYSTEM CALCULATIONS\n"
        report += "=" * 50 + "\n\n"
        
        # Circuit summary
        report += f"Total Circuits: {calculations['total_circuits']}\n"
        report += f"Total Devices: {calculations['total_devices']}\n\n"
        
        # Power consumption
        power = calculations['power_consumption']
        report += "POWER CONSUMPTION:\n"
        report += f"Standby: {power['standby_current_a']:.3f}A ({power['standby_power_w']:.1f}W)\n"
        report += f"Alarm: {power['alarm_current_a']:.3f}A ({power['alarm_power_w']:.1f}W)\n\n"
        
        # Battery calculation
        battery = calculations['battery_calculation']
        report += "BATTERY CALCULATION:\n"
        report += f"Standby requirement: {battery.standby_ah_required:.1f} AH\n"
        report += f"Alarm requirement: {battery.alarm_ah_required:.1f} AH\n"
        report += f"Total with safety factor: {battery.final_ah_required:.1f} AH\n"
        report += f"Recommended battery: {battery.recommended_battery_ah:.0f} AH\n"
        report += f"Battery count: {battery.battery_count}\n\n"
        
        # Circuit details
        report += "CIRCUIT DETAILS:\n"
        for i, load in enumerate(calculations['circuit_loads'], 1):
            report += f"Circuit {i}:\n"
            report += f"  Devices: {load.device_count}\n"
            report += f"  Standby: {load.standby_current_a:.3f}A\n"
            report += f"  Alarm: {load.alarm_current_a:.3f}A\n"
            report += f"  Voltage drop: {load.voltage_drop_percent:.1f}%\n\n"
            
        return report