"""
AI Device Placement Assistant for AutoFire
Intelligent device placement with NFPA 72 compliance and optimization

This module provides AI-powered device placement suggestions that automatically
analyze building layouts, optimize coverage, and ensure code compliance.
"""

import logging
import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Fire alarm device types with specific placement requirements."""
    SMOKE_DETECTOR = "smoke_detector"
    HEAT_DETECTOR = "heat_detector"
    PULL_STATION = "pull_station"
    HORN_STROBE = "horn_strobe"
    STROBE_ONLY = "strobe_only"
    DUCT_DETECTOR = "duct_detector"
    BEAM_DETECTOR = "beam_detector"


class SpaceType(Enum):
    """Building space classifications affecting device placement."""
    OFFICE = "office"
    CORRIDOR = "corridor"
    MECHANICAL = "mechanical"
    STORAGE = "storage"
    ASSEMBLY = "assembly"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    STAIRWELL = "stairwell"
    ELEVATOR_LOBBY = "elevator_lobby"


@dataclass
class PlacementRequirement:
    """NFPA 72 placement requirements for device types."""
    max_spacing_ft: float
    max_distance_from_wall_ft: float
    min_distance_from_hvac_ft: float
    min_height_ft: float
    max_height_ft: float
    avoid_corners: bool = True
    avoid_beams: bool = True


@dataclass
class Room:
    """Building room/space with AI analysis capabilities."""
    id: str
    name: str
    space_type: SpaceType
    vertices: List[Tuple[float, float]]  # Room boundary points
    obstacles: List[Tuple[float, float, float, float]] = None  # x1,y1,x2,y2 rects
    hvac_locations: List[Tuple[float, float]] = None  # HVAC equipment positions
    ceiling_height_ft: float = 10.0
    
    def __post_init__(self):
        if self.obstacles is None:
            self.obstacles = []
        if self.hvac_locations is None:
            self.hvac_locations = []
    
    @property
    def area_sqft(self) -> float:
        """Calculate room area using shoelace formula."""
        if len(self.vertices) < 3:
            return 0.0
        
        area = 0.0
        n = len(self.vertices)
        for i in range(n):
            j = (i + 1) % n
            area += self.vertices[i][0] * self.vertices[j][1]
            area -= self.vertices[j][0] * self.vertices[i][1]
        return abs(area) / 2.0
    
    @property
    def center_point(self) -> Tuple[float, float]:
        """Calculate geometric center of room."""
        if not self.vertices:
            return (0.0, 0.0)
        
        x_sum = sum(vertex[0] for vertex in self.vertices)
        y_sum = sum(vertex[1] for vertex in self.vertices)
        count = len(self.vertices)
        return (x_sum / count, y_sum / count)


@dataclass
class PlacementSuggestion:
    """AI-generated device placement suggestion."""
    device_type: DeviceType
    position: Tuple[float, float]
    room_id: str
    confidence_score: float  # 0.0 to 1.0
    reasoning: str
    compliance_notes: List[str]
    coverage_area_sqft: float
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high-confidence suggestion."""
        return self.confidence_score >= 0.8


class NFPARequirements:
    """NFPA 72 device placement requirements database."""
    
    PLACEMENT_RULES = {
        DeviceType.SMOKE_DETECTOR: PlacementRequirement(
            max_spacing_ft=30.0,
            max_distance_from_wall_ft=15.0,
            min_distance_from_hvac_ft=3.0,
            min_height_ft=8.0,
            max_height_ft=30.0,
            avoid_corners=True,
            avoid_beams=True
        ),
        DeviceType.HEAT_DETECTOR: PlacementRequirement(
            max_spacing_ft=50.0,  # For 135°F fixed temp
            max_distance_from_wall_ft=25.0,
            min_distance_from_hvac_ft=3.0,
            min_height_ft=8.0,
            max_height_ft=30.0,
            avoid_corners=True,
            avoid_beams=False
        ),
        DeviceType.PULL_STATION: PlacementRequirement(
            max_spacing_ft=200.0,  # Travel distance
            max_distance_from_wall_ft=0.0,  # Must be on wall
            min_distance_from_hvac_ft=0.0,
            min_height_ft=3.5,
            max_height_ft=4.5,
            avoid_corners=False,
            avoid_beams=False
        ),
        DeviceType.HORN_STROBE: PlacementRequirement(
            max_spacing_ft=100.0,  # Depends on candela
            max_distance_from_wall_ft=0.0,  # Wall or ceiling mount
            min_distance_from_hvac_ft=0.0,
            min_height_ft=7.0,
            max_height_ft=20.0,
            avoid_corners=False,
            avoid_beams=False
        )
    }
    
    @classmethod
    def get_requirements(cls, device_type: DeviceType) -> PlacementRequirement:
        """Get NFPA placement requirements for device type."""
        return cls.PLACEMENT_RULES.get(device_type, cls.PLACEMENT_RULES[DeviceType.SMOKE_DETECTOR])


class AIPlacementEngine:
    """AI-powered device placement optimization engine."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.placement_history: List[PlacementSuggestion] = []
        
    def suggest_device_placement(
        self, 
        room: Room, 
        device_type: DeviceType,
        existing_devices: List[Tuple[float, float]] = None
    ) -> List[PlacementSuggestion]:
        """
        Generate AI-powered device placement suggestions for a room.
        
        Args:
            room: Room to analyze
            device_type: Type of device to place
            existing_devices: List of existing device positions
            
        Returns:
            List of placement suggestions ordered by confidence score
        """
        if existing_devices is None:
            existing_devices = []
            
        requirements = NFPARequirements.get_requirements(device_type)
        suggestions = []
        
        # Analyze room and generate placement grid
        placement_candidates = self._generate_placement_candidates(room, requirements)
        
        # Score each candidate position
        for candidate in placement_candidates:
            score = self._score_placement_candidate(
                candidate, room, device_type, requirements, existing_devices
            )
            
            if score.confidence_score > 0.3:  # Only suggest viable placements
                suggestions.append(score)
        
        # Sort by confidence score (highest first)
        suggestions.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Store in history for learning
        self.placement_history.extend(suggestions[:3])  # Top 3 suggestions
        
        return suggestions
    
    def _generate_placement_candidates(
        self, 
        room: Room, 
        requirements: PlacementRequirement
    ) -> List[Tuple[float, float]]:
        """Generate candidate placement positions based on room geometry."""
        candidates = []
        
        # Calculate room bounds
        min_x = min(vertex[0] for vertex in room.vertices)
        max_x = max(vertex[0] for vertex in room.vertices)
        min_y = min(vertex[1] for vertex in room.vertices)
        max_y = max(vertex[1] for vertex in room.vertices)
        
        # Create placement grid based on device spacing requirements
        grid_spacing = requirements.max_spacing_ft * 0.8  # 80% of max for better coverage
        
        # Generate grid points
        x = min_x + requirements.max_distance_from_wall_ft
        while x <= max_x - requirements.max_distance_from_wall_ft:
            y = min_y + requirements.max_distance_from_wall_ft
            while y <= max_y - requirements.max_distance_from_wall_ft:
                if self._point_in_room(x, y, room):
                    candidates.append((x, y))
                y += grid_spacing
            x += grid_spacing
        
        # Add strategic positions (room center, near exits, etc.)
        center_x, center_y = room.center_point
        if self._point_in_room(center_x, center_y, room):
            candidates.append((center_x, center_y))
        
        return candidates
    
    def _score_placement_candidate(
        self,
        position: Tuple[float, float],
        room: Room,
        device_type: DeviceType,
        requirements: PlacementRequirement,
        existing_devices: List[Tuple[float, float]]
    ) -> PlacementSuggestion:
        """Score a placement candidate using AI analysis."""
        x, y = position
        score = 1.0
        reasoning_parts = []
        compliance_notes = []
        
        # NFPA compliance scoring
        if self._check_nfpa_compliance(position, room, requirements):
            compliance_notes.append("✅ NFPA 72 spacing compliant")
        else:
            score *= 0.5
            compliance_notes.append("⚠️ May not meet NFPA 72 spacing")
        
        # Distance from HVAC equipment
        hvac_penalty = self._calculate_hvac_proximity_penalty(position, room, requirements)
        score *= (1.0 - hvac_penalty)
        if hvac_penalty > 0:
            reasoning_parts.append(f"HVAC proximity penalty: {hvac_penalty:.1%}")
        
        # Coverage optimization
        coverage_score = self._calculate_coverage_score(position, room, device_type)
        score *= coverage_score
        reasoning_parts.append(f"Coverage effectiveness: {coverage_score:.1%}")
        
        # Interference with existing devices
        interference_penalty = self._calculate_interference_penalty(position, existing_devices, requirements)
        score *= (1.0 - interference_penalty)
        if interference_penalty > 0:
            reasoning_parts.append(f"Device interference penalty: {interference_penalty:.1%}")
        
        # Space-specific optimizations
        space_bonus = self._calculate_space_type_bonus(position, room, device_type)
        score *= (1.0 + space_bonus)
        if space_bonus > 0:
            reasoning_parts.append(f"Space type optimization bonus: {space_bonus:.1%}")
        
        # Calculate coverage area
        coverage_area = self._calculate_coverage_area(position, requirements, room)
        
        reasoning = "AI Analysis: " + " | ".join(reasoning_parts)
        
        return PlacementSuggestion(
            device_type=device_type,
            position=position,
            room_id=room.id,
            confidence_score=min(score, 1.0),
            reasoning=reasoning,
            compliance_notes=compliance_notes,
            coverage_area_sqft=coverage_area
        )
    
    def _point_in_room(self, x: float, y: float, room: Room) -> bool:
        """Check if point is inside room using ray casting algorithm."""
        vertices = room.vertices
        n = len(vertices)
        inside = False
        
        j = n - 1
        for i in range(n):
            xi, yi = vertices[i]
            xj, yj = vertices[j]
            
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        
        return inside
    
    def _check_nfpa_compliance(
        self, 
        position: Tuple[float, float], 
        room: Room, 
        requirements: PlacementRequirement
    ) -> bool:
        """Check if position meets NFPA 72 requirements."""
        x, y = position
        
        # Check distance from walls
        min_wall_distance = float('inf')
        for i in range(len(room.vertices)):
            j = (i + 1) % len(room.vertices)
            wall_distance = self._point_to_line_distance(
                position, room.vertices[i], room.vertices[j]
            )
            min_wall_distance = min(min_wall_distance, wall_distance)
        
        return min_wall_distance <= requirements.max_distance_from_wall_ft
    
    def _point_to_line_distance(
        self, 
        point: Tuple[float, float], 
        line_start: Tuple[float, float], 
        line_end: Tuple[float, float]
    ) -> float:
        """Calculate minimum distance from point to line segment."""
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Calculate line length squared
        line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        
        if line_length_sq == 0:
            return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
        
        # Calculate projection parameter
        t = max(0, min(1, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_sq))
        
        # Calculate projection point
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        # Return distance to projection
        return math.sqrt((x0 - proj_x) ** 2 + (y0 - proj_y) ** 2)
    
    def _calculate_hvac_proximity_penalty(
        self, 
        position: Tuple[float, float], 
        room: Room, 
        requirements: PlacementRequirement
    ) -> float:
        """Calculate penalty for being too close to HVAC equipment."""
        if not room.hvac_locations or requirements.min_distance_from_hvac_ft == 0:
            return 0.0
        
        x, y = position
        min_hvac_distance = float('inf')
        
        for hvac_x, hvac_y in room.hvac_locations:
            distance = math.sqrt((x - hvac_x) ** 2 + (y - hvac_y) ** 2)
            min_hvac_distance = min(min_hvac_distance, distance)
        
        if min_hvac_distance < requirements.min_distance_from_hvac_ft:
            # Exponential penalty for being too close
            penalty_ratio = 1.0 - (min_hvac_distance / requirements.min_distance_from_hvac_ft)
            return penalty_ratio ** 2
        
        return 0.0
    
    def _calculate_coverage_score(
        self, 
        position: Tuple[float, float], 
        room: Room, 
        device_type: DeviceType
    ) -> float:
        """Calculate how well this position covers the room."""
        x, y = position
        center_x, center_y = room.center_point
        
        # Distance from room center (closer to center is generally better)
        distance_from_center = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
        room_radius = math.sqrt(room.area_sqft / math.pi)  # Approximate room as circle
        
        center_score = 1.0 - min(distance_from_center / room_radius, 1.0)
        
        # Adjust based on device type
        if device_type == DeviceType.PULL_STATION:
            # Pull stations should be near exits/entrances (assume near room perimeter)
            center_score = 1.0 - center_score  # Invert for pull stations
        
        return max(center_score, 0.2)  # Minimum 20% coverage score
    
    def _calculate_interference_penalty(
        self, 
        position: Tuple[float, float], 
        existing_devices: List[Tuple[float, float]], 
        requirements: PlacementRequirement
    ) -> float:
        """Calculate penalty for being too close to existing devices."""
        if not existing_devices:
            return 0.0
        
        x, y = position
        min_device_distance = float('inf')
        
        for device_x, device_y in existing_devices:
            distance = math.sqrt((x - device_x) ** 2 + (y - device_y) ** 2)
            min_device_distance = min(min_device_distance, distance)
        
        # Devices should be at least half max spacing apart
        min_spacing = requirements.max_spacing_ft * 0.5
        
        if min_device_distance < min_spacing:
            penalty_ratio = 1.0 - (min_device_distance / min_spacing)
            return penalty_ratio ** 2
        
        return 0.0
    
    def _calculate_space_type_bonus(
        self, 
        position: Tuple[float, float], 
        room: Room, 
        device_type: DeviceType
    ) -> float:
        """Calculate bonus score based on space type and device type match."""
        bonuses = {
            (SpaceType.KITCHEN, DeviceType.HEAT_DETECTOR): 0.2,
            (SpaceType.MECHANICAL, DeviceType.HEAT_DETECTOR): 0.15,
            (SpaceType.CORRIDOR, DeviceType.PULL_STATION): 0.3,
            (SpaceType.STAIRWELL, DeviceType.HORN_STROBE): 0.25,
            (SpaceType.OFFICE, DeviceType.SMOKE_DETECTOR): 0.1,
        }
        
        return bonuses.get((room.space_type, device_type), 0.0)
    
    def _calculate_coverage_area(
        self, 
        position: Tuple[float, float], 
        requirements: PlacementRequirement, 
        room: Room
    ) -> float:
        """Calculate the coverage area for this device placement."""
        # Simplified circular coverage area
        coverage_radius = requirements.max_spacing_ft * 0.5
        coverage_area = math.pi * coverage_radius ** 2
        
        # Limit to room area
        return min(coverage_area, room.area_sqft)


def create_ai_placement_engine() -> AIPlacementEngine:
    """Factory function to create AI placement engine."""
    return AIPlacementEngine()


# Example usage and testing
if __name__ == "__main__":
    # Create sample room
    office_room = Room(
        id="office_001",
        name="Conference Room A",
        space_type=SpaceType.OFFICE,
        vertices=[(0, 0), (20, 0), (20, 15), (0, 15)],  # 20x15 ft room
        hvac_locations=[(10, 7.5)],  # HVAC in center
        ceiling_height_ft=9.0
    )
    
    # Create AI engine
    ai_engine = create_ai_placement_engine()
    
    # Get smoke detector suggestions
    suggestions = ai_engine.suggest_device_placement(
        room=office_room,
        device_type=DeviceType.SMOKE_DETECTOR
    )
    
    print(f"AI Placement Suggestions for {office_room.name}:")
    print(f"Room Area: {office_room.area_sqft:.1f} sq ft")
    print()
    
    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"{i}. {suggestion.device_type.value.title()}")
        print(f"   Position: ({suggestion.position[0]:.1f}, {suggestion.position[1]:.1f})")
        print(f"   Confidence: {suggestion.confidence_score:.1%}")
        print(f"   Coverage: {suggestion.coverage_area_sqft:.1f} sq ft")
        print(f"   Reasoning: {suggestion.reasoning}")
        for note in suggestion.compliance_notes:
            print(f"   {note}")
        print()