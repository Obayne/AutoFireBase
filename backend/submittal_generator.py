"""
Submittal packet generator for fire alarm systems.
Creates comprehensive submittal packages with cut sheets, operational matrices,
riser diagrams, and all required documentation.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3
import json
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, red, blue, green
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors


@dataclass
class CutSheetInfo:
    """Information about a device cut sheet."""
    manufacturer: str
    model: str
    description: str
    filename: str
    pages: int = 1
    file_path: str = ""
    
    
@dataclass
class OperationalMatrix:
    """Fire alarm operational matrix data."""
    input_devices: List[Dict[str, Any]]
    output_devices: List[Dict[str, Any]]
    matrix_data: Dict[str, List[str]]  # Input device -> List of output devices
    

@dataclass
class RiserDiagram:
    """Fire alarm riser diagram information."""
    panel_info: Dict[str, Any]
    circuits: List[Dict[str, Any]]
    devices_per_circuit: Dict[int, List[Dict[str, Any]]]
    wire_specifications: Dict[str, str]
    

@dataclass
class SubmittalPackage:
    """Complete submittal package."""
    project_info: Dict[str, str]
    device_schedule: List[Dict[str, Any]]
    cut_sheets: List[CutSheetInfo]
    operational_matrix: OperationalMatrix
    riser_diagram: RiserDiagram
    specifications: str
    calculations: Dict[str, Any]
    generated_date: datetime


class SubmittalGenerator:
    """Generates fire alarm submittal packages."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.con = db_connection
        self.con.row_factory = sqlite3.Row
        
        # Standard cut sheet database (would be populated with actual files)
        self.cut_sheet_database = {
            # Fire-Lite devices
            "MS-9200UDLS": CutSheetInfo("Fire-Lite", "MS-9200UDLS", 
                                      "Addressable Fire Alarm Control Panel", 
                                      "MS-9200UDLS_cutsheet.pdf", 4),
            "MS-9600UDLS": CutSheetInfo("Fire-Lite", "MS-9600UDLS",
                                      "Large Addressable FACP",
                                      "MS-9600UDLS_cutsheet.pdf", 6),
            "SD355": CutSheetInfo("Fire-Lite", "SD355",
                                "Photoelectric Smoke Detector",
                                "SD355_cutsheet.pdf", 2),
            "HD355": CutSheetInfo("Fire-Lite", "HD355", 
                                "Heat Detector",
                                "HD355_cutsheet.pdf", 2),
            "PSE-4": CutSheetInfo("Fire-Lite", "PSE-4",
                                "Addressable Strobe",
                                "PSE-4_cutsheet.pdf", 2),
            "PSH-4": CutSheetInfo("Fire-Lite", "PSH-4",
                                "Addressable Horn/Strobe", 
                                "PSH-4_cutsheet.pdf", 2),
            "BG-12LX": CutSheetInfo("Fire-Lite", "BG-12LX",
                                  "Addressable Manual Pull Station",
                                  "BG-12LX_cutsheet.pdf", 1)
        }
        
    def generate_submittal_package(self, project_id: str, 
                                 output_directory: str) -> SubmittalPackage:
        """Generate complete submittal package for project."""
        
        # Gather project information
        project_info = self._get_project_info(project_id)
        device_schedule = self._generate_device_schedule(project_id)
        cut_sheets = self._collect_cut_sheets(device_schedule)
        operational_matrix = self._generate_operational_matrix(project_id)
        riser_diagram = self._generate_riser_diagram(project_id)
        specifications = self._generate_specifications(project_id)
        calculations = self._get_project_calculations(project_id)
        
        # Create submittal package
        submittal = SubmittalPackage(
            project_info=project_info,
            device_schedule=device_schedule,
            cut_sheets=cut_sheets,
            operational_matrix=operational_matrix,
            riser_diagram=riser_diagram,
            specifications=specifications,
            calculations=calculations,
            generated_date=datetime.now()
        )
        
        # Generate PDF documents
        self._generate_submittal_pdf(submittal, output_directory)
        
        return submittal
        
    def _get_project_info(self, project_id: str) -> Dict[str, str]:
        """Get project information."""
        # Mock project info - would come from project database
        return {
            "project_name": f"Fire Alarm Project {project_id}",
            "project_address": "123 Main Street, Anytown, USA",
            "client": "ABC Corporation",
            "consultant": "Fire Safety Engineering Inc.",
            "contractor": "Fire Systems Contractor LLC",
            "project_number": f"FA-{project_id}",
            "submittal_number": "001",
            "revision": "0"
        }
        
    def _generate_device_schedule(self, project_id: str) -> List[Dict[str, Any]]:
        """Generate device schedule with quantities and specifications."""
        cur = self.con.cursor()
        
        # Get all devices used in project
        cur.execute("""
            SELECT d.manufacturer_id, m.name as manufacturer, d.model, d.name,
                   dt.code as device_type, COUNT(*) as quantity,
                   fas.current_standby_ma, fas.current_alarm_ma, fas.addressable,
                   fas.ul_category, d.properties_json
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
        
        devices = []
        for row in cur.fetchall():
            properties = json.loads(row['properties_json']) if row['properties_json'] else {}
            
            device_info = {
                'item': len(devices) + 1,
                'manufacturer': row['manufacturer'],
                'model': row['model'], 
                'description': row['name'],
                'quantity': row['quantity'],
                'device_type': row['device_type'],
                'addressable': bool(row['addressable']),
                'current_standby_ma': row['current_standby_ma'] or 0.0,
                'current_alarm_ma': row['current_alarm_ma'] or 0.0,
                'ul_listing': row['ul_category'] or 'UL 268',
                'specifications': self._format_device_specifications(row, properties)
            }
            devices.append(device_info)
            
        return devices
        
    def _format_device_specifications(self, device_row, properties: Dict[str, Any]) -> str:
        """Format device specifications text."""
        specs = []
        
        if device_row['addressable']:
            specs.append("Addressable")
            
        if device_row['current_standby_ma']:
            specs.append(f"Standby: {device_row['current_standby_ma']}mA")
            
        if device_row['current_alarm_ma']:
            specs.append(f"Alarm: {device_row['current_alarm_ma']}mA")
            
        # Add specific properties based on device type
        if 'candela_options' in properties:
            candelas = properties['candela_options']
            specs.append(f"Candela: {'/'.join(map(str, candelas))}")
            
        if 'thermal_rating' in properties:
            specs.append(f"Thermal: {properties['thermal_rating']}°F")
            
        if 'detection_type' in properties:
            specs.append(f"Type: {properties['detection_type'].title()}")
            
        return "; ".join(specs)
        
    def _collect_cut_sheets(self, device_schedule: List[Dict[str, Any]]) -> List[CutSheetInfo]:
        """Collect cut sheets for all devices in schedule."""
        cut_sheets = []
        seen_models = set()
        
        for device in device_schedule:
            model = device['model']
            if model not in seen_models and model in self.cut_sheet_database:
                cut_sheets.append(self.cut_sheet_database[model])
                seen_models.add(model)
                
        return cut_sheets
        
    def _generate_operational_matrix(self, project_id: str) -> OperationalMatrix:
        """Generate operational matrix showing input/output relationships."""
        cur = self.con.cursor()
        
        # Get input devices (detectors, pull stations)
        cur.execute("""
            SELECT da.device_address, d.model, d.name, da.zone_description
            FROM device_addresses da
            JOIN devices d ON da.project_device_id = d.id
            JOIN device_types dt ON d.type_id = dt.id
            WHERE dt.code IN ('Detector', 'Initiating')
            ORDER BY da.device_address
        """)
        
        input_devices = [dict(row) for row in cur.fetchall()]
        
        # Get output devices (notification appliances, modules)
        cur.execute("""
            SELECT da.device_address, d.model, d.name, da.zone_description
            FROM device_addresses da
            JOIN devices d ON da.project_device_id = d.id
            JOIN device_types dt ON d.type_id = dt.id
            WHERE dt.code IN ('Notification', 'Module')
            ORDER BY da.device_address
        """)
        
        output_devices = [dict(row) for row in cur.fetchall()]
        
        # Create matrix mapping (simplified - would be based on actual zone logic)
        matrix_data = {}
        for input_device in input_devices:
            zone = input_device.get('zone_description', 'General')
            # Map inputs to outputs in same zone
            outputs = [out['device_address'] for out in output_devices 
                      if out.get('zone_description', 'General') == zone]
            matrix_data[input_device['device_address']] = outputs or ['ALL']
            
        return OperationalMatrix(input_devices, output_devices, matrix_data)
        
    def _generate_riser_diagram(self, project_id: str) -> RiserDiagram:
        """Generate riser diagram data."""
        cur = self.con.cursor()
        
        # Get panel information
        cur.execute("""
            SELECT d.model, d.name, d.properties_json
            FROM project_panels pp
            JOIN devices d ON pp.device_id = d.id
            WHERE pp.project_id = ?
        """, (project_id,))
        
        panel_row = cur.fetchone()
        panel_info = dict(panel_row) if panel_row else {}
        
        # Get circuit information
        cur.execute("""
            SELECT sc.loop_number, sc.max_devices, sc.wire_type, sc.wire_gauge,
                   COUNT(da.id) as device_count
            FROM slc_circuits sc
            LEFT JOIN device_addresses da ON sc.id = da.slc_circuit_id
            JOIN project_panels pp ON sc.panel_device_id = pp.device_id
            WHERE pp.project_id = ?
            GROUP BY sc.id
            ORDER BY sc.loop_number
        """, (project_id,))
        
        circuits = [dict(row) for row in cur.fetchall()]
        
        # Get devices per circuit
        devices_per_circuit = {}
        for circuit in circuits:
            cur.execute("""
                SELECT da.device_address, d.model, d.name, dt.code as device_type
                FROM device_addresses da
                JOIN devices d ON da.project_device_id = d.id
                JOIN device_types dt ON d.type_id = dt.id
                JOIN slc_circuits sc ON da.slc_circuit_id = sc.id
                JOIN project_panels pp ON sc.panel_device_id = pp.device_id
                WHERE pp.project_id = ? AND sc.loop_number = ?
                ORDER BY da.device_address
            """, (project_id, circuit['loop_number']))
            
            devices_per_circuit[circuit['loop_number']] = [dict(row) for row in cur.fetchall()]
            
        wire_specs = {
            "SLC": "18 AWG FPLR, Class A wiring",
            "NAC": "16 AWG FPLR, Class B wiring", 
            "Power": "12 AWG THWN, in conduit"
        }
        
        return RiserDiagram(panel_info, circuits, devices_per_circuit, wire_specs)
        
    def _generate_specifications(self, project_id: str) -> str:
        """Generate written specifications."""
        specs = f"""
FIRE ALARM SYSTEM SPECIFICATIONS
Project: {project_id}

1. GENERAL REQUIREMENTS
The fire alarm system shall be designed, installed, and tested in accordance with NFPA 72, 
National Fire Alarm and Signaling Code, latest edition, and all applicable local codes.

2. SYSTEM TYPE
The system shall be an addressable, microprocessor-based fire alarm control system capable
of identifying the specific location of each alarm condition.

3. CONTROL PANEL
The fire alarm control panel (FACP) shall be Fire-Lite MS-9200UDLS or approved equal.
The panel shall provide full supervision of all connected devices and circuits.

4. INITIATING DEVICES
All smoke detectors shall be photoelectric type, addressable devices listed for the
intended application. Heat detectors shall be fixed temperature type rated for 135°F.

5. NOTIFICATION APPLIANCES
All notification appliances shall be addressable and capable of synchronized operation.
Strobes shall comply with ADA requirements for photometric performance.

6. INSTALLATION
All devices shall be installed in accordance with manufacturer's instructions and
NFPA 72 requirements. All wiring shall be FPLR rated and installed in accordance
with NEC Article 760.

7. TESTING AND COMMISSIONING
The complete system shall be tested and commissioned in accordance with NFPA 72
acceptance testing procedures. All test results shall be documented.

8. WARRANTY
The complete fire alarm system shall be warranted for a period of two (2) years
from the date of final acceptance.
"""
        return specs.strip()
        
    def _get_project_calculations(self, project_id: str) -> Dict[str, Any]:
        """Get project calculations for submittal."""
        # Mock calculations - would use actual circuit calculation results
        return {
            "total_devices": 45,
            "standby_current": 2.5,  # Amps
            "alarm_current": 4.2,    # Amps
            "battery_capacity": 33,  # AH
            "voltage_drop_max": 3.2, # Percent
            "power_consumption": 101  # Watts
        }
        
    def _generate_submittal_pdf(self, submittal: SubmittalPackage, output_dir: str):
        """Generate submittal PDF document."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = output_path / f"Fire_Alarm_Submittal_{submittal.project_info['project_number']}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Add custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=16,
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12
        )
        
        # Title page
        story.append(Paragraph("FIRE ALARM SYSTEM SUBMITTAL", title_style))
        story.append(Spacer(1, 20))
        
        # Project information
        story.append(Paragraph("PROJECT INFORMATION", heading_style))
        project_data = [
            ["Project Name:", submittal.project_info['project_name']],
            ["Project Address:", submittal.project_info['project_address']],
            ["Client:", submittal.project_info['client']],
            ["Project Number:", submittal.project_info['project_number']],
            ["Submittal Number:", submittal.project_info['submittal_number']],
            ["Date:", submittal.generated_date.strftime("%B %d, %Y")]
        ]
        
        project_table = Table(project_data, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(project_table)
        story.append(PageBreak())
        
        # Device schedule
        story.append(Paragraph("DEVICE SCHEDULE", heading_style))
        
        schedule_data = [["Item", "Manufacturer", "Model", "Description", "Qty", "Specifications"]]
        for device in submittal.device_schedule:
            schedule_data.append([
                str(device['item']),
                device['manufacturer'],
                device['model'],
                device['description'],
                str(device['quantity']),
                device['specifications']
            ])
            
        schedule_table = Table(schedule_data, colWidths=[0.5*inch, 1*inch, 1*inch, 2*inch, 0.5*inch, 2*inch])
        schedule_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(schedule_table)
        story.append(PageBreak())
        
        # Operational matrix
        story.append(Paragraph("OPERATIONAL MATRIX", heading_style))
        
        # Create matrix table
        matrix_headers = ["Input Device"] + [f"#{dev['device_address']}" for dev in submittal.operational_matrix.output_devices]
        matrix_data = [matrix_headers]
        
        for input_dev in submittal.operational_matrix.input_devices:
            row = [f"#{input_dev['device_address']} {input_dev['name']}"]
            outputs = submittal.operational_matrix.matrix_data.get(input_dev['device_address'], [])
            
            for output_dev in submittal.operational_matrix.output_devices:
                if str(output_dev['device_address']) in map(str, outputs) or 'ALL' in outputs:
                    row.append("X")
                else:
                    row.append("")
            matrix_data.append(row)
            
        if matrix_data:
            matrix_table = Table(matrix_data)
            matrix_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(matrix_table)
            
        story.append(PageBreak())
        
        # Specifications
        story.append(Paragraph("TECHNICAL SPECIFICATIONS", heading_style))
        story.append(Paragraph(submittal.specifications, styles['Normal']))
        story.append(PageBreak())
        
        # Calculations summary
        story.append(Paragraph("CALCULATIONS SUMMARY", heading_style))
        calc_data = [
            ["Total Devices:", str(submittal.calculations['total_devices'])],
            ["Standby Current:", f"{submittal.calculations['standby_current']} A"],
            ["Alarm Current:", f"{submittal.calculations['alarm_current']} A"],
            ["Battery Capacity:", f"{submittal.calculations['battery_capacity']} AH"],
            ["Max Voltage Drop:", f"{submittal.calculations['voltage_drop_max']}%"],
            ["Power Consumption:", f"{submittal.calculations['power_consumption']} W"]
        ]
        
        calc_table = Table(calc_data, colWidths=[2*inch, 2*inch])
        calc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(calc_table)
        
        # Build PDF
        doc.build(story)
        
        return str(filename)
        
    def generate_cut_sheet_package(self, device_models: List[str], output_dir: str) -> str:
        """Generate combined cut sheet package."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        cut_sheet_filename = output_path / "Device_Cut_Sheets.pdf"
        
        # For this implementation, we'll create a placeholder
        # In a real system, this would combine actual PDF cut sheets
        c = canvas.Canvas(str(cut_sheet_filename), pagesize=letter)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "DEVICE CUT SHEETS")
        
        y_pos = 700
        for model in device_models:
            if model in self.cut_sheet_database:
                cut_sheet = self.cut_sheet_database[model]
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_pos, f"{cut_sheet.manufacturer} {cut_sheet.model}")
                y_pos -= 20
                
                c.setFont("Helvetica", 10)
                c.drawString(70, y_pos, cut_sheet.description)
                y_pos -= 15
                
                c.drawString(70, y_pos, f"Cut sheet: {cut_sheet.filename} ({cut_sheet.pages} pages)")
                y_pos -= 30
                
                if y_pos < 100:
                    c.showPage()
                    y_pos = 750
                    
        c.save()
        return str(cut_sheet_filename)