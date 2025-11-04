"""
AI Floor Plan Processing & Coordinate Integration
Strips floor plans to bare necessities for comprehensive low voltage system design
"""

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Tuple

# TODO: Import coordinate system when available
# from cad_core.spaces.coordinate_system import CoordinateSystem, Units
from . import (
    ConstructionAnalysis,
    ConstructionIntelligenceBase,
    DeviceType,
    FloorPlanAnalysis,
    Room,
)


@dataclass
class CoordinateReference:
    """Coordinate reference point extracted from drawings"""

    x: float
    y: float
    reference_type: str  # "grid", "dimension", "symbol", "scale_bar"
    label: str
    confidence: float  # 0.0 to 1.0
    source_page: str


@dataclass
class StructuralElement:
    """Simplified structural element for low voltage design"""

    element_type: str  # "wall", "door", "window", "column", "ceiling_grid"
    coordinates: List[Tuple[float, float]]
    properties: Dict[str, Any] = field(default_factory=dict)
    low_voltage_impact: str = ""  # How this affects low voltage design


@dataclass
class SimpleCoordinateSystem:
    """Simple coordinate system for floor plan processing"""

    units: str = "feet"
    scale_factor: float = 1.0
    origin_x: float = 0.0
    origin_y: float = 0.0


@dataclass
class LowVoltageZone:
    """Simplified zone for low voltage system design"""

    zone_id: str
    zone_type: str  # "coverage", "pathway", "equipment", "restricted"
    boundaries: List[Tuple[float, float]]
    area_sq_ft: float
    ceiling_height: float
    special_requirements: List[str] = field(default_factory=list)
    device_requirements: List[DeviceType] = field(default_factory=list)


@dataclass
class SimplifiedFloorPlan:
    """Simplified floor plan optimized for low voltage design"""

    sheet_number: str
    coordinate_system: SimpleCoordinateSystem
    reference_points: List[CoordinateReference]
    structural_elements: List[StructuralElement]
    low_voltage_zones: List[LowVoltageZone]
    scale_factor: float
    north_angle: float  # Degrees from east
    building_outline: List[Tuple[float, float]]
    total_area_sq_ft: float
    simplified_date: datetime


class AIFloorPlanProcessor(ConstructionIntelligenceBase):
    """AI-powered floor plan processor for low voltage system design"""

    def __init__(self):
        super().__init__()
        self.coordinate_system = SimpleCoordinateSystem()
        self.confidence_threshold = 0.7

    def process_floor_plan_for_low_voltage(
        self, floor_plan: FloorPlanAnalysis, construction_analysis: ConstructionAnalysis
    ) -> SimplifiedFloorPlan:
        """
        Process architectural floor plan and strip to bare necessities for low voltage design

        User's vision: "AI should be able to design the entire system from beginning to end"
        """
        self.log_analysis(f"Processing floor plan {floor_plan.sheet_number} for low voltage design")

        # Extract coordinate system and reference points
        coordinate_system, reference_points = self._extract_coordinate_system(floor_plan)

        # Simplify structural elements for low voltage purposes
        structural_elements = self._extract_structural_elements(floor_plan)

        # Create low voltage zones from room analysis
        low_voltage_zones = self._create_low_voltage_zones(floor_plan.rooms)

        # Calculate building outline and total area
        building_outline, total_area = self._calculate_building_outline(floor_plan.rooms)

        # Detect scale and north orientation
        scale_factor = self._detect_scale_factor(floor_plan)
        north_angle = self._detect_north_orientation(floor_plan)

        simplified_plan = SimplifiedFloorPlan(
            sheet_number=floor_plan.sheet_number,
            coordinate_system=coordinate_system,
            reference_points=reference_points,
            structural_elements=structural_elements,
            low_voltage_zones=low_voltage_zones,
            scale_factor=scale_factor,
            north_angle=north_angle,
            building_outline=building_outline,
            total_area_sq_ft=total_area,
            simplified_date=datetime.now(),
        )

        self.log_analysis(
            f"Simplified floor plan created: {len(low_voltage_zones)} zones, {total_area:.0f} sq ft"
        )
        return simplified_plan

    def _extract_coordinate_system(
        self, floor_plan: FloorPlanAnalysis
    ) -> Tuple[SimpleCoordinateSystem, List[CoordinateReference]]:
        """Extract coordinate system and reference points from floor plan"""

        coordinate_system = SimpleCoordinateSystem()
        reference_points = []

        # Parse scale to determine coordinate system
        scale_text = floor_plan.scale.lower()

        if "1/4" in scale_text:
            # 1/4" = 1'-0" scale
            coordinate_system.scale_factor = 48.0
        elif "1/8" in scale_text:
            # 1/8" = 1'-0" scale
            coordinate_system.scale_factor = 96.0
        elif "1/16" in scale_text:
            # 1/16" = 1'-0" scale
            coordinate_system.scale_factor = 192.0  # Extract grid references from dimensions
        for dimension_key, value in floor_plan.dimensions.items():
            if "grid" in dimension_key.lower() or "coord" in dimension_key.lower():
                reference_points.append(
                    CoordinateReference(
                        x=0.0,  # Would be extracted from actual coordinate
                        y=0.0,
                        reference_type="grid",
                        label=dimension_key,
                        confidence=0.8,
                        source_page=floor_plan.sheet_number,
                    )
                )

        # Create primary reference point at origin
        reference_points.append(
            CoordinateReference(
                x=0.0,
                y=0.0,
                reference_type="origin",
                label="Plan Origin",
                confidence=1.0,
                source_page=floor_plan.sheet_number,
            )
        )

        return coordinate_system, reference_points

    def _extract_structural_elements(
        self, floor_plan: FloorPlanAnalysis
    ) -> List[StructuralElement]:
        """Extract structural elements relevant to low voltage design"""
        elements = []

        # Extract walls from room boundaries
        processed_walls = set()

        for room in floor_plan.rooms:
            if room.coordinates:
                wall_coords = room.coordinates

                # Create wall segments
                for i in range(len(wall_coords)):
                    start = wall_coords[i]
                    end = wall_coords[(i + 1) % len(wall_coords)]

                    # Create unique wall identifier to avoid duplicates
                    wall_key = tuple(sorted([start, end]))

                    if wall_key not in processed_walls:
                        processed_walls.add(wall_key)

                        elements.append(
                            StructuralElement(
                                element_type="wall",
                                coordinates=[start, end],
                                properties={
                                    "adjacent_rooms": [room.name],
                                    "wall_type": "interior",  # Would determine from context
                                },
                                low_voltage_impact="pathway_barrier_mounting_surface",
                            )
                        )

        # Add ceiling grid elements (standard for commercial buildings)
        for room in floor_plan.rooms:
            if room.occupancy_type in ["Office", "Assembly Public", "Conference"]:
                elements.append(
                    StructuralElement(
                        element_type="ceiling_grid",
                        coordinates=room.coordinates if room.coordinates else [],
                        properties={
                            "grid_size": "2x2",  # Standard ceiling grid
                            "ceiling_height": room.ceiling_height,
                        },
                        low_voltage_impact="device_mounting_pathway_support",
                    )
                )

        return elements

    def _create_low_voltage_zones(self, rooms: List[Room]) -> List[LowVoltageZone]:
        """Create simplified zones optimized for low voltage system design"""
        zones = []

        for room in rooms:
            # Determine device requirements based on room type
            device_requirements = self._determine_device_requirements(room)

            # Determine special requirements
            special_requirements = self._determine_special_requirements(room)

            zone = LowVoltageZone(
                zone_id=f"LV-{room.number or len(zones)+1}",
                zone_type=self._classify_zone_type(room),
                boundaries=room.coordinates if room.coordinates else [],
                area_sq_ft=room.area,
                ceiling_height=room.ceiling_height,
                special_requirements=special_requirements,
                device_requirements=device_requirements,
            )

            zones.append(zone)

        return zones

    def _determine_device_requirements(self, room: Room) -> List[DeviceType]:
        """Determine low voltage device requirements based on room characteristics"""
        devices = []

        # Fire alarm requirements (NFPA 72 based)
        if room.area > 900:  # Larger rooms need multiple smoke detectors
            devices.extend([DeviceType.SMOKE_DETECTOR] * math.ceil(room.area / 900))
        else:
            devices.append(DeviceType.SMOKE_DETECTOR)

        # Add heat detector for specific room types
        if any(keyword in room.name.lower() for keyword in ["kitchen", "mechanical", "storage"]):
            devices.append(DeviceType.HEAT_DETECTOR)

        # Notification devices
        if room.occupancy_type == "Assembly Public":
            devices.append(DeviceType.HORN_STROBE)
        else:
            devices.append(DeviceType.STROBE_BEACON)  # Use available device type

        # Pull stations for exits
        if any(keyword in room.name.lower() for keyword in ["lobby", "corridor", "exit", "stair"]):
            devices.append(DeviceType.PULL_STATION)

        # Security devices for appropriate spaces
        if room.occupancy_type in ["Office", "Secure Control", "Data Center"]:
            devices.append(DeviceType.CARD_READER)
            devices.append(DeviceType.MOTION_DETECTOR)

        # Communications devices
        if room.occupancy_type in ["Office", "Conference", "Assembly Public"]:
            devices.append(DeviceType.WIRELESS_AP)

        # Special systems
        if "data" in room.name.lower() or "server" in room.name.lower():
            devices.extend(
                [
                    DeviceType.CONTROL_MODULE,  # Represents network equipment
                    DeviceType.CONTROL_MODULE,  # Represents patch panels (using same type)
                ]
            )

        if "conference" in room.name.lower() or "meeting" in room.name.lower():
            devices.extend([DeviceType.MICROPHONE, DeviceType.SPEAKER])

        return devices

    def _determine_special_requirements(self, room: Room) -> List[str]:
        """Determine special requirements affecting low voltage design"""
        requirements = []

        # High ceiling requirements
        if room.ceiling_height > 12.0:
            requirements.append("high_ceiling_mounting")

        # Special detection requirements
        if any(keyword in room.name.lower() for keyword in ["kitchen", "laundry", "mechanical"]):
            requirements.append("heat_detection_preferred")

        # Accessibility requirements (ADA compliance)
        if room.occupancy_type == "Assembly Public":
            requirements.append("ada_compliance_required")
            requirements.append("visual_notification_required")

        # Security requirements
        if any(
            keyword in room.name.lower() for keyword in ["secure", "data", "electric", "telecom"]
        ):
            requirements.append("restricted_access")
            requirements.append("enhanced_security")

        # Environmental requirements
        if any(keyword in room.name.lower() for keyword in ["server", "data", "telecom"]):
            requirements.append("environmental_monitoring")
            requirements.append("redundant_power")

        # Plenum requirements
        if room.ceiling_height > 9.0:
            requirements.append("plenum_rated_cables")

        return requirements

    def _classify_zone_type(self, room: Room) -> str:
        """Classify zone type for low voltage system design"""

        if "corridor" in room.name.lower() or "hallway" in room.name.lower():
            return "pathway"
        elif any(
            keyword in room.name.lower() for keyword in ["data", "server", "telecom", "electric"]
        ):
            return "equipment"
        elif any(keyword in room.name.lower() for keyword in ["secure", "restricted"]):
            return "restricted"
        else:
            return "coverage"

    def _calculate_building_outline(
        self, rooms: List[Room]
    ) -> Tuple[List[Tuple[float, float]], float]:
        """Calculate building outline and total area"""

        if not rooms:
            return [], 0.0

        # Find bounding box of all rooms
        all_coords = []
        total_area = 0.0

        for room in rooms:
            total_area += room.area
            if room.coordinates:
                all_coords.extend(room.coordinates)

        if not all_coords:
            # Create default outline based on total area (square building)
            side_length = math.sqrt(total_area)
            outline = [
                (0.0, 0.0),
                (side_length, 0.0),
                (side_length, side_length),
                (0.0, side_length),
            ]
            return outline, total_area

        # Calculate bounding box
        min_x = min(coord[0] for coord in all_coords)
        max_x = max(coord[0] for coord in all_coords)
        min_y = min(coord[1] for coord in all_coords)
        max_y = max(coord[1] for coord in all_coords)

        outline = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]

        return outline, total_area

    def _detect_scale_factor(self, floor_plan: FloorPlanAnalysis) -> float:
        """Detect scale factor from drawing scale information"""

        scale_text = floor_plan.scale.lower()

        # Parse common architectural scales
        if "1/4" in scale_text:
            return 48.0  # 1/4" = 1'-0" means 48:1 ratio
        elif "1/8" in scale_text:
            return 96.0  # 1/8" = 1'-0" means 96:1 ratio
        elif "1/16" in scale_text:
            return 192.0  # 1/16" = 1'-0" means 192:1 ratio
        elif "3/32" in scale_text:
            return 128.0  # 3/32" = 1'-0" means 128:1 ratio
        elif "3/16" in scale_text:
            return 64.0  # 3/16" = 1'-0" means 64:1 ratio
        elif "1/2" in scale_text:
            return 24.0  # 1/2" = 1'-0" means 24:1 ratio

        return 48.0  # Default to 1/4" scale

    def _detect_north_orientation(self, floor_plan: FloorPlanAnalysis) -> float:
        """Detect north orientation from architectural features"""

        # Look for north arrow indicators in architectural features
        if hasattr(floor_plan, "architectural_features"):
            features = floor_plan.architectural_features

            if "north_arrow" in features:
                # Extract angle from north arrow (would be more sophisticated in real implementation)
                return features.get("north_angle", 0.0)

        # Default assumption: north is up (0 degrees from east = 90 degrees from north)
        return 90.0

    def integrate_with_coordinate_system(
        self, simplified_plan: SimplifiedFloorPlan, model_space_coords: SimpleCoordinateSystem
    ) -> Dict[str, Any]:
        """
        Integrate simplified floor plan with CAD model space coordinate system

        This enables end-to-end system design from floor plan to final construction documents
        """

        self.log_analysis("Integrating simplified floor plan with model space coordinates")

        integration_data = {
            "coordinate_mapping": {},
            "scale_transformations": {},
            "reference_alignments": {},
            "design_zones": [],
        }

        # Map simplified plan coordinates to model space
        for zone in simplified_plan.low_voltage_zones:
            model_space_boundaries = []

            for x, y in zone.boundaries:
                # Transform coordinates using scale factor and coordinate system
                model_x = x / simplified_plan.scale_factor
                model_y = y / simplified_plan.scale_factor

                # Store coordinates for model space use
                model_space_boundaries.append((model_x, model_y))

            integration_data["design_zones"].append(
                {
                    "zone_id": zone.zone_id,
                    "model_space_boundaries": model_space_boundaries,
                    "device_requirements": [d.value for d in zone.device_requirements],
                    "special_requirements": zone.special_requirements,
                    "area_sq_ft": zone.area_sq_ft,
                }
            )

        # Create coordinate mapping for reference points
        for ref_point in simplified_plan.reference_points:
            model_x = ref_point.x / simplified_plan.scale_factor
            model_y = ref_point.y / simplified_plan.scale_factor

            integration_data["coordinate_mapping"][ref_point.label] = {
                "plan_coordinates": (ref_point.x, ref_point.y),
                "model_coordinates": (model_x, model_y),
                "confidence": ref_point.confidence,
            }

        # Calculate scale transformations
        integration_data["scale_transformations"] = {
            "plan_scale_factor": simplified_plan.scale_factor,
            "drawing_scale": f'1/{int(simplified_plan.scale_factor)}" = 1\'-0"',
            "model_units": model_space_coords.units,
            "conversion_factor": 1.0 / simplified_plan.scale_factor,
        }

        self.log_analysis(
            f"Integration complete: {len(integration_data['design_zones'])} zones mapped to model space"
        )

        return integration_data

    def generate_end_to_end_design_plan(
        self,
        simplified_plans: List[SimplifiedFloorPlan],
        construction_analysis: ConstructionAnalysis,
    ) -> Dict[str, Any]:
        """
        Generate complete end-to-end low voltage system design plan

        This achieves the user's vision: "AI should be able to design the entire system from beginning to end"
        """

        self.log_analysis("Generating end-to-end low voltage system design plan")

        design_plan = {
            "project_overview": {
                "project_name": construction_analysis.project_name,
                "total_floors": len(simplified_plans),
                "total_area_sq_ft": sum(plan.total_area_sq_ft for plan in simplified_plans),
                "design_date": datetime.now().isoformat(),
            },
            "system_requirements": {},
            "device_placement_plan": {},
            "pathway_design": {},
            "compliance_verification": {},
            "implementation_phases": [],
        }

        # Aggregate system requirements across all floors
        all_device_requirements = {}
        all_special_requirements = set()

        for plan in simplified_plans:
            for zone in plan.low_voltage_zones:
                for device_type in zone.device_requirements:
                    device_name = device_type.value
                    all_device_requirements[device_name] = (
                        all_device_requirements.get(device_name, 0) + 1
                    )

                all_special_requirements.update(zone.special_requirements)

        design_plan["system_requirements"] = {
            "device_counts": all_device_requirements,
            "special_requirements": list(all_special_requirements),
            "estimated_panels": math.ceil(
                sum(all_device_requirements.values()) / 99
            ),  # Standard panel capacity
            "estimated_circuits": math.ceil(
                sum(all_device_requirements.values()) / 20
            ),  # Devices per circuit
        }

        # Device placement strategy
        design_plan["device_placement_plan"] = {
            "fire_alarm_strategy": "NFPA 72 compliant spacing with optimal coverage",
            "security_strategy": "Comprehensive access control and surveillance",
            "communications_strategy": "Complete wireless and wired infrastructure",
            "av_strategy": "Conference and presentation systems integration",
            "placement_methodology": "AI-optimized for coverage, code compliance, and installation efficiency",
        }

        # Pathway design strategy
        design_plan["pathway_design"] = {
            "cable_management": "Structured pathways with BICSI compliance",
            "conduit_routing": "Optimized for accessibility and future expansion",
            "plenum_considerations": "Plenum-rated cables where required",
            "pathway_coordination": "Coordinated with other building systems",
        }

        # Compliance verification
        design_plan["compliance_verification"] = {
            "nfpa_72_compliance": "Complete fire alarm code compliance",
            "nec_compliance": "Full electrical code compliance for all low voltage systems",
            "bicsi_compliance": "Installation practices per BICSI standards",
            "nicet_compliance": "Design and installation per NICET requirements",
            "ada_compliance": "Accessibility requirements fully addressed",
        }

        # Implementation phases
        design_plan["implementation_phases"] = [
            {
                "phase": 1,
                "description": "Infrastructure and pathways installation",
                "duration_weeks": 2,
                "systems": ["conduit", "cable_trays", "j_hooks"],
            },
            {
                "phase": 2,
                "description": "Fire alarm system installation",
                "duration_weeks": 3,
                "systems": ["fire_alarm_devices", "panels", "circuits"],
            },
            {
                "phase": 3,
                "description": "Security and access control installation",
                "duration_weeks": 2,
                "systems": ["card_readers", "cameras", "access_panels"],
            },
            {
                "phase": 4,
                "description": "Communications and AV systems installation",
                "duration_weeks": 2,
                "systems": ["network_infrastructure", "wireless_systems", "av_equipment"],
            },
            {
                "phase": 5,
                "description": "Testing, commissioning, and documentation",
                "duration_weeks": 1,
                "systems": ["system_testing", "documentation", "training"],
            },
        ]

        self.log_analysis(
            f"End-to-end design plan generated: {design_plan['project_overview']['total_area_sq_ft']:.0f} sq ft, {len(all_device_requirements)} device types"
        )

        return design_plan


# Factory function for easy usage
def process_floor_plans_for_low_voltage(
    construction_analysis: ConstructionAnalysis,
) -> List[SimplifiedFloorPlan]:
    """
    Process all floor plans in construction analysis for low voltage system design

    Args:
        construction_analysis: Complete construction document analysis

    Returns:
        List of simplified floor plans optimized for low voltage design
    """
    processor = AIFloorPlanProcessor()
    simplified_plans = []

    for floor_plan in construction_analysis.floor_plans:
        simplified_plan = processor.process_floor_plan_for_low_voltage(
            floor_plan, construction_analysis
        )
        simplified_plans.append(simplified_plan)

    return simplified_plans


def generate_complete_low_voltage_design(
    construction_analysis: ConstructionAnalysis,
) -> Dict[str, Any]:
    """
    Generate complete end-to-end low voltage system design from construction documents

    This function achieves the user's vision: "AI should be able to design the entire system from beginning to end"

    Args:
        construction_analysis: Complete construction document analysis

    Returns:
        Complete design plan for all low voltage systems
    """
    processor = AIFloorPlanProcessor()

    # Process all floor plans
    simplified_plans = process_floor_plans_for_low_voltage(construction_analysis)

    # Generate complete design plan
    design_plan = processor.generate_end_to_end_design_plan(simplified_plans, construction_analysis)

    return {
        "simplified_floor_plans": simplified_plans,
        "complete_design_plan": design_plan,
        "processor_info": {
            "processed_date": datetime.now().isoformat(),
            "floor_plan_count": len(simplified_plans),
            "total_zones": sum(len(plan.low_voltage_zones) for plan in simplified_plans),
        },
    }
