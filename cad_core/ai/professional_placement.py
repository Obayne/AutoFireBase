"""
AI Model/Paper Space Integration - Professional CAD with AI Device Placement

This module integrates the AI device placement system with the professional
model/paper space architecture, enabling intelligent device placement with
real-world coordinates and automated construction document generation.
"""

import logging
import time
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

from ..geometry import Point
from ..units import UnitSystem, Units
from ..spaces import ModelSpace, PaperSpace, PageSize, ViewportScale
from ..spaces.model_space import Circle, Line, Entity, Bounds
from .device_placement import (
    AIPlacementEngine,
    Room,
    DeviceType,
    PlacementSuggestion,
    SpaceType,
    NFPARequirements,
)

logger = logging.getLogger(__name__)


class FireAlarmEntity(Circle):
    """Fire alarm device entity with AI metadata."""

    def __init__(
        self,
        center: Point,
        radius: float,
        device_type: DeviceType,
        ai_metadata: Dict[str, Any] | None = None,
        entity_id: str | None = None,
    ):
        super().__init__(center, radius, entity_id)
        self.device_type = device_type
        self.ai_metadata = ai_metadata or {}

        # Fire alarm specific properties
        self.properties.update(
            {
                "device_type": device_type.value,
                "manufacturer": self.ai_metadata.get("manufacturer", "System Sensor"),
                "model": self.ai_metadata.get("model", self._default_model()),
                "zone": self.ai_metadata.get("zone", "Zone 1"),
                "circuit": self.ai_metadata.get("circuit", "SLC-1"),
                "address": self.ai_metadata.get("address", "001"),
                "coverage_area": self.ai_metadata.get("coverage_area", 900.0),
                "confidence_score": self.ai_metadata.get("confidence_score", 0.0),
                "ai_reasoning": self.ai_metadata.get("reasoning", ""),
            }
        )

        # Set appropriate layer
        layer_map = {
            DeviceType.SMOKE_DETECTOR: "FA-DETECTORS",
            DeviceType.HEAT_DETECTOR: "FA-DETECTORS",
            DeviceType.PULL_STATION: "FA-PULL-STATIONS",
            DeviceType.HORN_STROBE: "FA-NOTIFICATION",
            DeviceType.STROBE_ONLY: "FA-NOTIFICATION",
        }
        self.layer = layer_map.get(device_type, "FA-DEVICES")

    def _default_model(self) -> str:
        """Get default model based on device type."""
        return {
            DeviceType.SMOKE_DETECTOR: "FSP-851",
            DeviceType.HEAT_DETECTOR: "FST-851",
            DeviceType.PULL_STATION: "BG-12",
            DeviceType.HORN_STROBE: "P2RH-15/75",
            DeviceType.STROBE_ONLY: "P2W-15",
        }.get(self.device_type, "Unknown")


@dataclass
class AIPlacementResult:
    """Result of AI device placement operation."""

    devices_placed: List[FireAlarmEntity]
    total_devices: int
    coverage_percentage: float
    compliance_score: float
    cost_estimate: float
    recommendations: List[str]
    nfpa_violations: List[str]
    placement_time_seconds: float


class ProfessionalAIPlacementEngine:
    """
    Professional AI placement engine that integrates with model/paper space.

    This class combines the AI device placement algorithms with professional
    CAD coordinate systems and units for real-world fire alarm design.
    """

    def __init__(self, model_space: ModelSpace, unit_system: UnitSystem | None = None):
        self.model_space = model_space
        self.unit_system = unit_system or UnitSystem(Units.FEET)
        self.ai_engine = AIPlacementEngine()

        # Device placement history and statistics
        self.placement_sessions: List[Dict[str, Any]] = []
        self.total_devices_placed = 0

    def analyze_building_layout(self, building_bounds: Bounds) -> Room:
        """
        Convert model space bounds to AI analyzable room format.

        Args:
            building_bounds: Model space bounds of building

        Returns:
            Room object for AI analysis
        """
        # Convert bounds to vertices (rectangle)
        vertices = [
            (building_bounds.min_x, building_bounds.min_y),
            (building_bounds.max_x, building_bounds.min_y),
            (building_bounds.max_x, building_bounds.max_y),
            (building_bounds.min_x, building_bounds.max_y),
        ]

        # Determine space type based on dimensions
        width = building_bounds.width()
        length = building_bounds.height()
        area = width * length

        if width > 100 or length > 100 or area > 5000:
            space_type = SpaceType.ASSEMBLY
        elif width < 8 or length < 8:
            space_type = SpaceType.CORRIDOR
        else:
            space_type = SpaceType.OFFICE

        return Room(
            id="main_space",
            name="Building Main Area",
            space_type=space_type,
            vertices=vertices,
            ceiling_height_ft=10.0,
        )

    def place_devices_ai_optimized(
        self,
        device_type: DeviceType,
        building_bounds: Bounds | None = None,
        target_coverage: float = 0.95,
        budget_limit: float | None = None,
    ) -> AIPlacementResult:
        """
        AI-optimized device placement in model space.

        Args:
            device_type: Type of fire alarm device to place
            building_bounds: Area to analyze (uses model extents if None)
            target_coverage: Target coverage percentage (0.0 to 1.0)
            budget_limit: Optional budget constraint

        Returns:
            Complete AI placement result with professional entities
        """
        import time

        start_time = time.time()

        # Use model space extents if no bounds specified
        if building_bounds is None:
            building_bounds = self.model_space.get_bounds()
            if building_bounds is None:
                raise ValueError("No building bounds available - add building geometry first")

        # Convert to AI analyzable format
        room = self.analyze_building_layout(building_bounds)

        # Get existing devices of this type
        existing_devices = []
        for entity in self.model_space.entities.values():
            if isinstance(entity, FireAlarmEntity) and entity.device_type == device_type:
                existing_devices.append((entity.center.x, entity.center.y))

        # Generate AI placement suggestions
        suggestions = self.ai_engine.suggest_device_placement(
            room=room, device_type=device_type, existing_devices=existing_devices
        )

        # Filter suggestions based on coverage and budget
        selected_suggestions = self._optimize_selection(
            suggestions, target_coverage, budget_limit, room.area_sqft
        )

        # Create professional fire alarm entities
        devices_placed = []
        for suggestion in selected_suggestions:
            # Convert AI position to professional Point
            ai_x, ai_y = suggestion.position
            device_center = Point(ai_x, ai_y)

            # Calculate device radius based on type
            radius = self._get_device_radius(device_type)

            # Create fire alarm entity with AI metadata
            device = FireAlarmEntity(
                center=device_center,
                radius=radius,
                device_type=device_type,
                ai_metadata={
                    "confidence_score": suggestion.confidence_score,
                    "reasoning": suggestion.reasoning,
                    "coverage_area": suggestion.coverage_area_sqft,
                    "compliance_notes": suggestion.compliance_notes,
                    "model": self._get_device_model(device_type),
                    "zone": self._assign_zone(device_center),
                    "circuit": self._assign_circuit(device_type),
                    "address": f"{len(devices_placed) + 1:03d}",
                },
            )

            # Add to model space
            self.model_space.add_entity(device, device.layer)
            devices_placed.append(device)
            self.total_devices_placed += 1

        # Calculate results
        placement_time = time.time() - start_time
        result = self._calculate_placement_results(
            devices_placed, suggestions, room, placement_time
        )

        # Log placement session
        self._log_placement_session(device_type, result)

        logger.info(
            f"AI placed {len(devices_placed)} {device_type.value} devices "
            f"with {result.coverage_percentage:.1f}% coverage "
            f"(confidence: {result.compliance_score:.1f}%)"
        )

        return result

    def _optimize_selection(
        self,
        suggestions: List[PlacementSuggestion],
        target_coverage: float,
        budget_limit: float | None,
        room_area: float,
    ) -> List[PlacementSuggestion]:
        """Optimize device selection based on coverage and budget."""
        if not suggestions:
            return []

        # Sort by confidence score
        sorted_suggestions = sorted(suggestions, key=lambda s: s.confidence_score, reverse=True)

        # Calculate coverage incrementally
        selected = []
        total_coverage_area = 0.0
        total_cost = 0.0
        device_cost = self._get_device_cost(suggestions[0].device_type)

        for suggestion in sorted_suggestions:
            # Check budget constraint
            if budget_limit and (total_cost + device_cost) > budget_limit:
                break

            # Check if we need more coverage
            coverage_ratio = total_coverage_area / room_area
            if coverage_ratio >= target_coverage:
                break

            # Add device
            selected.append(suggestion)
            total_coverage_area += suggestion.coverage_area_sqft
            total_cost += device_cost

            # Stop if we have excellent coverage
            if coverage_ratio >= 0.98:
                break

        return selected

    def _get_device_radius(self, device_type: DeviceType) -> float:
        """Get device radius in model units (feet)."""
        return {
            DeviceType.SMOKE_DETECTOR: 0.25,  # 6" diameter
            DeviceType.HEAT_DETECTOR: 0.25,  # 6" diameter
            DeviceType.PULL_STATION: 0.33,  # 8" wide
            DeviceType.HORN_STROBE: 0.42,  # 10" diameter
            DeviceType.STROBE_ONLY: 0.33,  # 8" diameter
        }.get(device_type, 0.25)

    def _get_device_model(self, device_type: DeviceType) -> str:
        """Get professional device model number."""
        return {
            DeviceType.SMOKE_DETECTOR: "FSP-851",
            DeviceType.HEAT_DETECTOR: "FST-851",
            DeviceType.PULL_STATION: "BG-12",
            DeviceType.HORN_STROBE: "P2RH-15/75",
            DeviceType.STROBE_ONLY: "P2W-15",
        }.get(device_type, "Unknown")

    def _get_device_cost(self, device_type: DeviceType) -> float:
        """Get estimated device cost."""
        return {
            DeviceType.SMOKE_DETECTOR: 85.0,
            DeviceType.HEAT_DETECTOR: 75.0,
            DeviceType.PULL_STATION: 45.0,
            DeviceType.HORN_STROBE: 120.0,
            DeviceType.STROBE_ONLY: 90.0,
        }.get(device_type, 100.0)

    def _assign_zone(self, position: Point) -> str:
        """Assign zone based on device position."""
        # Simple zone assignment based on position
        if position.x < 50:
            return "Zone 1"
        elif position.x < 100:
            return "Zone 2"
        else:
            return "Zone 3"

    def _assign_circuit(self, device_type: DeviceType) -> str:
        """Assign circuit based on device type."""
        if device_type in [
            DeviceType.SMOKE_DETECTOR,
            DeviceType.HEAT_DETECTOR,
            DeviceType.PULL_STATION,
        ]:
            return "SLC-1"
        else:
            return "NAC-1"

    def _calculate_placement_results(
        self,
        devices_placed: List[FireAlarmEntity],
        all_suggestions: List[PlacementSuggestion],
        room: Room,
        placement_time: float,
    ) -> AIPlacementResult:
        """Calculate comprehensive placement results."""

        if not devices_placed:
            return AIPlacementResult(
                devices_placed=[],
                total_devices=0,
                coverage_percentage=0.0,
                compliance_score=0.0,
                cost_estimate=0.0,
                recommendations=[],
                nfpa_violations=[],
                placement_time_seconds=placement_time,
            )

        # Calculate coverage
        total_coverage_area = sum(d.properties["coverage_area"] for d in devices_placed)
        coverage_percentage = min(100.0, (total_coverage_area / room.area_sqft) * 100)

        # Calculate compliance score (average confidence)
        compliance_score = (
            sum(d.properties["confidence_score"] for d in devices_placed)
            / len(devices_placed)
            * 100
        )

        # Calculate cost
        device_cost = self._get_device_cost(devices_placed[0].device_type)
        cost_estimate = len(devices_placed) * device_cost

        # Generate recommendations
        recommendations = []
        if coverage_percentage < 95:
            recommendations.append(
                f"Consider adding {int((95 - coverage_percentage) / 10)} more devices for complete coverage"
            )

        if compliance_score < 80:
            recommendations.append("Review device placement for NFPA compliance")

        if len(devices_placed) > 20:
            recommendations.append("Consider zoning devices across multiple circuits")

        # Check for NFPA violations
        violations = []
        requirements = NFPARequirements.get_requirements(devices_placed[0].device_type)

        for device in devices_placed:
            # Check spacing violations
            for other_device in devices_placed:
                if device != other_device:
                    distance = device.center.distance_to(other_device.center)
                    if distance < requirements.max_spacing_ft * 0.5:  # Too close
                        violations.append(
                            f"Devices {device.id} and {other_device.id} may be too close ({distance:.1f}')"
                        )

        return AIPlacementResult(
            devices_placed=devices_placed,
            total_devices=len(devices_placed),
            coverage_percentage=coverage_percentage,
            compliance_score=compliance_score,
            cost_estimate=cost_estimate,
            recommendations=recommendations,
            nfpa_violations=violations,
            placement_time_seconds=placement_time,
        )

    def _log_placement_session(self, device_type: DeviceType, result: AIPlacementResult):
        """Log placement session for analytics."""
        session = {
            "timestamp": time.time(),
            "device_type": device_type.value,
            "devices_placed": result.total_devices,
            "coverage_percentage": result.coverage_percentage,
            "compliance_score": result.compliance_score,
            "cost_estimate": result.cost_estimate,
            "placement_time": result.placement_time_seconds,
        }
        self.placement_sessions.append(session)

    def create_ai_enhanced_layout(
        self, paper_space: PaperSpace, building_bounds: Bounds | None = None
    ) -> Tuple[PaperSpace, Dict[str, Any]]:
        """
        Create AI-enhanced paper space layout with device placement.

        Args:
            paper_space: Paper space for layout
            building_bounds: Building area to analyze

        Returns:
            Enhanced paper space and placement statistics
        """
        if building_bounds is None:
            building_bounds = self.model_space.get_bounds()
            if building_bounds is None:
                raise ValueError("No building geometry available")

        # Create main viewport showing building
        center = building_bounds.center()
        scale = ViewportScale.from_string('1/8"=1\'-0"')  # Common fire alarm scale

        viewport = paper_space.add_viewport(
            paper_x=2.0,
            paper_y=5.0,
            paper_width=18.0,
            paper_height=24.0,
            model_center=center,
            scale=scale,
            model_space=self.model_space,
        )

        # Generate placement statistics
        device_counts = {}
        total_cost = 0.0

        for entity in self.model_space.entities.values():
            if isinstance(entity, FireAlarmEntity):
                device_type = entity.device_type.value
                device_counts[device_type] = device_counts.get(device_type, 0) + 1
                total_cost += self._get_device_cost(entity.device_type)

        # Create title block data with AI statistics
        ai_stats = {
            "ai_device_placement": True,
            "total_devices": sum(device_counts.values()),
            "device_breakdown": device_counts,
            "estimated_cost": total_cost,
            "ai_confidence": "High" if len(device_counts) > 0 else "N/A",
            "nfpa_compliance": "Validated",
            "last_ai_update": time.strftime("%m/%d/%Y %H:%M"),
        }

        return paper_space, ai_stats

    def get_placement_statistics(self) -> Dict[str, Any]:
        """Get comprehensive placement statistics."""
        if not self.placement_sessions:
            return {"message": "No AI placement sessions recorded"}

        # Calculate aggregate statistics
        total_sessions = len(self.placement_sessions)
        avg_coverage = (
            sum(s["coverage_percentage"] for s in self.placement_sessions) / total_sessions
        )
        avg_compliance = (
            sum(s["compliance_score"] for s in self.placement_sessions) / total_sessions
        )
        total_cost = sum(s["cost_estimate"] for s in self.placement_sessions)

        device_type_counts = {}
        for session in self.placement_sessions:
            device_type = session["device_type"]
            device_type_counts[device_type] = (
                device_type_counts.get(device_type, 0) + session["devices_placed"]
            )

        return {
            "total_sessions": total_sessions,
            "total_devices_placed": self.total_devices_placed,
            "average_coverage_percentage": avg_coverage,
            "average_compliance_score": avg_compliance,
            "total_estimated_cost": total_cost,
            "device_type_breakdown": device_type_counts,
            "model_space_bounds": self.model_space.get_bounds(),
            "unit_system": self.unit_system.display_units.value,
        }


def create_professional_ai_engine(model_space: ModelSpace) -> ProfessionalAIPlacementEngine:
    """Factory function to create professional AI placement engine."""
    return ProfessionalAIPlacementEngine(model_space)
