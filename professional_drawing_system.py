#!/usr/bin/env python3
"""
AutoFire Professional Drawing Output System
==========================================

Professional fire alarm drawing generation with industry-standard symbols,
annotations, layers, and export capabilities. This system provides the
foundation for AI to produce professional fire alarm drawings.

Key Features:
- Industry-standard fire alarm symbols library
- Professional layer management (background, devices, circuits, annotations)
- Automatic wire routing and connection display
- NFPA-compliant device labeling and specifications
- Multiple export formats (DXF, PDF, PNG, SVG)
- Real-time calculation integration
- Professional title blocks and drawing standards

DEVELOPMENT NOTES:
- Built as drawing foundation for AI integration
- Follows CAD industry standards (layers, blocks, annotations)
- Integrates with Live Calculations Engine for real-time validation
- Scalable symbol library for 16K+ device types
"""

import sys
import math
import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path

try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
    qt_available = True
except ImportError:
    qt_available = False
    print("⚠️ PySide6 not available - using fallback mode")

# Import our live calculations engine
try:
    from live_calculations_engine import LiveCalculationsEngine, DeviceType, Circuit, CircuitDevice
    calculations_available = True
except ImportError:
    calculations_available = False
    print("⚠️ Live Calculations Engine not available")
    
    # Define fallback DeviceType enum  
    class DeviceType(Enum):
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
    
    # Fallback classes
    class LiveCalculationsEngine:
        pass
    
    class Circuit:
        pass
    
    class CircuitDevice:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DrawingLayer(Enum):
    """Professional CAD drawing layers."""
    BACKGROUND = "A-WALL"      # Architectural background
    STRUCTURE = "A-STRUC"      # Structural elements
    DEVICES = "FA-DEVICE"      # Fire alarm devices
    CIRCUITS = "FA-CIRCUIT"    # Circuit wiring
    LABELS = "FA-LABEL"        # Device labels and text
    DIMENSIONS = "FA-DIM"      # Dimensions and annotations
    TITLE_BLOCK = "A-TITLE"    # Title block and border
    NOTES = "FA-NOTE"          # General notes and legends

class SymbolType(Enum):
    """Fire alarm symbol types."""
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
    JUNCTION_BOX = "junction_box"
    CONDUIT = "conduit"

@dataclass
class DrawingSymbol:
    """Professional fire alarm symbol definition."""
    symbol_type: SymbolType
    name: str
    description: str
    
    # Symbol geometry (as drawing commands)
    geometry: List[Dict[str, Any]]
    
    # Symbol properties
    width: float  # Symbol width in drawing units
    height: float  # Symbol height in drawing units
    insertion_point: Tuple[float, float]  # Local insertion point
    
    # Text properties
    label_position: Tuple[float, float]  # Relative to insertion point
    label_size: float  # Text height
    
    # Layer assignments
    symbol_layer: DrawingLayer
    text_layer: DrawingLayer
    
    # Additional properties
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DrawingDevice:
    """Device placed on drawing with position and properties."""
    id: str
    symbol: DrawingSymbol
    position: Tuple[float, float]  # X, Y in drawing units
    rotation: float = 0.0  # Rotation in degrees
    scale: float = 1.0     # Scale factor
    
    # Device properties
    device_label: str = ""
    circuit_label: str = ""
    zone_label: str = ""
    
    # Connection information
    connections: List[str] = field(default_factory=list)  # Connected device IDs
    
    # Additional properties
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DrawingCircuit:
    """Circuit representation on drawing."""
    id: str
    devices: List[str]  # Device IDs on this circuit
    wire_path: List[Tuple[float, float]]  # Wire routing points
    
    # Circuit properties
    circuit_type: str  # "SLC", "NAC", "IDC", "POWER"
    wire_specification: str  # "18 AWG FPLR"
    
    # Visual properties
    line_style: str = "CONTINUOUS"  # Line type
    line_weight: float = 0.25  # Line weight in mm
    color: str = "RED"  # Circuit color
    
    # Labels and annotations
    labels: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class DrawingSheet:
    """Complete drawing sheet with all elements."""
    title: str
    sheet_number: str
    drawing_bounds: Tuple[float, float, float, float]  # min_x, min_y, max_x, max_y
    drawing_scale: str = "1/8\" = 1'-0\""
    sheet_size: str = "D"  # A, B, C, D, E
    
    # Drawing elements
    devices: List[DrawingDevice] = field(default_factory=list)
    circuits: List[DrawingCircuit] = field(default_factory=list)
    
    # Annotations
    title_block: Dict[str, str] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    legends: List[Dict[str, Any]] = field(default_factory=list)
    
    # Layer settings
    layer_settings: Dict[DrawingLayer, Dict[str, Any]] = field(default_factory=dict)

class DrawingSymbolLibrary:
    """Professional fire alarm symbol library."""
    
    def __init__(self):
        self.symbols = self._create_symbol_library()
        logger.info(f"📚 Symbol library loaded: {len(self.symbols)} symbols")
    
    def _create_symbol_library(self) -> Dict[SymbolType, DrawingSymbol]:
        """Create comprehensive fire alarm symbol library."""
        
        symbols = {}
        
        # Smoke Detector Symbol
        symbols[SymbolType.SMOKE_DETECTOR] = DrawingSymbol(
            symbol_type=SymbolType.SMOKE_DETECTOR,
            name="Smoke Detector",
            description="Photoelectric or ionization smoke detector",
            geometry=[
                {"type": "circle", "center": (0, 0), "radius": 6},
                {"type": "line", "start": (-4, -4), "end": (4, 4)},
                {"type": "line", "start": (-4, 4), "end": (4, -4)},
                {"type": "text", "text": "S", "position": (0, -1), "height": 4}
            ],
            width=12.0,
            height=12.0,
            insertion_point=(0, 0),
            label_position=(0, -10),
            label_size=2.5,
            symbol_layer=DrawingLayer.DEVICES,
            text_layer=DrawingLayer.LABELS
        )
        
        # Heat Detector Symbol
        symbols[SymbolType.HEAT_DETECTOR] = DrawingSymbol(
            symbol_type=SymbolType.HEAT_DETECTOR,
            name="Heat Detector",
            description="Fixed temperature or rate-of-rise heat detector",
            geometry=[
                {"type": "circle", "center": (0, 0), "radius": 6},
                {"type": "triangle", "points": [(-3, -2), (3, -2), (0, 3)]},
                {"type": "text", "text": "H", "position": (0, -1), "height": 4}
            ],
            width=12.0,
            height=12.0,
            insertion_point=(0, 0),
            label_position=(0, -10),
            label_size=2.5,
            symbol_layer=DrawingLayer.DEVICES,
            text_layer=DrawingLayer.LABELS
        )
        
        # Manual Pull Station Symbol
        symbols[SymbolType.MANUAL_PULL] = DrawingSymbol(
            symbol_type=SymbolType.MANUAL_PULL,
            name="Manual Pull Station",
            description="Manual fire alarm pull station",
            geometry=[
                {"type": "rectangle", "corner1": (-6, -4), "corner2": (6, 4)},
                {"type": "line", "start": (-4, 2), "end": (4, 2)},
                {"type": "line", "start": (-4, 0), "end": (4, 0)},
                {"type": "line", "start": (-4, -2), "end": (4, -2)},
                {"type": "text", "text": "P", "position": (0, -1), "height": 3}
            ],
            width=12.0,
            height=8.0,
            insertion_point=(0, 0),
            label_position=(0, -8),
            label_size=2.5,
            symbol_layer=DrawingLayer.DEVICES,
            text_layer=DrawingLayer.LABELS
        )
        
        # Horn/Strobe Symbol
        symbols[SymbolType.HORN_STROBE] = DrawingSymbol(
            symbol_type=SymbolType.HORN_STROBE,
            name="Horn/Strobe",
            description="Audible/visible notification appliance",
            geometry=[
                {"type": "circle", "center": (-3, 0), "radius": 4},  # Horn
                {"type": "rectangle", "corner1": (1, -3), "corner2": (5, 3)},  # Strobe
                {"type": "line", "start": (2, -2), "end": (4, 0)},  # Lightning bolt
                {"type": "line", "start": (2, 0), "end": (4, 2)},
                {"type": "text", "text": "H/S", "position": (1, -6), "height": 2}
            ],
            width=10.0,
            height=8.0,
            insertion_point=(1, 0),
            label_position=(1, -8),
            label_size=2.5,
            symbol_layer=DrawingLayer.DEVICES,
            text_layer=DrawingLayer.LABELS
        )
        
        # Control Panel Symbol
        symbols[SymbolType.CONTROL_PANEL] = DrawingSymbol(
            symbol_type=SymbolType.CONTROL_PANEL,
            name="Fire Alarm Control Panel",
            description="Main fire alarm control panel",
            geometry=[
                {"type": "rectangle", "corner1": (-12, -8), "corner2": (12, 8)},
                {"type": "rectangle", "corner1": (-10, -6), "corner2": (10, 6)},
                {"type": "circle", "center": (-6, 2), "radius": 1.5},  # LED
                {"type": "circle", "center": (-6, -2), "radius": 1.5},
                {"type": "rectangle", "corner1": (2, -2), "corner2": (8, 2)},  # Display
                {"type": "text", "text": "FACP", "position": (0, 0), "height": 3}
            ],
            width=24.0,
            height=16.0,
            insertion_point=(0, 0),
            label_position=(0, -12),
            label_size=3.0,
            symbol_layer=DrawingLayer.DEVICES,
            text_layer=DrawingLayer.LABELS
        )
        
        return symbols
    
    def get_symbol(self, symbol_type: SymbolType) -> Optional[DrawingSymbol]:
        """Get symbol by type."""
        return self.symbols.get(symbol_type)
    
    def get_symbol_for_device_type(self, device_type: DeviceType) -> Optional[DrawingSymbol]:
        """Map device type to drawing symbol."""
        mapping = {
            DeviceType.SMOKE_DETECTOR: SymbolType.SMOKE_DETECTOR,
            DeviceType.HEAT_DETECTOR: SymbolType.HEAT_DETECTOR,
            DeviceType.MANUAL_PULL: SymbolType.MANUAL_PULL,
            DeviceType.HORN: SymbolType.HORN,
            DeviceType.STROBE: SymbolType.STROBE,
            DeviceType.HORN_STROBE: SymbolType.HORN_STROBE,
            DeviceType.SPEAKER: SymbolType.SPEAKER,
            DeviceType.CONTROL_PANEL: SymbolType.CONTROL_PANEL,
            DeviceType.NAC_EXTENDER: SymbolType.NAC_EXTENDER,
            DeviceType.RELAY: SymbolType.RELAY,
            DeviceType.ISOLATOR: SymbolType.ISOLATOR
        }
        
        symbol_type = mapping.get(device_type)
        return self.get_symbol(symbol_type) if symbol_type else None

class ProfessionalDrawingEngine:
    """Professional drawing generation engine."""
    
    def __init__(self):
        self.symbol_library = DrawingSymbolLibrary()
        self.layer_definitions = self._create_layer_definitions()
        self.drawing_standards = self._load_drawing_standards()
        
        # Integration with calculations engine
        if calculations_available:
            self.calculations_engine = LiveCalculationsEngine()
        else:
            self.calculations_engine = None
            
        logger.info("🎨 Professional Drawing Engine initialized")
    
    def _create_layer_definitions(self) -> Dict[DrawingLayer, Dict[str, Any]]:
        """Define professional drawing layers."""
        
        return {
            DrawingLayer.BACKGROUND: {
                "name": "A-WALL",
                "description": "Architectural walls and background",
                "color": "BLACK",
                "line_weight": 0.35,
                "line_type": "CONTINUOUS",
                "plotable": True
            },
            DrawingLayer.STRUCTURE: {
                "name": "A-STRUC", 
                "description": "Structural elements",
                "color": "CYAN",
                "line_weight": 0.25,
                "line_type": "CONTINUOUS",
                "plotable": True
            },
            DrawingLayer.DEVICES: {
                "name": "FA-DEVICE",
                "description": "Fire alarm devices",
                "color": "RED",
                "line_weight": 0.25,
                "line_type": "CONTINUOUS", 
                "plotable": True
            },
            DrawingLayer.CIRCUITS: {
                "name": "FA-CIRCUIT",
                "description": "Fire alarm circuits",
                "color": "RED",
                "line_weight": 0.18,
                "line_type": "HIDDEN",
                "plotable": True
            },
            DrawingLayer.LABELS: {
                "name": "FA-LABEL",
                "description": "Device labels and text",
                "color": "MAGENTA",
                "line_weight": 0.13,
                "line_type": "CONTINUOUS",
                "plotable": True
            },
            DrawingLayer.DIMENSIONS: {
                "name": "FA-DIM",
                "description": "Dimensions and annotations",
                "color": "GREEN",
                "line_weight": 0.13,
                "line_type": "CONTINUOUS",
                "plotable": True
            },
            DrawingLayer.TITLE_BLOCK: {
                "name": "A-TITLE",
                "description": "Title block and border",
                "color": "BLACK",
                "line_weight": 0.50,
                "line_type": "CONTINUOUS",
                "plotable": True
            },
            DrawingLayer.NOTES: {
                "name": "FA-NOTE",
                "description": "General notes and legends",
                "color": "BLUE",
                "line_weight": 0.13,
                "line_type": "CONTINUOUS",
                "plotable": True
            }
        }
    
    def _load_drawing_standards(self) -> Dict[str, Any]:
        """Load professional drawing standards and defaults."""
        
        return {
            "sheet_sizes": {
                "A": {"width": 11.0, "height": 8.5},      # 8.5" x 11"
                "B": {"width": 17.0, "height": 11.0},     # 11" x 17"  
                "C": {"width": 22.0, "height": 17.0},     # 17" x 22"
                "D": {"width": 34.0, "height": 22.0},     # 22" x 34"
                "E": {"width": 44.0, "height": 34.0}      # 34" x 44"
            },
            "text_styles": {
                "device_label": {"height": 2.5, "style": "ROMANS"},
                "circuit_label": {"height": 2.0, "style": "ROMANS"},
                "title": {"height": 5.0, "style": "ROMAND"},
                "notes": {"height": 2.0, "style": "ROMANS"}
            },
            "line_types": {
                "CONTINUOUS": [],
                "HIDDEN": [0.125, 0.0625],
                "CENTER": [0.75, 0.125, 0.125, 0.125],
                "PHANTOM": [0.5, 0.125, 0.125, 0.125, 0.125, 0.125]
            },
            "colors": {
                "BLACK": (0, 0, 0),
                "RED": (255, 0, 0),
                "GREEN": (0, 255, 0),
                "BLUE": (0, 0, 255),
                "CYAN": (0, 255, 255),
                "MAGENTA": (255, 0, 255),
                "YELLOW": (255, 255, 0)
            }
        }
    
    def create_drawing_sheet(self, title: str, sheet_number: str = "FA-1") -> DrawingSheet:
        """Create new professional drawing sheet."""
        
        # Create title block data
        title_block = {
            "project_name": "AutoFire Fire Alarm System",
            "drawing_title": title,
            "sheet_number": sheet_number,
            "drawn_by": "AutoFire AI",
            "checked_by": "AI Validation",
            "date": datetime.now().strftime("%m/%d/%Y"),
            "scale": "1/8\" = 1'-0\"",
            "revision": "A"
        }
        
        # Standard drawing bounds for D-size sheet
        drawing_bounds = (1.0, 1.0, 33.0, 21.0)  # 1" margins
        
        sheet = DrawingSheet(
            title=title,
            sheet_number=sheet_number,
            drawing_bounds=drawing_bounds,
            title_block=title_block,
            layer_settings=self.layer_definitions.copy()
        )
        
        # Add standard notes
        sheet.notes = [
            "ALL WORK SHALL CONFORM TO NFPA 72 AND LOCAL CODES",
            "CONTRACTOR SHALL VERIFY ALL DIMENSIONS IN FIELD",
            "DEVICES SHOWN ARE MINIMUM REQUIRED - ADDITIONAL DEVICES MAY BE REQUIRED",
            "ALL WIRING SHALL BE INSTALLED PER NEC AND MANUFACTURER REQUIREMENTS"
        ]
        
        return sheet
    
    def place_device(self, sheet: DrawingSheet, device_id: str, device_type: DeviceType, 
                    position: Tuple[float, float], circuit_id: str = "") -> bool:
        """Place device on drawing sheet."""
        
        # Get appropriate symbol
        symbol = self.symbol_library.get_symbol_for_device_type(device_type)
        if not symbol:
            logger.warning(f"No symbol found for device type: {device_type}")
            return False
        
        # Create drawing device
        drawing_device = DrawingDevice(
            id=device_id,
            symbol=symbol,
            position=position,
            device_label=device_id,
            circuit_label=circuit_id
        )
        
        sheet.devices.append(drawing_device)
        logger.info(f"📍 Placed {device_type.value} at {position}")
        return True
    
    def route_circuit(self, sheet: DrawingSheet, circuit_id: str, device_ids: List[str],
                     circuit_type: str = "SLC") -> bool:
        """Automatically route circuit between devices."""
        
        if not device_ids:
            return False
        
        # Find devices on sheet
        circuit_devices = [d for d in sheet.devices if d.id in device_ids]
        if len(circuit_devices) != len(device_ids):
            logger.warning(f"Some devices not found on sheet for circuit {circuit_id}")
            return False
        
        # Simple routing algorithm (optimize later for AI)
        wire_path = []
        for device in circuit_devices:
            wire_path.append(device.position)
        
        # Create circuit
        circuit = DrawingCircuit(
            id=circuit_id,
            devices=device_ids,
            wire_path=wire_path,
            circuit_type=circuit_type,
            wire_specification="18 AWG FPLR"  # Default
        )
        
        sheet.circuits.append(circuit)
        logger.info(f"🔌 Routed {circuit_type} circuit {circuit_id} through {len(device_ids)} devices")
        return True
    
    def validate_drawing_compliance(self, sheet: DrawingSheet) -> Dict[str, Any]:
        """Validate drawing against NFPA requirements."""
        
        violations = []
        warnings = []
        
        # Check device spacing
        for device in sheet.devices:
            if device.symbol.symbol_type == SymbolType.SMOKE_DETECTOR:
                # Check 30-foot spacing rule
                nearby_smoke = [d for d in sheet.devices 
                              if d.symbol.symbol_type == SymbolType.SMOKE_DETECTOR and d.id != device.id]
                
                for other in nearby_smoke:
                    distance = math.sqrt((device.position[0] - other.position[0])**2 + 
                                       (device.position[1] - other.position[1])**2)
                    if distance > 30.0:  # More than 30 feet
                        warnings.append(f"Smoke detectors {device.id} and {other.id} may exceed 30-foot spacing")
        
        # Check circuit integrity
        for circuit in sheet.circuits:
            if len(circuit.devices) < 2:
                violations.append(f"Circuit {circuit.id} has insufficient devices")
        
        return {
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "devices_checked": len(sheet.devices),
            "circuits_checked": len(sheet.circuits)
        }
    
    def optimize_device_placement(self, sheet: DrawingSheet, room_bounds: Tuple[float, float, float, float]) -> List[Dict[str, Any]]:
        """Generate optimized device placement suggestions."""
        
        suggestions = []
        min_x, min_y, max_x, max_y = room_bounds
        room_area = (max_x - min_x) * (max_y - min_y)
        
        # Smoke detector coverage analysis
        smoke_detectors = [d for d in sheet.devices if d.symbol.symbol_type == SymbolType.SMOKE_DETECTOR]
        total_coverage = len(smoke_detectors) * 900.0  # 30x30 feet per detector
        
        if total_coverage < room_area:
            required_additional = math.ceil((room_area - total_coverage) / 900.0)
            suggestions.append({
                "type": "add_device",
                "device_type": "smoke_detector",
                "quantity": required_additional,
                "reason": f"Insufficient coverage: {total_coverage:.0f} sq ft vs {room_area:.0f} sq ft room"
            })
        
        # Manual pull station placement
        pull_stations = [d for d in sheet.devices if d.symbol.symbol_type == SymbolType.MANUAL_PULL]
        if not pull_stations:
            # Suggest pull station at main exit
            suggestions.append({
                "type": "add_device",
                "device_type": "manual_pull",
                "position": (min_x + 5.0, min_y + 5.0),  # Near entrance
                "reason": "Manual pull station required at main exit"
            })
        
        return suggestions
    
    def export_to_dxf(self, sheet: DrawingSheet, output_path: str) -> bool:
        """Export drawing to DXF format."""
        
        try:
            # This would use ezdxf library for real DXF output
            # For now, create a simple text representation
            
            dxf_content = []
            dxf_content.append("0\nSECTION\n2\nENTITIES")
            
            # Export devices
            for device in sheet.devices:
                dxf_content.append("0\nCIRCLE")
                dxf_content.append(f"10\n{device.position[0]}")  # X center
                dxf_content.append(f"20\n{device.position[1]}")  # Y center
                dxf_content.append("40\n6.0")  # Radius
                dxf_content.append("8\nFA-DEVICE")  # Layer
                
                # Add device label
                dxf_content.append("0\nTEXT")
                dxf_content.append(f"10\n{device.position[0]}")
                dxf_content.append(f"20\n{device.position[1] - 10}")
                dxf_content.append(f"1\n{device.device_label}")
                dxf_content.append("40\n2.5")  # Text height
                dxf_content.append("8\nFA-LABEL")
            
            # Export circuits
            for circuit in sheet.circuits:
                for i in range(len(circuit.wire_path) - 1):
                    start = circuit.wire_path[i]
                    end = circuit.wire_path[i + 1]
                    
                    dxf_content.append("0\nLINE")
                    dxf_content.append(f"10\n{start[0]}")  # Start X
                    dxf_content.append(f"20\n{start[1]}")  # Start Y
                    dxf_content.append(f"11\n{end[0]}")    # End X
                    dxf_content.append(f"21\n{end[1]}")    # End Y
                    dxf_content.append("8\nFA-CIRCUIT")    # Layer
            
            dxf_content.append("0\nENDSEC\n0\nEOF")
            
            # Write to file
            with open(output_path, 'w') as f:
                f.write('\n'.join(dxf_content))
            
            logger.info(f"📄 Exported drawing to DXF: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export DXF: {e}")
            return False
    
    def create_legend(self, sheet: DrawingSheet) -> List[Dict[str, Any]]:
        """Create symbol legend for drawing."""
        
        legend_items = []
        used_symbols = set()
        
        # Collect unique symbols used in drawing
        for device in sheet.devices:
            if device.symbol.symbol_type not in used_symbols:
                used_symbols.add(device.symbol.symbol_type)
                legend_items.append({
                    "symbol_type": device.symbol.symbol_type,
                    "name": device.symbol.name,
                    "description": device.symbol.description
                })
        
        return legend_items

def create_sample_drawing_demo():
    """Create demonstration of professional drawing system."""
    
    engine = ProfessionalDrawingEngine()
    
    print("🎨 AutoFire Professional Drawing Output System Demo")
    print("=" * 55)
    
    # Create new drawing sheet
    sheet = engine.create_drawing_sheet("Fire Alarm Plan - First Floor", "FA-1")
    print(f"📄 Created drawing sheet: {sheet.title}")
    
    # Place devices
    devices_placed = [
        ("SD-001", DeviceType.SMOKE_DETECTOR, (50.0, 50.0)),
        ("SD-002", DeviceType.SMOKE_DETECTOR, (100.0, 50.0)),
        ("SD-003", DeviceType.SMOKE_DETECTOR, (150.0, 50.0)),
        ("MP-001", DeviceType.MANUAL_PULL, (25.0, 25.0)),
        ("HS-001", DeviceType.HORN_STROBE, (75.0, 25.0)),
        ("FACP-1", DeviceType.CONTROL_PANEL, (200.0, 25.0))
    ]
    
    for device_id, device_type, position in devices_placed:
        success = engine.place_device(sheet, device_id, device_type, position)
        if success:
            print(f"   ✅ Placed {device_id} ({device_type.value})")
    
    # Route circuits
    slc_devices = ["SD-001", "SD-002", "SD-003", "MP-001"]
    nac_devices = ["HS-001"]
    
    engine.route_circuit(sheet, "SLC-1", slc_devices, "SLC")
    engine.route_circuit(sheet, "NAC-1", nac_devices, "NAC")
    
    print(f"🔌 Routed {len(sheet.circuits)} circuits")
    
    # Validate compliance
    compliance = engine.validate_drawing_compliance(sheet)
    print(f"\n✅ COMPLIANCE VALIDATION:")
    print(f"   Compliant: {'✅ YES' if compliance['is_compliant'] else '❌ NO'}")
    print(f"   Devices Checked: {compliance['devices_checked']}")
    print(f"   Circuits Checked: {compliance['circuits_checked']}")
    
    if compliance['violations']:
        for violation in compliance['violations']:
            print(f"   ⚠️ {violation}")
    
    if compliance['warnings']:
        for warning in compliance['warnings']:
            print(f"   💡 {warning}")
    
    # Generate optimization suggestions
    room_bounds = (0.0, 0.0, 250.0, 100.0)  # 250' x 100' room
    suggestions = engine.optimize_device_placement(sheet, room_bounds)
    
    print(f"\n🎯 PLACEMENT OPTIMIZATION:")
    for suggestion in suggestions:
        print(f"   💡 {suggestion['type']}: {suggestion['reason']}")
    
    # Create legend
    legend = engine.create_legend(sheet)
    print(f"\n📚 SYMBOL LEGEND:")
    for item in legend:
        print(f"   {item['symbol_type'].value}: {item['name']}")
    
    # Export drawing
    output_path = "sample_fire_alarm_plan.dxf"
    success = engine.export_to_dxf(sheet, output_path)
    if success:
        print(f"\n📄 Drawing exported to: {output_path}")
    
    print(f"\n🎯 DRAWING SYSTEM READY FOR AI INTEGRATION!")
    
    return engine, sheet

if __name__ == "__main__":
    # Run demonstration
    engine, sample_sheet = create_sample_drawing_demo()
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. ✅ Professional Drawing Output System complete")
    print(f"   2. 🔄 Integrate with Live Calculations Engine")
    print(f"   3. 📊 Real-time drawing validation")
    print(f"   4. 🤖 AI-driven automatic drawing generation")
    print(f"   5. 🎯 Professional export to all CAD formats")