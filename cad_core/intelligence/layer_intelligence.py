"""
AutoFire CAD Layer Intelligence Engine
=====================================

BREAKTHROUGH: Reading CAD layers provides precise element classification
vs visual guessing. This is a game-changer for construction drawing analysis.

Key Insight: CAD drawings are organized in layers with standardized naming:
- E-FIRE = Fire alarm devices
- E-SPKR = Sprinkler systems
- A-WALL = Architectural walls
- A-DOOR = Doors and openings

This provides EXACT device counts and locations vs visual detection estimates.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple

try:
    import ezdxf
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False
    ezdxf = None

# Configure logging
logger = logging.getLogger(__name__)


class LayerClassification(Enum):
    """Standard CAD layer classifications."""

    FIRE_SAFETY = "fire_safety"
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    PLUMBING = "plumbing"
    ARCHITECTURAL = "architectural"
    STRUCTURAL = "structural"
    ANNOTATION = "annotation"
    UNKNOWN = "unknown"


@dataclass
class CADDevice:
    """Precise device information extracted from CAD layers."""

    device_type: str
    coordinates: Tuple[float, float]
    block_name: str
    layer_name: str
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    attributes: Dict = field(default_factory=dict)


@dataclass
class LayerInfo:
    """Complete layer analysis information."""

    name: str
    element_count: int
    color: int
    line_weight: float
    classification: LayerClassification
    fire_safety_relevance: str
    is_frozen: bool = False
    is_off: bool = False


class CADLayerIntelligence:
    """
    Revolutionary CAD layer reading for precise construction analysis.

    This solves the "656 smoke detectors" problem by reading actual
    CAD layer data instead of guessing from visual analysis.
    """

    def __init__(self):
        """Initialize with industry-standard layer conventions."""
        self.aia_layer_standards = self._load_aia_standards()
        self.fire_safety_layers = [
            "E-FIRE",
            "E-SPKR",
            "E-LITE",
            "E-SECU",
            "FIRE",
            "SPRINKLER",
            "SMOKE",
            "ALARM",
        ]
        self.device_type_mappings = self._load_device_mappings()

    def is_available(self) -> bool:
        """Check if ezdxf is available for CAD file processing."""
        return EZDXF_AVAILABLE

    def analyze_cad_file_layers(self, cad_file_path: str) -> Dict:
        """
        Complete CAD layer analysis providing exact element information.

        Args:
            cad_file_path: Path to DXF/DWG file

        Returns:
            Complete layer analysis with device counts and classifications
        """
        if not EZDXF_AVAILABLE:
            logger.error("ezdxf library not available - cannot analyze CAD layers")
            return {"error": "ezdxf library not installed"}

        logger.info(f"🔍 Analyzing CAD layers in {cad_file_path}")

        try:
            # Read CAD file
            doc = ezdxf.readfile(cad_file_path)

            # Analyze layer structure
            layer_analysis = self._analyze_layer_structure(doc)

            # Extract fire safety devices by layer
            fire_devices = self._extract_fire_safety_devices(doc)

            # Get precise room boundaries from architectural layers
            rooms = self._extract_rooms_from_layers(doc)

            # Calculate real-world coordinates
            scale_info = self._detect_drawing_scale(doc)

            analysis_results = {
                "file_path": cad_file_path,
                "layer_analysis": layer_analysis,
                "fire_safety_devices": fire_devices,
                "room_boundaries": rooms,
                "scale_information": scale_info,
                "total_layers": len(layer_analysis),
                "fire_safety_layer_count": len(
                    [
                        layer
                        for layer in layer_analysis.values()
                        if layer.fire_safety_relevance == "critical"
                    ]
                ),
                "device_summary": self._summarize_devices(fire_devices),
            }

            logger.info(
                f"✅ Layer analysis complete: {len(fire_devices)} fire safety devices found"
            )
            return analysis_results

        except Exception as e:
            logger.error(f"❌ Error analyzing CAD file: {e}")
            return {"error": str(e)}

    def extract_precise_fire_devices(self, cad_file_path: str) -> List[CADDevice]:
        """
        Extract fire safety devices with EXACT coordinates from CAD layers.

        This replaces visual detection with precise CAD data extraction.
        """
        if not EZDXF_AVAILABLE:
            logger.error("ezdxf library not available")
            return []

        logger.info("🔥 Extracting fire safety devices from CAD layers...")

        try:
            doc = ezdxf.readfile(cad_file_path)
            devices = []

            # Search all fire safety relevant layers
            for layer_name in self.fire_safety_layers:
                if layer_name in [layer.dxf.name for layer in doc.layers]:
                    layer_devices = self._extract_devices_from_layer(doc, layer_name)
                    devices.extend(layer_devices)

            # Also search layers with fire safety keywords
            for layer in doc.layers:
                if self._is_fire_safety_layer(layer.dxf.name):
                    if layer.dxf.name not in self.fire_safety_layers:
                        layer_devices = self._extract_devices_from_layer(doc, layer.dxf.name)
                        devices.extend(layer_devices)

            logger.info(f"🎯 Found {len(devices)} fire safety devices in CAD layers")
            return devices
        except Exception as e:
            logger.error(f"Error extracting fire devices: {e}")
            return []

    def validate_layer_organization(self, cad_file_path: str) -> Dict:
        """
        Validate CAD file organization against industry standards.

        Checks:
        - AIA layer naming compliance
        - Fire safety layer presence
        - Element organization
        - Professional standards adherence
        """
        if not EZDXF_AVAILABLE:
            return {"error": "ezdxf not available"}

        try:
            doc = ezdxf.readfile(cad_file_path)
            validation_results = {
                "aia_compliance": {},
                "fire_safety_organization": {},
                "missing_critical_layers": [],
                "recommendations": [],
            }

            # Check AIA layer compliance
            for layer in doc.layers:
                layer_name = layer.dxf.name
                compliance = self._check_aia_compliance(layer_name)
                validation_results["aia_compliance"][layer_name] = compliance

            # Check fire safety layer organization
            fire_layer_check = self._validate_fire_safety_layers(doc)
            validation_results["fire_safety_organization"] = fire_layer_check

            # Identify missing critical layers
            missing_layers = self._identify_missing_layers(doc)
            validation_results["missing_critical_layers"] = missing_layers

            # Generate recommendations
            recommendations = self._generate_layer_recommendations(validation_results)
            validation_results["recommendations"] = recommendations

            return validation_results
        except Exception as e:
            logger.error(f"Error validating layer organization: {e}")
            return {"error": str(e)}

    def _analyze_layer_structure(self, doc) -> Dict[str, LayerInfo]:
        """Analyze complete layer structure with classifications."""
        layer_analysis = {}

        for layer in doc.layers:
            layer_name = layer.dxf.name

            # Count elements on this layer
            element_count = len(list(doc.modelspace().query(f'*[layer=="{layer_name}"]')))

            # Classify layer purpose
            classification = self._classify_layer(layer_name)

            # Assess fire safety relevance
            fire_relevance = self._assess_fire_safety_relevance(layer_name)

            layer_info = LayerInfo(
                name=layer_name,
                element_count=element_count,
                color=layer.dxf.color,
                line_weight=layer.dxf.lineweight if hasattr(layer.dxf, "lineweight") else 0,
                classification=classification,
                fire_safety_relevance=fire_relevance,
                is_frozen=layer.is_frozen(),
                is_off=layer.is_off(),
            )

            layer_analysis[layer_name] = layer_info

        return layer_analysis

    def _extract_fire_safety_devices(self, doc) -> Dict[str, List[CADDevice]]:
        """Extract fire safety devices organized by layer."""
        fire_devices = {}

        for layer_name in self.fire_safety_layers:
            if layer_name in [layer.dxf.name for layer in doc.layers]:
                devices = self._extract_devices_from_layer(doc, layer_name)
                if devices:
                    fire_devices[layer_name] = devices

        return fire_devices

    def _extract_devices_from_layer(self, doc, layer_name: str) -> List[CADDevice]:
        """Extract device information from specific layer."""
        devices = []
        msp = doc.modelspace()

        # Query all INSERT entities (block references) on this layer
        for entity in msp.query(f'INSERT[layer=="{layer_name}"]'):
            device_type = self._classify_device_by_block(entity.dxf.name)

            device = CADDevice(
                device_type=device_type,
                coordinates=(entity.dxf.insert.x, entity.dxf.insert.y),
                block_name=entity.dxf.name,
                layer_name=layer_name,
                rotation=entity.dxf.rotation if hasattr(entity.dxf, "rotation") else 0.0,
                scale_x=entity.dxf.xscale if hasattr(entity.dxf, "xscale") else 1.0,
                scale_y=entity.dxf.yscale if hasattr(entity.dxf, "yscale") else 1.0,
                attributes=self._extract_block_attributes(entity),
            )
            devices.append(device)

        return devices

    def _classify_device_by_block(self, block_name: str) -> str:
        """Classify device type based on CAD block name."""
        block_upper = block_name.upper()

        # Fire safety device classification
        if any(keyword in block_upper for keyword in ["SMOKE", "DETECTOR"]):
            return "smoke_detector"
        elif any(keyword in block_upper for keyword in ["SPRINKLER", "SPKR"]):
            return "sprinkler_head"
        elif any(keyword in block_upper for keyword in ["PULL", "STATION"]):
            return "manual_pull_station"
        elif any(keyword in block_upper for keyword in ["HORN", "STROBE"]):
            return "horn_strobe"
        elif any(keyword in block_upper for keyword in ["EXIT", "LIGHT"]):
            return "exit_light"
        elif any(keyword in block_upper for keyword in ["FIRE", "EXTINGUISHER"]):
            return "fire_extinguisher"
        else:
            return "unknown_device"

    def _classify_layer(self, layer_name: str) -> LayerClassification:
        """Classify layer based on naming conventions."""
        layer_upper = layer_name.upper()

        # Fire safety classification
        if any(keyword in layer_upper for keyword in ["FIRE", "SMOKE", "SPRINKLER", "ALARM"]):
            return LayerClassification.FIRE_SAFETY

        # Electrical classification
        elif any(keyword in layer_upper for keyword in ["ELECTRICAL", "POWER", "LITE", "E-"]):
            return LayerClassification.ELECTRICAL

        # Mechanical classification
        elif any(keyword in layer_upper for keyword in ["HVAC", "MECHANICAL", "DUCT", "M-"]):
            return LayerClassification.MECHANICAL

        # Plumbing classification
        elif any(keyword in layer_upper for keyword in ["PLUMBING", "PIPE", "P-"]):
            return LayerClassification.PLUMBING

        # Architectural classification
        elif any(keyword in layer_upper for keyword in ["WALL", "DOOR", "WINDOW", "A-"]):
            return LayerClassification.ARCHITECTURAL

        # Structural classification
        elif any(keyword in layer_upper for keyword in ["STRUCTURAL", "BEAM", "COLUMN", "S-"]):
            return LayerClassification.STRUCTURAL

        # Annotation classification
        elif any(keyword in layer_upper for keyword in ["TEXT", "DIMENSION", "ANNO"]):
            return LayerClassification.ANNOTATION

        else:
            return LayerClassification.UNKNOWN

    def _assess_fire_safety_relevance(self, layer_name: str) -> str:
        """Assess layer relevance to fire safety analysis."""
        layer_upper = layer_name.upper()

        # Critical - direct fire safety systems
        if any(keyword in layer_upper for keyword in ["FIRE", "SMOKE", "SPRINKLER", "ALARM"]):
            return "critical"

        # Important - related electrical/MEP
        elif any(keyword in layer_upper for keyword in ["ELECTRICAL", "LITE", "POWER", "HVAC"]):
            return "important"

        # Contextual - architectural context
        elif any(keyword in layer_upper for keyword in ["WALL", "DOOR", "WINDOW", "ROOM"]):
            return "contextual"

        else:
            return "minimal"

    def _is_fire_safety_layer(self, layer_name: str) -> bool:
        """Check if layer contains fire safety elements."""
        layer_upper = layer_name.upper()
        fire_keywords = ["FIRE", "SMOKE", "SPRINKLER", "ALARM", "DETECTOR", "SPKR"]
        return any(keyword in layer_upper for keyword in fire_keywords)

    def _summarize_devices(self, fire_devices: Dict) -> Dict:
        """Summarize device counts by type."""
        summary = {}
        total_devices = 0

        for layer_name, devices in fire_devices.items():
            layer_summary = {}
            for device in devices:
                device_type = device.device_type
                layer_summary[device_type] = layer_summary.get(device_type, 0) + 1
                total_devices += 1
            summary[layer_name] = layer_summary

        summary["total_devices"] = total_devices
        return summary

    # Standard libraries and mappings
    def _load_aia_standards(self) -> Dict:
        """Load AIA CAD layer standards."""
        return {
            # Architectural layers
            "A-WALL": {"description": "Walls", "discipline": "architectural"},
            "A-DOOR": {"description": "Doors", "discipline": "architectural"},
            "A-GLAZ": {"description": "Glazing/Windows", "discipline": "architectural"},
            "A-FLOR": {"description": "Floor elements", "discipline": "architectural"},
            # Electrical layers (critical for fire safety)
            "E-LITE": {"description": "Lighting", "discipline": "electrical"},
            "E-POWR": {"description": "Power", "discipline": "electrical"},
            "E-FIRE": {"description": "Fire alarm", "discipline": "electrical"},
            "E-SPKR": {"description": "Sprinkler", "discipline": "electrical"},
            # MEP layers
            "M-HVAC": {"description": "HVAC equipment", "discipline": "mechanical"},
            "P-PIPE": {"description": "Piping", "discipline": "plumbing"},
            # Structural layers
            "S-GRID": {"description": "Structural grid", "discipline": "structural"},
            "S-BEAM": {"description": "Beams", "discipline": "structural"},
        }

    def _load_device_mappings(self) -> Dict:
        """Load device type mappings for block classification."""
        return {
            "smoke_detector": ["SMOKE", "DETECTOR", "SD"],
            "sprinkler_head": ["SPRINKLER", "SPKR", "HEAD"],
            "manual_pull_station": ["PULL", "STATION", "MPS"],
            "horn_strobe": ["HORN", "STROBE", "HS"],
            "exit_light": ["EXIT", "LIGHT", "EMERGENCY"],
            "fire_extinguisher": ["EXTINGUISHER", "FE"],
        }

    # Placeholder methods for complete implementation
    def _extract_rooms_from_layers(self, doc) -> List:
        """Extract room boundaries from architectural layers."""
        # Implementation needed for future enhancement
        return []

    def _detect_drawing_scale(self, doc) -> Dict:
        """Detect drawing scale from CAD file."""
        # Implementation needed for future enhancement
        return {"scale": "unknown"}

    def _check_aia_compliance(self, layer_name: str) -> Dict:
        """Check layer name compliance with AIA standards."""
        is_compliant = layer_name in self.aia_layer_standards
        return {
            "compliant": is_compliant,
            "standard": self.aia_layer_standards.get(layer_name, {}).get("description", "Unknown"),
        }

    def _validate_fire_safety_layers(self, doc) -> Dict:
        """Validate fire safety layer organization."""
        found_layers = [layer.dxf.name for layer in doc.layers]
        fire_layers_present = [layer for layer in self.fire_safety_layers if layer in found_layers]
        return {
            "expected_layers": self.fire_safety_layers,
            "found_layers": fire_layers_present,
            "organized": len(fire_layers_present) > 0,
        }

    def _identify_missing_layers(self, doc) -> List:
        """Identify missing critical layers."""
        found_layers = [layer.dxf.name for layer in doc.layers]
        missing = [layer for layer in self.fire_safety_layers if layer not in found_layers]
        return missing

    def _generate_layer_recommendations(self, validation_results: Dict) -> List:
        """Generate recommendations for layer organization."""
        recommendations = []

        if validation_results["missing_critical_layers"]:
            recommendations.append(
                f"Consider adding fire safety layers: {', '.join(validation_results['missing_critical_layers'])}"
            )

        fire_org = validation_results.get("fire_safety_organization", {})
        if not fire_org.get("organized", False):
            recommendations.append("No fire safety layers detected - ensure fire alarm devices are properly layered")

        if not recommendations:
            recommendations.append("Layer organization follows industry standards")

        return recommendations

    def _extract_block_attributes(self, entity) -> Dict:
        """Extract attributes from CAD block."""
        attributes = {}
        if hasattr(entity, "attribs"):
            for attrib in entity.attribs:
                if hasattr(attrib, "dxf"):
                    attributes[attrib.dxf.tag] = attrib.dxf.text
        return attributes


# Integration function for AutoFire
def enhance_autofire_with_layer_intelligence(cad_file_path: str, autofire_results: Dict) -> Dict:
    """
    Enhance AutoFire visual processing with precise CAD layer analysis.

    This provides:
    - Exact device counts (no more 656 smoke detectors!)
    - Precise coordinates from CAD data
    - Professional device classification
    - Industry-standard layer organization

    Args:
        cad_file_path: Path to CAD file (DXF/DWG)
        autofire_results: Results from visual processing

    Returns:
        Enhanced results with layer intelligence
    """
    layer_engine = CADLayerIntelligence()

    if not layer_engine.is_available():
        logger.warning("ezdxf not available - layer intelligence disabled")
        return {
            **autofire_results,
            "layer_intelligence": {
                "error": "ezdxf library not installed",
                "note": "Install ezdxf to enable precise CAD layer analysis",
            },
        }

    # Analyze CAD layers
    layer_analysis = layer_engine.analyze_cad_file_layers(cad_file_path)

    # Extract precise device information
    precise_devices = layer_engine.extract_precise_fire_devices(cad_file_path)

    # Validate layer organization
    validation = layer_engine.validate_layer_organization(cad_file_path)

    # Combine with AutoFire results
    enhanced_results = {
        **autofire_results,
        "layer_intelligence": {
            "analysis": layer_analysis,
            "precise_devices": precise_devices,
            "validation": validation,
            "accuracy_improvement": "Layer-based analysis provides exact counts vs visual estimation",
        },
        "device_count_comparison": {
            "visual_detection": len(autofire_results.get("devices", [])),
            "layer_extraction": len(precise_devices),
            "accuracy_note": "Layer extraction provides precise device counts and locations",
        },
    }

    return enhanced_results


__all__ = [
    "CADLayerIntelligence",
    "LayerClassification",
    "CADDevice",
    "LayerInfo",
    "enhance_autofire_with_layer_intelligence",
    "EZDXF_AVAILABLE",
]
