"""
AutoFire Construction Intelligence System
Core framework for analyzing complete construction sets and generating RFI materials
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class PageType(Enum):
    """Types of construction document pages"""

    FLOOR_PLAN = "floor_plan"
    FIRE_ALARM_PLAN = "fire_alarm_plan"
    ELECTRICAL_PLAN = "electrical_plan"
    SCHEDULE = "schedule"
    SPECIFICATIONS = "specifications"
    DETAILS = "details"
    COVER_SHEET = "cover_sheet"
    UNKNOWN = "unknown"


class DeviceType(Enum):
    """Low voltage system device types"""

    # Fire Alarm & Life Safety
    SMOKE_DETECTOR = "smoke_detector"
    HEAT_DETECTOR = "heat_detector"
    PULL_STATION = "pull_station"
    HORN_STROBE = "horn_strobe"
    SPEAKER = "speaker"
    CONTROL_MODULE = "control_module"
    MONITOR_MODULE = "monitor_module"
    PANEL = "panel"
    DUCT_DETECTOR = "duct_detector"
    BEAM_DETECTOR = "beam_detector"

    # Security & Access Control
    CARD_READER = "card_reader"
    KEYPAD = "keypad"
    MOTION_DETECTOR = "motion_detector"
    DOOR_CONTACT = "door_contact"
    GLASS_BREAK = "glass_break"
    CAMERA = "camera"
    INTERCOM = "intercom"
    PANIC_BUTTON = "panic_button"

    # Communications & Data
    PHONE = "phone"
    DATA_OUTLET = "data_outlet"
    WIRELESS_AP = "wireless_access_point"
    SWITCH = "network_switch"
    ROUTER = "router"
    PATCH_PANEL = "patch_panel"

    # Audio/Visual
    MICROPHONE = "microphone"
    AV_DISPLAY = "av_display"
    PROJECTOR = "projector"
    AV_CONTROL = "av_control"

    # Nurse Call & Healthcare
    NURSE_CALL_STATION = "nurse_call_station"
    EMERGENCY_CALL = "emergency_call"

    # Mass Notification
    OUTDOOR_SPEAKER = "outdoor_speaker"
    STROBE_BEACON = "strobe_beacon"
    SIREN = "siren"


class Priority(Enum):
    """Issue priority levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Room:
    """Architectural room definition"""

    name: str
    number: str | None
    area: float  # Square feet
    occupancy_type: str
    ceiling_height: float
    coordinates: List[tuple]  # Room boundary points


@dataclass
class FireAlarmDevice:
    """Fire alarm device from construction documents"""

    device_type: DeviceType
    location: tuple  # (x, y) coordinates
    model: str | None
    address: str | None
    circuit: str | None
    room: str | None
    notes: str | None


@dataclass
class Circuit:
    """Fire alarm circuit definition"""

    circuit_id: str
    circuit_type: str  # SLC, NAC, etc.
    wire_type: str
    devices: List[FireAlarmDevice]
    route_points: List[tuple]  # Wire routing coordinates


@dataclass
class FloorPlanAnalysis:
    """Analysis results from architectural floor plan"""

    sheet_number: str
    rooms: List[Room]
    dimensions: Dict[str, float]
    scale: str
    architectural_features: Dict[str, Any]
    coordinate_system: Dict[str, Any] | None


@dataclass
class FireAlarmAnalysis:
    """Analysis results from fire alarm plan"""

    sheet_number: str
    devices: List[FireAlarmDevice]
    circuits: List[Circuit]
    annotations: List[str]
    panel_locations: List[tuple]
    coverage_analysis: Dict[str, Any] | None


@dataclass
class ScheduleAnalysis:
    """Analysis results from device schedules"""

    sheet_number: str
    device_schedule: List[Dict[str, Any]]
    panel_schedule: List[Dict[str, Any]]
    specifications: Dict[str, str]


@dataclass
class ConstructionAnalysis:
    """Complete construction document analysis"""

    project_name: str
    analyzed_date: datetime
    pdf_path: str
    total_pages: int
    floor_plans: List[FloorPlanAnalysis]
    fire_alarm_plans: List[FireAlarmAnalysis]
    schedules: List[ScheduleAnalysis]
    specifications: List[Dict[str, Any]]

    @property
    def total_devices(self) -> int:
        """Total device count across all plans"""
        return sum(len(plan.devices) for plan in self.fire_alarm_plans)

    @property
    def total_building_area(self) -> float:
        """Total building area from floor plans"""
        return sum(sum(room.area for room in plan.rooms) for plan in self.floor_plans)


@dataclass
class RFIItem:
    """Request for Information item"""

    category: str
    description: str
    priority: Priority
    reference_drawing: str
    location: str | None
    suggested_resolution: str | None
    created_date: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        return {
            "category": self.category,
            "description": self.description,
            "priority": self.priority.value,
            "reference_drawing": self.reference_drawing,
            "location": self.location,
            "suggested_resolution": self.suggested_resolution,
            "created_date": self.created_date.isoformat(),
        }


@dataclass
class MaterialTakeoffItem:
    """Material takeoff line item"""

    item_type: str  # device, wire, conduit, etc.
    description: str
    model: str
    quantity: float
    unit: str
    location: str | None
    notes: str | None


@dataclass
class MaterialTakeoff:
    """Complete material takeoff"""

    project_name: str
    items: List[MaterialTakeoffItem]
    generated_date: datetime

    @property
    def device_count(self) -> int:
        """Total device count"""
        return sum(int(item.quantity) for item in self.items if item.item_type == "device")

    @property
    def wire_footage(self) -> float:
        """Total wire footage"""
        return sum(item.quantity for item in self.items if item.item_type == "wire")


@dataclass
class CostLineItem:
    """Cost estimate line item"""

    description: str
    quantity: float
    unit: str
    material_cost: float
    labor_hours: float
    labor_rate: float

    @property
    def material_total(self) -> float:
        return self.quantity * self.material_cost

    @property
    def labor_total(self) -> float:
        return self.labor_hours * self.labor_rate

    @property
    def total_cost(self) -> float:
        return self.material_total + self.labor_total


@dataclass
class CostEstimate:
    """Complete project cost estimate"""

    project_name: str
    line_items: List[CostLineItem]
    material_markup: float = 0.15
    overhead: float = 0.10
    profit: float = 0.08
    generated_date: datetime | None = None

    def __post_init__(self):
        if self.generated_date is None:
            self.generated_date = datetime.now()

    @property
    def subtotal_material(self) -> float:
        return sum(item.material_total for item in self.line_items)

    @property
    def subtotal_labor(self) -> float:
        return sum(item.labor_total for item in self.line_items)

    @property
    def subtotal(self) -> float:
        return self.subtotal_material + self.subtotal_labor

    @property
    def material_markup_amount(self) -> float:
        return self.subtotal_material * self.material_markup

    @property
    def overhead_amount(self) -> float:
        return self.subtotal * self.overhead

    @property
    def profit_amount(self) -> float:
        return (self.subtotal + self.material_markup_amount + self.overhead_amount) * self.profit

    @property
    def total_cost(self) -> float:
        return (
            self.subtotal + self.material_markup_amount + self.overhead_amount + self.profit_amount
        )


@dataclass
class ProjectIntelligence:
    """Executive-level project intelligence report"""

    project_name: str
    executive_summary: Dict[str, Any]
    technical_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    recommendations: List[str]
    generated_date: datetime

    def export_json(self, path: Path) -> None:
        """Export intelligence report as JSON"""
        data = {
            "project_name": self.project_name,
            "executive_summary": self.executive_summary,
            "technical_analysis": self.technical_analysis,
            "risk_assessment": self.risk_assessment,
            "cost_analysis": self.cost_analysis,
            "recommendations": self.recommendations,
            "generated_date": self.generated_date.isoformat(),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)


class ConstructionIntelligenceBase:
    """Base class for construction intelligence components"""

    def __init__(self):
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Setup logging for intelligence components"""
        import logging

        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(self.__class__.__name__)

    def log_analysis(self, message: str, level: str = "info"):
        """Log analysis progress"""
        getattr(self.logger, level)(f"🤖 AI Analysis: {message}")


# Factory functions for creating common objects
def create_rfi_item(
    category: str,
    description: str,
    priority: str,
    reference_drawing: str,
    location: str | None = None,
    suggested_resolution: str | None = None,
) -> RFIItem:
    """Factory function for creating RFI items"""
    return RFIItem(
        category=category,
        description=description,
        priority=Priority(priority.lower()),
        reference_drawing=reference_drawing,
        location=location,
        suggested_resolution=suggested_resolution,
        created_date=datetime.now(),
    )


def create_material_item(
    item_type: str, description: str, model: str, quantity: float, unit: str = "EA"
) -> MaterialTakeoffItem:
    """Factory function for creating material takeoff items"""
    return MaterialTakeoffItem(
        item_type=item_type,
        description=description,
        model=model,
        quantity=quantity,
        unit=unit,
        location=None,
        notes=None,
    )


def create_cost_line_item(
    description: str,
    quantity: float,
    material_cost: float,
    labor_hours: float,
    labor_rate: float = 75.0,
    unit: str = "EA",
) -> CostLineItem:
    """Factory function for creating cost estimate line items"""
    return CostLineItem(
        description=description,
        quantity=quantity,
        unit=unit,
        material_cost=material_cost,
        labor_hours=labor_hours,
        labor_rate=labor_rate,
    )


# Data validation functions
def validate_construction_analysis(analysis: ConstructionAnalysis) -> List[str]:
    """Validate construction analysis for completeness"""
    issues = []

    if not analysis.floor_plans:
        issues.append("No floor plans found in construction documents")

    if not analysis.fire_alarm_plans:
        issues.append("No fire alarm plans found in construction documents")

    if analysis.total_devices == 0:
        issues.append("No fire alarm devices found in plans")

    if analysis.total_building_area == 0:
        issues.append("Building area could not be determined")

    return issues


# Constants for fire alarm design
NFPA_72_SPACING = {
    DeviceType.SMOKE_DETECTOR: 30.0,  # 30 feet maximum spacing
    DeviceType.HEAT_DETECTOR: 50.0,  # 50 feet maximum spacing
}

DEVICE_COST_ESTIMATES = {
    DeviceType.SMOKE_DETECTOR: 85.0,
    DeviceType.HEAT_DETECTOR: 95.0,
    DeviceType.PULL_STATION: 45.0,
    DeviceType.HORN_STROBE: 120.0,
    DeviceType.SPEAKER: 150.0,
    DeviceType.CONTROL_MODULE: 95.0,
    DeviceType.MONITOR_MODULE: 85.0,
    DeviceType.PANEL: 2500.0,
}

INSTALLATION_LABOR_HOURS = {
    DeviceType.SMOKE_DETECTOR: 0.5,
    DeviceType.HEAT_DETECTOR: 0.5,
    DeviceType.PULL_STATION: 0.75,
    DeviceType.HORN_STROBE: 0.75,
    DeviceType.SPEAKER: 1.0,
    DeviceType.CONTROL_MODULE: 1.5,
    DeviceType.MONITOR_MODULE: 1.5,
    DeviceType.PANEL: 8.0,
}

# AI Floor Plan Processing exports
from .ai_floor_plan_processor import (
    AIFloorPlanProcessor,
    CoordinateReference,
    LowVoltageZone,
    SimpleCoordinateSystem,
    SimplifiedFloorPlan,
    StructuralElement,
    generate_complete_low_voltage_design,
    process_floor_plans_for_low_voltage,
)

# CAD Layer Intelligence exports
from .layer_intelligence import (
    CADDevice,
    CADLayerIntelligence,
    EZDXF_AVAILABLE,
    LayerClassification,
    LayerInfo,
    enhance_autofire_with_layer_intelligence,
)

__all__ = [
    # Core enums and data classes
    "PageType",
    "DeviceType",
    "Priority",
    "Room",
    "FireAlarmDevice",
    "Circuit",
    "FloorPlanAnalysis",
    "FireAlarmAnalysis",
    "ScheduleAnalysis",
    "ConstructionAnalysis",
    "RFIItem",
    "MaterialTakeoffItem",
    "MaterialTakeoff",
    "CostLineItem",
    "CostEstimate",
    "ProjectIntelligence",
    "ConstructionIntelligenceBase",
    # Processing functions
    "create_rfi_item",
    "create_material_item",
    "create_cost_line_item",
    "validate_construction_analysis",
    # Pricing data
    "INSTALLATION_LABOR_HOURS",
    # AI Floor Plan Processing
    "AIFloorPlanProcessor",
    "CoordinateReference",
    "StructuralElement",
    "LowVoltageZone",
    "SimpleCoordinateSystem",
    "SimplifiedFloorPlan",
    "process_floor_plans_for_low_voltage",
    "generate_complete_low_voltage_design",
    # CAD Layer Intelligence
    "CADLayerIntelligence",
    "LayerClassification",
    "CADDevice",
    "LayerInfo",
    "enhance_autofire_with_layer_intelligence",
    "EZDXF_AVAILABLE",
]
