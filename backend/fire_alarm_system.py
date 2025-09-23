"""
Integrated Fire Alarm System Manager.
Combines all fire alarm components into a unified system for managing
fire alarm design, addressing, calculations, and documentation.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import sqlite3
import os
from pathlib import Path

# Import all fire alarm system components
from .slc_addressing import SLCAddressingSystem, SLCCircuit, DeviceAddress
from .circuit_calculations import CircuitCalculator, CircuitCalculationManager
from .bom_generator import BOMGenerator, ProjectBOM
from .submittal_generator import SubmittalGenerator, SubmittalPackage
from .pdf_paperspace import PaperSpaceManager, PaperSpaceLayout
from db.fire_alarm_seeder import initialize_fire_alarm_database
from db.firelite_catalog import FIRELITE_CATALOG, get_device_by_model
from frontend.layer_manager import FireAlarmLayerManager


@dataclass
class FireAlarmProject:
    """Complete fire alarm project data."""
    project_id: str
    project_name: str
    client: str
    location: str
    panels: List[Dict[str, Any]]
    circuits: List[SLCCircuit]
    devices: List[DeviceAddress]
    calculations: Dict[str, Any]
    bom: Optional[ProjectBOM] = None
    submittal: Optional[SubmittalPackage] = None


class FireAlarmSystemManager:
    """Master manager for complete fire alarm system functionality."""
    
    def __init__(self, db_path: str | None = None):
        """Initialize fire alarm system manager."""
        if db_path is None:
            db_path = os.path.join(os.path.expanduser('~'), 'AutoFire', 'fire_alarm.db')
            
        self.db_path = db_path
        self._ensure_database()
        
        # Initialize all subsystems
        self.con = sqlite3.connect(self.db_path)
        self.con.row_factory = sqlite3.Row
        
        self.slc_system = SLCAddressingSystem(self.con)
        self.circuit_calculator = CircuitCalculationManager(self.con)
        self.bom_generator = BOMGenerator(self.con)
        self.submittal_generator = SubmittalGenerator(self.con)
        self.paperspace_manager = PaperSpaceManager()
        self.layer_manager = FireAlarmLayerManager(self.con)
        
        # Current project
        self.current_project: Optional[FireAlarmProject] = None
        
    def _ensure_database(self):
        """Ensure fire alarm database exists and is initialized."""
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)
        
        if not os.path.exists(self.db_path):
            initialize_fire_alarm_database(self.db_path)
            
    def create_new_project(self, project_id: str, project_name: str, 
                          client: str = "", location: str = "") -> FireAlarmProject:
        """Create a new fire alarm project."""
        project = FireAlarmProject(
            project_id=project_id,
            project_name=project_name,
            client=client,
            location=location,
            panels=[],
            circuits=[],
            devices=[],
            calculations={}
        )
        
        self.current_project = project
        
        # Create project entry in database
        cur = self.con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT,
                client TEXT,
                location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            INSERT OR REPLACE INTO projects (id, name, client, location)
            VALUES (?, ?, ?, ?)
        """, (project_id, project_name, client, location))
        
        self.con.commit()
        return project
        
    def load_project(self, project_id: str) -> Optional[FireAlarmProject]:
        """Load an existing project."""
        cur = self.con.cursor()
        
        # Get project info
        cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project_row = cur.fetchone()
        
        if not project_row:
            return None
            
        # Load project components
        panels = self._load_project_panels(project_id)
        circuits = self._load_project_circuits(project_id)
        devices = self._load_project_devices(project_id)
        calculations = self.circuit_calculator.calculate_project_circuits(project_id)
        
        project = FireAlarmProject(
            project_id=project_id,
            project_name=project_row['name'],
            client=project_row['client'] or "",
            location=project_row['location'] or "",
            panels=panels,
            circuits=circuits,
            devices=devices,
            calculations=calculations
        )
        
        self.current_project = project
        return project
        
    def add_facp_panel(self, panel_model: str, x_coord: float, y_coord: float,
                       floor_level: str = "Ground") -> Dict[str, Any]:
        """Add a Fire Alarm Control Panel to the current project."""
        if not self.current_project:
            raise ValueError("No current project loaded")
            
        # Get panel specifications from catalog
        panel_spec = get_device_by_model(panel_model)
        if not panel_spec:
            raise ValueError(f"Panel model {panel_model} not found in catalog")
            
        # Add panel to project database
        cur = self.con.cursor()
        
        # Find device ID for panel
        cur.execute("""
            SELECT d.id FROM devices d
            JOIN manufacturers m ON d.manufacturer_id = m.id
            WHERE m.name = 'Fire-Lite' AND d.model = ?
        """, (panel_model,))
        
        device_row = cur.fetchone()
        if not device_row:
            raise ValueError(f"Panel {panel_model} not found in device database")
            
        device_id = device_row['id']
        
        # Insert project panel
        cur.execute("""
            INSERT INTO project_panels (project_id, device_id, panel_name, x_coordinate, y_coordinate, floor_level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.current_project.project_id, device_id, f"FACP-{panel_model}", x_coord, y_coord, floor_level))
        
        panel_id = cur.lastrowid
        self.con.commit()
        
        # Create SLC circuits for panel
        slc_loops = panel_spec.get('slc_loops', 1)
        for loop_num in range(1, slc_loops + 1):
            circuit_id = self.slc_system.create_slc_circuit(device_id, loop_num)
            print(f"Created SLC Loop {loop_num} (Circuit ID: {circuit_id})")
            
        # Update current project
        panel_info = {
            'id': panel_id,
            'device_id': device_id,
            'model': panel_model,
            'name': f"FACP-{panel_model}",
            'x': x_coord,
            'y': y_coord,
            'floor': floor_level,
            'specifications': panel_spec
        }
        
        self.current_project.panels.append(panel_info)
        return panel_info
        
    def add_device_to_circuit(self, device_model: str, circuit_id: int,
                            x_coord: float, y_coord: float, 
                            floor_level: str = "Ground", zone: str = "",
                            preferred_address: Optional[int] = None) -> int:
        """Add a device to an SLC circuit with automatic addressing."""
        if not self.current_project:
            raise ValueError("No current project loaded")
            
        # Get device specifications
        device_spec = get_device_by_model(device_model)
        if not device_spec:
            raise ValueError(f"Device model {device_model} not found in catalog")
            
        # Find device ID in database
        cur = self.con.cursor()
        cur.execute("""
            SELECT d.id, dt.code FROM devices d
            JOIN manufacturers m ON d.manufacturer_id = m.id
            JOIN device_types dt ON d.type_id = dt.id
            WHERE m.name = 'Fire-Lite' AND d.model = ?
        """, (device_model,))
        
        device_row = cur.fetchone()
        if not device_row:
            raise ValueError(f"Device {device_model} not found in device database")
            
        device_id = device_row['id']
        device_type = device_row['code']
        
        # Assign address on SLC circuit
        assigned_address = self.slc_system.assign_device_address(
            circuit_id, device_id, device_type, x_coord, y_coord, 
            floor_level, zone, preferred_address
        )
        
        print(f"Assigned address {assigned_address} to {device_model} on circuit {circuit_id}")
        
        # Update current project devices
        device_info = DeviceAddress(
            address=assigned_address,
            device_id=device_id,
            device_model=device_model,
            device_type=device_type,
            x_coord=x_coord,
            y_coord=y_coord,
            floor_level=floor_level,
            zone=zone,
            connected=True
        )
        
        self.current_project.devices.append(device_info)
        return assigned_address
        
    def create_device_connection(self, from_circuit_id: int, from_address: int,
                               to_circuit_id: int, to_address: int,
                               wire_path: Optional[List[Tuple[float, float]]] = None) -> int:
        """Create a wire connection between two devices."""
        connection_id = self.slc_system.create_device_connection(
            from_circuit_id, from_address, to_circuit_id, to_address,
            "SLC", wire_path
        )
        
        print(f"Created connection {connection_id} between addresses {from_address} and {to_address}")
        return connection_id
        
    def calculate_system_performance(self) -> Dict[str, Any]:
        """Calculate complete system performance and compliance."""
        if not self.current_project:
            raise ValueError("No current project loaded")
            
        calculations = self.circuit_calculator.calculate_project_circuits(
            self.current_project.project_id
        )
        
        self.current_project.calculations = calculations
        return calculations
        
    def generate_project_bom(self, include_labor: bool = True) -> ProjectBOM:
        """Generate Bill of Materials for current project."""
        if not self.current_project:
            raise ValueError("No current project loaded")
            
        bom = self.bom_generator.generate_project_bom(
            self.current_project.project_id,
            self.current_project.project_name
        )
        
        self.current_project.bom = bom
        return bom
        
    def generate_submittal_package(self, output_directory: str) -> SubmittalPackage:
        """Generate complete submittal package."""
        if not self.current_project:
            raise ValueError("No current project loaded")
            
        submittal = self.submittal_generator.generate_submittal_package(
            self.current_project.project_id,
            output_directory
        )
        
        self.current_project.submittal = submittal
        return submittal
        
    def export_project_pdf(self, output_filename: str, layout_name: str = "Fire Alarm Plan"):
        """Export project to PDF using paperspace system."""
        if not self.current_project:
            raise ValueError("No current project loaded")
            
        # Prepare CAD data for PDF export
        cad_data = {
            'devices': [
                {
                    'x': device.x_coord,
                    'y': device.y_coord,
                    'symbol': device.device_model,
                    'type': device.device_type,
                    'address': device.address,
                    'layer': self.layer_manager.get_device_layer(device.device_type)
                }
                for device in self.current_project.devices
            ],
            'connections': [],  # Would be populated with actual connection data
            'floor_plan': []    # Would be populated with floor plan elements
        }
        
        # Generate PDF
        self.paperspace_manager.generate_pdf(layout_name, output_filename, cad_data)
        
    def get_available_devices(self, device_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available Fire-Lite devices from catalog."""
        if device_type:
            devices = {k: v for k, v in FIRELITE_CATALOG.items() 
                      if v.get('type') == device_type}
        else:
            devices = FIRELITE_CATALOG
            
        return [
            {
                'model': model,
                'name': spec.get('name', model),
                'description': spec.get('description', ''),
                'type': spec.get('type', ''),
                'addressable': spec.get('addressable', False),
                'specifications': spec
            }
            for model, spec in devices.items()
        ]
        
    def get_project_summary(self) -> Dict[str, Any]:
        """Get summary of current project."""
        if not self.current_project:
            return {}
            
        return {
            'project_id': self.current_project.project_id,
            'project_name': self.current_project.project_name,
            'client': self.current_project.client,
            'location': self.current_project.location,
            'total_panels': len(self.current_project.panels),
            'total_circuits': len(self.current_project.circuits),
            'total_devices': len(self.current_project.devices),
            'calculations_complete': bool(self.current_project.calculations),
            'bom_generated': self.current_project.bom is not None,
            'submittal_generated': self.current_project.submittal is not None
        }
        
    def validate_project_compliance(self) -> Dict[str, Any]:
        """Validate project compliance with NFPA 72."""
        if not self.current_project:
            raise ValueError("No current project loaded")
            
        compliance_results = {
            'overall_compliant': True,
            'issues': [],
            'warnings': [],
            'circuit_compliance': []
        }
        
        # Check each circuit
        for circuit in self.current_project.circuits:
            circuit_compliance = self.slc_system.validate_circuit_compliance(circuit.circuit_id)
            compliance_results['circuit_compliance'].append(circuit_compliance)
            
            if not circuit_compliance['compliant']:
                compliance_results['overall_compliant'] = False
                compliance_results['issues'].extend(circuit_compliance['issues'])
                
            compliance_results['warnings'].extend(circuit_compliance['warnings'])
            
        return compliance_results
        
    def _load_project_panels(self, project_id: str) -> List[Dict[str, Any]]:
        """Load panels for a project."""
        cur = self.con.cursor()
        cur.execute("""
            SELECT pp.*, d.model, d.name 
            FROM project_panels pp
            JOIN devices d ON pp.device_id = d.id
            WHERE pp.project_id = ?
        """, (project_id,))
        
        return [dict(row) for row in cur.fetchall()]
        
    def _load_project_circuits(self, project_id: str) -> List[SLCCircuit]:
        """Load circuits for a project."""
        panels = self._load_project_panels(project_id)
        circuits = []
        
        for panel in panels:
            panel_circuits = self.slc_system.get_panel_circuits(panel['device_id'])
            circuits.extend(panel_circuits)
            
        return circuits
        
    def _load_project_devices(self, project_id: str) -> List[DeviceAddress]:
        """Load devices for a project."""
        circuits = self._load_project_circuits(project_id)
        devices = []
        
        for circuit in circuits:
            circuit_devices = self.slc_system.get_circuit_devices(circuit.circuit_id)
            devices.extend(circuit_devices)
            
        return devices
        
    def close(self):
        """Close database connection."""
        if self.con:
            self.con.close()


# Example usage functions
def create_sample_project():
    """Create a sample fire alarm project for demonstration."""
    manager = FireAlarmSystemManager()
    
    # Create new project
    project = manager.create_new_project(
        "DEMO-001",
        "Sample Office Building Fire Alarm",
        "ABC Corporation",
        "123 Main Street, Anytown, USA"
    )
    
    # Add FACP panel
    panel = manager.add_facp_panel("MS-9200UDLS", 50.0, 25.0, "First Floor")
    print(f"Added panel: {panel['name']}")
    
    # Get circuits for the panel
    circuits = manager.slc_system.get_panel_circuits(panel['device_id'])
    
    if circuits:
        circuit_id = circuits[0].circuit_id
        
        # Add devices to circuit
        devices_to_add = [
            ("SD355", 100.0, 100.0, "Office Area 1"),
            ("SD355", 150.0, 100.0, "Office Area 2"),
            ("HD355", 75.0, 150.0, "Storage Room"),
            ("PSE-4", 50.0, 200.0, "Corridor"),
            ("BG-12LX", 25.0, 175.0, "Main Exit")
        ]
        
        for device_model, x, y, zone in devices_to_add:
            address = manager.add_device_to_circuit(
                device_model, circuit_id, x, y, "First Floor", zone
            )
            print(f"Added {device_model} at address {address}")
    
    # Calculate system performance
    calculations = manager.calculate_system_performance()
    print(f"System calculations: {calculations}")
    
    # Generate BOM
    bom = manager.generate_project_bom()
    print(f"BOM generated with {len(bom.sections)} sections")
    
    # Validate compliance
    compliance = manager.validate_project_compliance()
    print(f"Project compliant: {compliance['overall_compliant']}")
    
    manager.close()
    return project


if __name__ == "__main__":
    # Run sample project creation
    create_sample_project()