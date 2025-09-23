"""
Bill of Materials (BOM) automation for fire alarm systems.
Generates comprehensive BOMs from connected devices and panel configurations
with quantity calculations, pricing, and specifications.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import sqlite3
import csv
import json


@dataclass
class BOMItem:
    """Represents an item in the Bill of Materials."""
    manufacturer: str
    part_number: str
    description: str
    quantity: int
    unit_price: float = 0.0
    extended_price: float = 0.0
    category: str = ""
    specifications: str = ""
    notes: str = ""
    
    def __post_init__(self):
        self.extended_price = self.quantity * self.unit_price


@dataclass
class BOMSection:
    """Represents a section of the BOM (e.g., Panels, Devices, Wire)."""
    section_name: str
    items: List[BOMItem]
    section_total: float = 0.0
    
    def __post_init__(self):
        self.section_total = sum(item.extended_price for item in self.items)


@dataclass
class ProjectBOM:
    """Complete Bill of Materials for a fire alarm project."""
    project_id: str
    project_name: str
    generated_date: datetime
    sections: List[BOMSection]
    total_cost: float = 0.0
    labor_hours: float = 0.0
    labor_rate: float = 75.0
    labor_cost: float = 0.0
    grand_total: float = 0.0
    
    def __post_init__(self):
        self.total_cost = sum(section.section_total for section in self.sections)
        self.labor_cost = self.labor_hours * self.labor_rate
        self.grand_total = self.total_cost + self.labor_cost


class BOMGenerator:
    """Generates Bills of Materials for fire alarm projects."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.con = db_connection
        self.con.row_factory = sqlite3.Row
        
        # Default pricing - would typically come from pricing database
        self.default_pricing = {
            # Fire-Lite FACP panels
            "MS-9200UDLS": 2850.00,
            "MS-9600UDLS": 4200.00,
            "MS-4": 425.00,
            
            # Fire-Lite detectors
            "SD355": 45.00,
            "SD355T": 52.00,
            "HD355": 38.00,
            
            # Fire-Lite notification
            "PSE-4": 35.00,
            "PSH-4": 48.00,
            "PSM-4": 85.00,
            
            # Fire-Lite initiating/modules
            "BG-12LX": 28.00,
            "BG-12": 22.00,
            "MMX-1": 65.00,
            "MMI-1": 58.00,
            
            # Wire and accessories
            "FPLR_18_2": 0.45,  # per foot
            "FPLR_16_2": 0.62,  # per foot
            "FPLR_14_2": 0.85,  # per foot
            "SLC_SHIELD": 0.75,  # per foot
            "CONDUIT_3_4": 1.25,  # per foot
            "DEVICE_BOX": 8.50,
            "DUCT_DETECTOR_HOUSING": 125.00,
        }
        
        # Labor estimates (hours per device/task)
        self.labor_estimates = {
            "FACP": 8.0,        # Panel installation
            "Detector": 0.75,    # Per detector
            "Notification": 1.0, # Per notification device
            "Initiating": 1.25,  # Per pull station
            "Module": 1.5,       # Per control module
            "wire_per_100ft": 2.0,  # Wire pulling/termination
            "commissioning": 16.0,  # System commissioning
            "programming": 12.0,    # Panel programming
        }
        
    def generate_project_bom(self, project_id: str, project_name: str = "") -> ProjectBOM:
        """Generate complete BOM for a fire alarm project."""
        
        if not project_name:
            project_name = f"Fire Alarm Project {project_id}"
            
        # Get all devices and components used in project
        panels = self._get_project_panels(project_id)
        devices = self._get_project_devices(project_id)
        wire_requirements = self._calculate_wire_requirements(project_id)
        accessories = self._calculate_accessories(project_id, devices)
        
        # Create BOM sections
        sections = []
        
        # Panels section
        if panels:
            panel_section = self._create_panels_section(panels)
            sections.append(panel_section)
            
        # Devices section
        if devices:
            device_section = self._create_devices_section(devices)
            sections.append(device_section)
            
        # Wire and conduit section
        if wire_requirements:
            wire_section = self._create_wire_section(wire_requirements)
            sections.append(wire_section)
            
        # Accessories section
        if accessories:
            accessory_section = self._create_accessories_section(accessories)
            sections.append(accessory_section)
            
        # Calculate labor
        labor_hours = self._calculate_labor_hours(panels, devices, wire_requirements)
        
        # Create project BOM
        bom = ProjectBOM(
            project_id=project_id,
            project_name=project_name,
            generated_date=datetime.now(),
            sections=sections,
            labor_hours=labor_hours
        )
        
        return bom
        
    def _get_project_panels(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all panels used in project."""
        cur = self.con.cursor()
        
        cur.execute("""
            SELECT d.manufacturer_id, m.name as manufacturer, d.model, d.name,
                   COUNT(*) as quantity, d.properties_json
            FROM project_panels pp
            JOIN devices d ON pp.device_id = d.id
            JOIN manufacturers m ON d.manufacturer_id = m.id
            WHERE pp.project_id = ?
            GROUP BY d.id
        """, (project_id,))
        
        return [dict(row) for row in cur.fetchall()]
        
    def _get_project_devices(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all devices used in project with quantities."""
        cur = self.con.cursor()
        
        cur.execute("""
            SELECT d.manufacturer_id, m.name as manufacturer, d.model, d.name,
                   dt.code as device_type, COUNT(*) as quantity,
                   fas.current_standby_ma, fas.current_alarm_ma, fas.addressable
            FROM device_addresses da
            JOIN slc_circuits sc ON da.slc_circuit_id = sc.id
            JOIN project_panels pp ON sc.panel_device_id = pp.device_id
            JOIN devices d ON da.project_device_id = d.id
            JOIN manufacturers m ON d.manufacturer_id = m.id
            JOIN device_types dt ON d.type_id = dt.id
            LEFT JOIN fire_alarm_specs fas ON d.id = fas.device_id
            WHERE pp.project_id = ?
            GROUP BY d.id
            ORDER BY dt.code, d.model
        """, (project_id,))
        
        return [dict(row) for row in cur.fetchall()]
        
    def _calculate_wire_requirements(self, project_id: str) -> Dict[str, float]:
        """Calculate wire requirements for project."""
        cur = self.con.cursor()
        
        # Get total wire lengths by circuit
        cur.execute("""
            SELECT sc.wire_type, sc.wire_gauge, 
                   SUM(dc.length_feet) as total_length_feet
            FROM device_connections dc
            JOIN device_addresses da ON dc.from_device_address_id = da.id
            JOIN slc_circuits sc ON da.slc_circuit_id = sc.id
            JOIN project_panels pp ON sc.panel_device_id = pp.device_id
            WHERE pp.project_id = ?
            GROUP BY sc.wire_type, sc.wire_gauge
        """, (project_id,))
        
        wire_requirements = {}
        for row in cur.fetchall():
            wire_key = f"{row['wire_type']}_{row['wire_gauge'].replace(' ', '_')}"
            wire_requirements[wire_key] = row['total_length_feet']
            
        return wire_requirements
        
    def _calculate_accessories(self, project_id: str, devices: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate accessories needed (boxes, hardware, etc.)."""
        accessories = {}
        
        # Device boxes (one per device)
        total_devices = sum(device['quantity'] for device in devices)
        accessories['DEVICE_BOX'] = total_devices
        
        # Duct detector housings (estimate 10% of smoke detectors in HVAC areas)
        smoke_detectors = sum(device['quantity'] for device in devices 
                            if 'SD' in device.get('model', ''))
        accessories['DUCT_DETECTOR_HOUSING'] = max(1, int(smoke_detectors * 0.1))
        
        return accessories
        
    def _create_panels_section(self, panels: List[Dict[str, Any]]) -> BOMSection:
        """Create BOM section for fire alarm panels."""
        items = []
        
        for panel in panels:
            price = self.default_pricing.get(panel['model'], 0.0)
            
            # Parse properties for additional specifications
            properties = json.loads(panel.get('properties_json', '{}'))
            specs = []
            if properties.get('slc_loops'):
                specs.append(f"{properties['slc_loops']} SLC loops")
            if properties.get('total_devices'):
                specs.append(f"{properties['total_devices']} device capacity")
                
            item = BOMItem(
                manufacturer=panel['manufacturer'],
                part_number=panel['model'],
                description=panel['name'],
                quantity=panel['quantity'],
                unit_price=price,
                category="Fire Alarm Control Panel",
                specifications=", ".join(specs)
            )
            items.append(item)
            
        return BOMSection("Fire Alarm Control Panels", items)
        
    def _create_devices_section(self, devices: List[Dict[str, Any]]) -> BOMSection:
        """Create BOM section for fire alarm devices."""
        items = []
        
        for device in devices:
            price = self.default_pricing.get(device['model'], 0.0)
            
            # Build specifications
            specs = []
            if device.get('addressable'):
                specs.append("Addressable")
            if device.get('current_standby_ma'):
                specs.append(f"{device['current_standby_ma']}mA standby")
                
            item = BOMItem(
                manufacturer=device['manufacturer'],
                part_number=device['model'],
                description=device['name'],
                quantity=device['quantity'],
                unit_price=price,
                category=f"Fire Alarm {device['device_type']}",
                specifications=", ".join(specs)
            )
            items.append(item)
            
        return BOMSection("Fire Alarm Devices", items)
        
    def _create_wire_section(self, wire_requirements: Dict[str, float]) -> BOMSection:
        """Create BOM section for wire and conduit."""
        items = []
        
        for wire_type, length_feet in wire_requirements.items():
            # Add 10% for waste/spares
            total_length = int(length_feet * 1.1)
            
            price_per_foot = self.default_pricing.get(wire_type, 0.50)
            
            # Convert wire type back to readable format
            display_name = wire_type.replace('_', ' ')
            
            item = BOMItem(
                manufacturer="Generic",
                part_number=wire_type,
                description=f"{display_name} Fire Alarm Cable",
                quantity=total_length,
                unit_price=price_per_foot,
                category="Wire and Cable",
                specifications=f"Per foot, includes 10% waste allowance"
            )
            items.append(item)
            
        # Add conduit (estimate 50% of wire length needs conduit)
        total_wire_length = sum(wire_requirements.values())
        conduit_length = int(total_wire_length * 0.5)
        
        if conduit_length > 0:
            conduit_item = BOMItem(
                manufacturer="Generic",
                part_number="CONDUIT_3_4",
                description="3/4\" EMT Conduit",
                quantity=conduit_length,
                unit_price=self.default_pricing.get("CONDUIT_3_4", 1.25),
                category="Conduit and Fittings",
                specifications="Per foot"
            )
            items.append(conduit_item)
            
        return BOMSection("Wire, Cable, and Conduit", items)
        
    def _create_accessories_section(self, accessories: Dict[str, int]) -> BOMSection:
        """Create BOM section for accessories and hardware."""
        items = []
        
        for accessory_type, quantity in accessories.items():
            price = self.default_pricing.get(accessory_type, 10.0)
            
            # Generate description based on type
            descriptions = {
                'DEVICE_BOX': "4\" Square Device Box",
                'DUCT_DETECTOR_HOUSING': "Duct Detector Housing Kit"
            }
            
            item = BOMItem(
                manufacturer="Generic",
                part_number=accessory_type,
                description=descriptions.get(accessory_type, accessory_type),
                quantity=quantity,
                unit_price=price,
                category="Accessories and Hardware"
            )
            items.append(item)
            
        return BOMSection("Accessories and Hardware", items)
        
    def _calculate_labor_hours(self, panels: List[Dict[str, Any]], 
                             devices: List[Dict[str, Any]],
                             wire_requirements: Dict[str, float]) -> float:
        """Calculate estimated labor hours for project."""
        total_hours = 0.0
        
        # Panel installation
        total_panels = sum(panel['quantity'] for panel in panels)
        total_hours += total_panels * self.labor_estimates['FACP']
        
        # Device installation
        for device in devices:
            device_type = device.get('device_type', 'Device')
            labor_rate = self.labor_estimates.get(device_type, 1.0)
            total_hours += device['quantity'] * labor_rate
            
        # Wire installation
        total_wire_feet = sum(wire_requirements.values())
        total_hours += (total_wire_feet / 100.0) * self.labor_estimates['wire_per_100ft']
        
        # System commissioning and programming
        total_hours += self.labor_estimates['commissioning']
        total_hours += self.labor_estimates['programming']
        
        return total_hours
        
    def export_bom_csv(self, bom: ProjectBOM, filename: str):
        """Export BOM to CSV file."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([f"Bill of Materials - {bom.project_name}"])
            writer.writerow([f"Generated: {bom.generated_date.strftime('%Y-%m-%d %H:%M')}"])
            writer.writerow([])  # Empty row
            
            # Column headers
            writer.writerow([
                "Section", "Manufacturer", "Part Number", "Description", 
                "Quantity", "Unit Price", "Extended Price", "Specifications"
            ])
            
            # BOM sections
            for section in bom.sections:
                for item in section.items:
                    writer.writerow([
                        section.section_name,
                        item.manufacturer,
                        item.part_number,
                        item.description,
                        item.quantity,
                        f"${item.unit_price:.2f}",
                        f"${item.extended_price:.2f}",
                        item.specifications
                    ])
                    
                # Section total
                writer.writerow([
                    f"{section.section_name} Total", "", "", "", "", "", 
                    f"${section.section_total:.2f}", ""
                ])
                writer.writerow([])  # Empty row
                
            # Totals
            writer.writerow(["Material Total", "", "", "", "", "", f"${bom.total_cost:.2f}", ""])
            writer.writerow(["Labor Hours", "", "", "", f"{bom.labor_hours:.1f}", f"${bom.labor_rate:.2f}", f"${bom.labor_cost:.2f}", ""])
            writer.writerow(["Grand Total", "", "", "", "", "", f"${bom.grand_total:.2f}", ""])
            
    def export_bom_json(self, bom: ProjectBOM, filename: str):
        """Export BOM to JSON file."""
        bom_data = {
            'project_id': bom.project_id,
            'project_name': bom.project_name,
            'generated_date': bom.generated_date.isoformat(),
            'sections': [],
            'totals': {
                'material_cost': bom.total_cost,
                'labor_hours': bom.labor_hours,
                'labor_rate': bom.labor_rate,
                'labor_cost': bom.labor_cost,
                'grand_total': bom.grand_total
            }
        }
        
        for section in bom.sections:
            section_data = {
                'section_name': section.section_name,
                'section_total': section.section_total,
                'items': []
            }
            
            for item in section.items:
                item_data = {
                    'manufacturer': item.manufacturer,
                    'part_number': item.part_number,
                    'description': item.description,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'extended_price': item.extended_price,
                    'category': item.category,
                    'specifications': item.specifications,
                    'notes': item.notes
                }
                section_data['items'].append(item_data)
                
            bom_data['sections'].append(section_data)
            
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(bom_data, jsonfile, indent=2)
            
    def update_pricing(self, pricing_updates: Dict[str, float]):
        """Update default pricing with new values."""
        self.default_pricing.update(pricing_updates)
        
    def get_bom_summary(self, bom: ProjectBOM) -> Dict[str, Any]:
        """Get summary statistics for BOM."""
        total_items = sum(len(section.items) for section in bom.sections)
        total_quantity = sum(
            sum(item.quantity for item in section.items) 
            for section in bom.sections
        )
        
        return {
            'total_sections': len(bom.sections),
            'total_items': total_items,
            'total_quantity': total_quantity,
            'material_cost': bom.total_cost,
            'labor_hours': bom.labor_hours,
            'labor_cost': bom.labor_cost,
            'grand_total': bom.grand_total,
            'cost_per_device': bom.grand_total / max(1, total_quantity)
        }