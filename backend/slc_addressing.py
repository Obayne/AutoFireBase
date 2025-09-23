"""
SLC (Signaling Line Circuit) addressing and management system.
Handles automatic assignment of device addresses, circuit validation,
and connection tracking for fire alarm systems.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import sqlite3
import json


class CircuitType(Enum):
    """Fire alarm circuit types."""
    SLC = "SLC"           # Signaling Line Circuit (addressable devices)
    NAC = "NAC"           # Notification Appliance Circuit 
    IDC = "IDC"           # Initiating Device Circuit (conventional)


class SupervisionType(Enum):
    """Circuit supervision types per NFPA 72.""" 
    CLASS_A = "Class A"   # Two-wire path, more reliable
    CLASS_B = "Class B"   # Single-wire path, basic supervision


@dataclass
class DeviceAddress:
    """Represents an addressed device on an SLC circuit."""
    address: int
    device_id: int
    device_model: str
    device_type: str
    x_coord: float
    y_coord: float
    floor_level: str = "Ground"
    zone: str = ""
    connected: bool = False
    
    
@dataclass 
class SLCCircuit:
    """Represents an SLC loop/circuit with its devices."""
    circuit_id: int
    panel_device_id: int
    loop_number: int
    supervision_type: SupervisionType = SupervisionType.CLASS_A
    max_devices: int = 159
    wire_type: str = "FPLR"
    wire_gauge: str = "18 AWG"
    devices: List[DeviceAddress] | None = None
    
    def __post_init__(self):
        if self.devices is None:
            self.devices = []
    
    @property
    def available_addresses(self) -> List[int]:
        """Get list of available device addresses."""
        if self.devices is None:
            return list(range(1, self.max_devices + 1))
        used_addresses = {device.address for device in self.devices}
        return [addr for addr in range(1, self.max_devices + 1) if addr not in used_addresses]
    
    @property
    def device_count(self) -> int:
        """Get current device count on circuit."""
        return len(self.devices) if self.devices is not None else 0
    
    @property 
    def is_full(self) -> bool:
        """Check if circuit is at maximum capacity."""
        return self.device_count >= self.max_devices


class SLCAddressingSystem:
    """Manages SLC addressing and device connections."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.con = db_connection
        self.con.row_factory = sqlite3.Row
        
    def create_slc_circuit(self, panel_device_id: int, loop_number: int, 
                          supervision_type: SupervisionType = SupervisionType.CLASS_A,
                          max_devices: int = 159) -> int:
        """Create a new SLC circuit for a panel."""
        cur = self.con.cursor()
        
        cur.execute("""
            INSERT INTO slc_circuits (panel_device_id, loop_number, max_devices, supervision_type)
            VALUES (?, ?, ?, ?)
        """, (panel_device_id, loop_number, max_devices, supervision_type.value))
        
        circuit_id = cur.lastrowid
        assert circuit_id is not None
        
        # Initialize circuit calculations
        cur.execute("""
            INSERT INTO circuit_calculations (slc_circuit_id)
            VALUES (?)
        """, (circuit_id,))
        
        self.con.commit()
        return circuit_id
    
    def get_panel_circuits(self, panel_device_id: int) -> List[SLCCircuit]:
        """Get all SLC circuits for a panel."""
        cur = self.con.cursor()
        
        cur.execute("""
            SELECT id, panel_device_id, loop_number, max_devices, supervision_type,
                   wire_type, wire_gauge
            FROM slc_circuits 
            WHERE panel_device_id = ?
            ORDER BY loop_number
        """, (panel_device_id,))
        
        circuits = []
        for row in cur.fetchall():
            circuit = SLCCircuit(
                circuit_id=row['id'],
                panel_device_id=row['panel_device_id'],
                loop_number=row['loop_number'],
                max_devices=row['max_devices'],
                supervision_type=SupervisionType(row['supervision_type']),
                wire_type=row['wire_type'],
                wire_gauge=row['wire_gauge']
            )
            
            # Load devices for this circuit
            circuit.devices = self.get_circuit_devices(circuit.circuit_id)
            circuits.append(circuit)
            
        return circuits
    
    def get_circuit_devices(self, circuit_id: int) -> List[DeviceAddress]:
        """Get all devices on an SLC circuit."""
        cur = self.con.cursor()
        
        cur.execute("""
            SELECT da.device_address, da.project_device_id, da.device_type_code,
                   da.x_coordinate, da.y_coordinate, da.floor_level, da.zone_description,
                   d.model, d.name
            FROM device_addresses da
            LEFT JOIN devices d ON da.project_device_id = d.id
            WHERE da.slc_circuit_id = ?
            ORDER BY da.device_address
        """, (circuit_id,))
        
        devices = []
        for row in cur.fetchall():
            device = DeviceAddress(
                address=row['device_address'],
                device_id=row['project_device_id'],
                device_model=row['model'] or 'Unknown',
                device_type=row['device_type_code'],
                x_coord=row['x_coordinate'] or 0.0,
                y_coord=row['y_coordinate'] or 0.0,
                floor_level=row['floor_level'] or 'Ground',
                zone=row['zone_description'] or '',
                connected=True
            )
            devices.append(device)
            
        return devices
    
    def assign_device_address(self, circuit_id: int, device_id: int, device_type: str,
                            x_coord: float, y_coord: float, floor_level: str = "Ground",
                            zone: str = "", preferred_address: Optional[int] = None) -> int:
        """Assign next available address to a device on SLC circuit."""
        cur = self.con.cursor()
        
        # Get circuit info
        cur.execute("SELECT max_devices FROM slc_circuits WHERE id = ?", (circuit_id,))
        circuit = cur.fetchone()
        if not circuit:
            raise ValueError(f"Circuit {circuit_id} not found")
        
        # Get used addresses
        cur.execute("""
            SELECT device_address FROM device_addresses 
            WHERE slc_circuit_id = ? 
            ORDER BY device_address
        """, (circuit_id,))
        
        used_addresses = {row['device_address'] for row in cur.fetchall()}
        
        # Determine address to assign
        if preferred_address and preferred_address not in used_addresses:
            address = preferred_address
        else:
            # Find next available address
            address = None
            for addr in range(1, circuit['max_devices'] + 1):
                if addr not in used_addresses:
                    address = addr
                    break
        
        if not address:
            raise ValueError(f"Circuit {circuit_id} is full (max {circuit['max_devices']} devices)")
        
        # Insert device address assignment
        cur.execute("""
            INSERT INTO device_addresses 
            (project_device_id, slc_circuit_id, device_address, device_type_code,
             x_coordinate, y_coordinate, floor_level, zone_description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (device_id, circuit_id, address, device_type, x_coord, y_coord, floor_level, zone))
        
        self.con.commit()
        
        # Update circuit calculations
        self._update_circuit_calculations(circuit_id)
        
        return address
    
    def remove_device_address(self, circuit_id: int, address: int) -> bool:
        """Remove device from SLC circuit."""
        cur = self.con.cursor()
        
        # Remove connections first
        cur.execute("""
            DELETE FROM device_connections 
            WHERE from_device_address_id IN (
                SELECT id FROM device_addresses 
                WHERE slc_circuit_id = ? AND device_address = ?
            ) OR to_device_address_id IN (
                SELECT id FROM device_addresses
                WHERE slc_circuit_id = ? AND device_address = ?
            )
        """, (circuit_id, address, circuit_id, address))
        
        # Remove device address
        cur.execute("""
            DELETE FROM device_addresses 
            WHERE slc_circuit_id = ? AND device_address = ?
        """, (circuit_id, address))
        
        removed = cur.rowcount > 0
        self.con.commit()
        
        if removed:
            self._update_circuit_calculations(circuit_id)
            
        return removed
    
    def create_device_connection(self, from_circuit_id: int, from_address: int,
                               to_circuit_id: int, to_address: int,
                               connection_type: str = "SLC",
                               wire_path: Optional[List[Tuple[float, float]]] = None,
                               length_feet: float = 0.0) -> int:
        """Create a connection between two devices."""
        cur = self.con.cursor()
        
        # Get device address IDs
        cur.execute("""
            SELECT id FROM device_addresses 
            WHERE slc_circuit_id = ? AND device_address = ?
        """, (from_circuit_id, from_address))
        from_id = cur.fetchone()
        
        cur.execute("""
            SELECT id FROM device_addresses
            WHERE slc_circuit_id = ? AND device_address = ?  
        """, (to_circuit_id, to_address))
        to_id = cur.fetchone()
        
        if not from_id or not to_id:
            raise ValueError("One or both device addresses not found")
        
        # Create connection
        wire_path_json = json.dumps(wire_path) if wire_path else None
        
        cur.execute("""
            INSERT INTO device_connections 
            (from_device_address_id, to_device_address_id, connection_type, 
             wire_path_json, length_feet)
            VALUES (?, ?, ?, ?, ?)
        """, (from_id['id'], to_id['id'], connection_type, wire_path_json, length_feet))
        
        connection_id = cur.lastrowid
        assert connection_id is not None
        self.con.commit()
        
        return connection_id
    
    def get_device_connections(self, circuit_id: int, address: int) -> List[Dict[str, Any]]:
        """Get all connections for a specific device."""
        cur = self.con.cursor()
        
        cur.execute("""
            SELECT dc.*, 
                   da_from.device_address as from_address,
                   da_from.slc_circuit_id as from_circuit,
                   da_to.device_address as to_address, 
                   da_to.slc_circuit_id as to_circuit
            FROM device_connections dc
            JOIN device_addresses da_from ON dc.from_device_address_id = da_from.id
            JOIN device_addresses da_to ON dc.to_device_address_id = da_to.id
            WHERE (da_from.slc_circuit_id = ? AND da_from.device_address = ?)
               OR (da_to.slc_circuit_id = ? AND da_to.device_address = ?)
        """, (circuit_id, address, circuit_id, address))
        
        return [dict(row) for row in cur.fetchall()]
    
    def _update_circuit_calculations(self, circuit_id: int):
        """Update electrical calculations for a circuit."""
        cur = self.con.cursor()
        
        # Get all devices on circuit with their electrical specs
        cur.execute("""
            SELECT fas.current_standby_ma, fas.current_alarm_ma, fas.voltage_nominal
            FROM device_addresses da
            JOIN fire_alarm_specs fas ON da.project_device_id = fas.device_id
            WHERE da.slc_circuit_id = ?
        """, (circuit_id,))
        
        standby_total = 0.0
        alarm_total = 0.0
        
        for row in cur.fetchall():
            standby_total += row['current_standby_ma'] or 0.0
            alarm_total += row['current_alarm_ma'] or 0.0
        
        # Update calculations (convert mA to A)
        cur.execute("""
            UPDATE circuit_calculations 
            SET total_standby_current = ?, total_alarm_current = ?, calculated_at = CURRENT_TIMESTAMP
            WHERE slc_circuit_id = ?
        """, (standby_total / 1000.0, alarm_total / 1000.0, circuit_id))
        
        self.con.commit()
    
    def get_circuit_summary(self, circuit_id: int) -> Dict[str, Any]:
        """Get comprehensive circuit summary with calculations."""
        cur = self.con.cursor()
        
        # Get circuit info
        cur.execute("""
            SELECT sc.*, cc.total_standby_current, cc.total_alarm_current,
                   cc.voltage_drop_percent, cc.calculated_at
            FROM slc_circuits sc
            LEFT JOIN circuit_calculations cc ON sc.id = cc.slc_circuit_id
            WHERE sc.id = ?
        """, (circuit_id,))
        
        circuit = cur.fetchone()
        if not circuit:
            return {}
        
        # Get device count
        cur.execute("""
            SELECT COUNT(*) as device_count FROM device_addresses 
            WHERE slc_circuit_id = ?
        """, (circuit_id,))
        device_count = cur.fetchone()['device_count']
        
        return {
            'circuit_id': circuit['id'],
            'loop_number': circuit['loop_number'], 
            'device_count': device_count,
            'max_devices': circuit['max_devices'],
            'utilization_percent': (device_count / circuit['max_devices']) * 100,
            'standby_current_a': circuit['total_standby_current'] or 0.0,
            'alarm_current_a': circuit['total_alarm_current'] or 0.0,
            'voltage_drop_percent': circuit['voltage_drop_percent'] or 0.0,
            'supervision_type': circuit['supervision_type'],
            'wire_info': f"{circuit['wire_type']} {circuit['wire_gauge']}",
            'last_calculated': circuit['calculated_at']
        }
    
    def validate_circuit_compliance(self, circuit_id: int) -> Dict[str, Any]:
        """Validate circuit compliance with NFPA 72 requirements."""
        summary = self.get_circuit_summary(circuit_id)
        issues = []
        warnings = []
        
        # Check device count
        if summary['device_count'] > summary['max_devices']:
            issues.append(f"Device count ({summary['device_count']}) exceeds maximum ({summary['max_devices']})")
        
        # Check current draw
        if summary['alarm_current_a'] > 3.0:  # Typical SLC current limit
            issues.append(f"Alarm current ({summary['alarm_current_a']:.3f}A) exceeds 3.0A limit")
        
        # Check utilization
        if summary['utilization_percent'] > 90:
            warnings.append(f"Circuit utilization ({summary['utilization_percent']:.1f}%) is high")
        
        # Check voltage drop
        if summary['voltage_drop_percent'] > 5.0:
            issues.append(f"Voltage drop ({summary['voltage_drop_percent']:.1f}%) exceeds 5% limit")
        
        return {
            'compliant': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'summary': summary
        }