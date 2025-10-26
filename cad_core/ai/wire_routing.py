"""
AI Wire Routing Engine for AutoFire
Smart auto-routing with obstacle avoidance, conduit optimization, and cost analysis

This module provides intelligent wire routing that automatically finds optimal
paths between devices while avoiding obstacles, minimizing costs, and ensuring
code compliance.
"""

import math
import logging
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Set
from enum import Enum
import heapq

logger = logging.getLogger(__name__)


class RoutingMode(Enum):
    """Wire routing optimization modes."""
    SHORTEST_PATH = "shortest_path"  # Minimize wire length
    LOWEST_COST = "lowest_cost"      # Minimize total cost
    FEWEST_TURNS = "fewest_turns"    # Minimize bends/turns
    CONDUIT_SHARED = "conduit_shared" # Share conduit runs
    MAINTENANCE_ACCESS = "maintenance_access"  # Ensure maintenance access


class WireType(Enum):
    """Wire types with different properties."""
    THHN_12 = "thhn_12"
    THHN_14 = "thhn_14" 
    THHN_16 = "thhn_16"
    THHN_18 = "thhn_18"
    FPLR_14 = "fplr_14"
    FPLR_16 = "fplr_16"
    FPLR_18 = "fplr_18"


@dataclass
class WireSpec:
    """Wire specifications and properties."""
    wire_type: WireType
    cost_per_foot: float
    max_current: float
    resistance_per_1000ft: float
    conduit_fill_area: float  # Square inches
    bend_radius_multiplier: float = 6.0  # Times wire diameter


@dataclass
class Obstacle:
    """Obstacle in the routing path."""
    x1: float
    y1: float
    x2: float
    y2: float
    height_ft: float = 0.0
    obstacle_type: str = "wall"  # wall, beam, equipment, etc.


@dataclass
class Conduit:
    """Conduit run with capacity and cost."""
    id: str
    start_point: Tuple[float, float]
    end_point: Tuple[float, float]
    diameter_inches: float
    material: str = "EMT"  # EMT, PVC, etc.
    current_fill_area: float = 0.0
    installed_cost: float = 0.0
    
    @property
    def max_fill_area(self) -> float:
        """Maximum allowable fill area (40% of conduit area)."""
        area = math.pi * (self.diameter_inches / 2) ** 2
        return area * 0.4  # NEC 40% fill


@dataclass
class RoutingResult:
    """Result of wire routing with path and cost analysis."""
    device_from: str
    device_to: str
    path_points: List[Tuple[float, float]]
    wire_type: WireType
    total_length_ft: float
    total_cost: float
    conduits_used: List[str]
    turn_count: int
    routing_mode: RoutingMode
    confidence_score: float
    obstacles_avoided: List[str]
    code_compliance: bool = True
    optimization_notes: List[str] = field(default_factory=list)


class SmartRoutingEngine:
    """AI-powered wire routing engine with pathfinding and optimization."""
    
    # Wire specifications database
    WIRE_SPECS = {
        WireType.THHN_12: WireSpec(WireType.THHN_12, 0.85, 20.0, 2.01, 0.0133),
        WireType.THHN_14: WireSpec(WireType.THHN_14, 0.65, 15.0, 3.19, 0.0097),
        WireType.THHN_16: WireSpec(WireType.THHN_16, 0.45, 10.0, 5.08, 0.0075),
        WireType.THHN_18: WireSpec(WireType.THHN_18, 0.35, 7.0, 8.08, 0.0058),
        WireType.FPLR_14: WireSpec(WireType.FPLR_14, 1.25, 15.0, 3.19, 0.0097),
        WireType.FPLR_16: WireSpec(WireType.FPLR_16, 0.95, 10.0, 5.08, 0.0075),
        WireType.FPLR_18: WireSpec(WireType.FPLR_18, 0.75, 7.0, 8.08, 0.0058),
    }
    
    def __init__(self, grid_resolution: float = 1.0):
        """
        Initialize routing engine.
        
        Args:
            grid_resolution: Grid spacing for pathfinding (feet)
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.grid_resolution = grid_resolution
        self.obstacles: List[Obstacle] = []
        self.conduits: Dict[str, Conduit] = {}
        self.device_locations: Dict[str, Tuple[float, float]] = {}
        self.routing_cache: Dict[str, RoutingResult] = {}
        
    def add_obstacle(self, obstacle: Obstacle) -> None:
        """Add obstacle to routing environment."""
        self.obstacles.append(obstacle)
        self._clear_cache()
    
    def add_conduit(self, conduit: Conduit) -> None:
        """Add conduit run to routing environment."""
        self.conduits[conduit.id] = conduit
        self._clear_cache()
    
    def set_device_location(self, device_id: str, location: Tuple[float, float]) -> None:
        """Set device location for routing."""
        self.device_locations[device_id] = location
        self._clear_cache()
    
    def route_wire(
        self,
        from_device: str,
        to_device: str,
        wire_type: WireType,
        routing_mode: RoutingMode = RoutingMode.SHORTEST_PATH,
        circuit_current: float = 1.0
    ) -> RoutingResult:
        """
        Calculate optimal wire route between devices.
        
        Args:
            from_device: Starting device ID
            to_device: Ending device ID
            wire_type: Type of wire to route
            routing_mode: Optimization mode
            circuit_current: Current for this wire (Amps)
            
        Returns:
            RoutingResult with optimal path and analysis
        """
        # Check cache first
        cache_key = f"{from_device}_{to_device}_{wire_type.value}_{routing_mode.value}"
        if cache_key in self.routing_cache:
            return self.routing_cache[cache_key]
        
        # Get device locations
        if from_device not in self.device_locations:
            raise ValueError(f"Device location not set: {from_device}")
        if to_device not in self.device_locations:
            raise ValueError(f"Device location not set: {to_device}")
        
        start_pos = self.device_locations[from_device]
        end_pos = self.device_locations[to_device]
        
        # Find optimal path using A* algorithm
        path = self._find_optimal_path(start_pos, end_pos, routing_mode)
        
        # Analyze and optimize the path
        result = self._analyze_route(
            from_device, to_device, path, wire_type, routing_mode, circuit_current
        )
        
        # Cache result
        self.routing_cache[cache_key] = result
        
        return result
    
    def _find_optimal_path(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        routing_mode: RoutingMode
    ) -> List[Tuple[float, float]]:
        """Find optimal path using A* pathfinding algorithm."""
        
        # Create grid for pathfinding
        min_x = min(start[0], end[0]) - 20
        max_x = max(start[0], end[0]) + 20
        min_y = min(start[1], end[1]) - 20
        max_y = max(start[1], end[1]) + 20
        
        # A* pathfinding
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, end)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if self._distance(current, end) < self.grid_resolution:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                path.append(end)  # Add exact end point
                return self._smooth_path(path)
            
            # Get neighbors
            neighbors = self._get_neighbors(current, min_x, max_x, min_y, max_y)
            
            for neighbor in neighbors:
                if self._is_obstacle_collision(current, neighbor):
                    continue
                
                tentative_g = g_score[current] + self._movement_cost(
                    current, neighbor, routing_mode
                )
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # No path found, return direct line
        self.logger.warning(f"No optimal path found, using direct route")
        return [start, end]
    
    def _get_neighbors(
        self, 
        point: Tuple[float, float], 
        min_x: float, 
        max_x: float, 
        min_y: float, 
        max_y: float
    ) -> List[Tuple[float, float]]:
        """Get valid neighbor points for pathfinding."""
        x, y = point
        neighbors = []
        
        # 8-directional movement
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dx, dy in directions:
            new_x = x + dx * self.grid_resolution
            new_y = y + dy * self.grid_resolution
            
            if min_x <= new_x <= max_x and min_y <= new_y <= max_y:
                neighbors.append((new_x, new_y))
        
        return neighbors
    
    def _heuristic(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Heuristic distance function for A*."""
        return self._distance(point1, point2)
    
    def _distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between points."""
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    
    def _movement_cost(
        self,
        from_point: Tuple[float, float],
        to_point: Tuple[float, float],
        routing_mode: RoutingMode
    ) -> float:
        """Calculate cost of movement between points based on routing mode."""
        base_cost = self._distance(from_point, to_point)
        
        if routing_mode == RoutingMode.SHORTEST_PATH:
            return base_cost
        elif routing_mode == RoutingMode.LOWEST_COST:
            # Factor in wire cost and installation difficulty
            return base_cost * 1.2  # Base installation multiplier
        elif routing_mode == RoutingMode.FEWEST_TURNS:
            # Penalize direction changes
            return base_cost * 1.5 if self._is_turn(from_point, to_point) else base_cost
        elif routing_mode == RoutingMode.CONDUIT_SHARED:
            # Favor paths near existing conduits
            conduit_bonus = self._calculate_conduit_proximity_bonus(from_point, to_point)
            return base_cost * (1.0 - conduit_bonus)
        else:
            return base_cost
    
    def _is_turn(self, from_point: Tuple[float, float], to_point: Tuple[float, float]) -> bool:
        """Check if movement represents a turn (diagonal)."""
        dx = abs(to_point[0] - from_point[0])
        dy = abs(to_point[1] - from_point[1])
        return dx > 0 and dy > 0
    
    def _calculate_conduit_proximity_bonus(
        self, 
        from_point: Tuple[float, float], 
        to_point: Tuple[float, float]
    ) -> float:
        """Calculate bonus for being near existing conduits."""
        min_distance = float('inf')
        
        for conduit in self.conduits.values():
            # Distance from line segment
            distance = self._point_to_line_distance(
                from_point, conduit.start_point, conduit.end_point
            )
            min_distance = min(min_distance, distance)
        
        if min_distance == float('inf'):
            return 0.0
        
        # Bonus decreases with distance
        max_bonus_distance = 5.0  # feet
        if min_distance <= max_bonus_distance:
            return (max_bonus_distance - min_distance) / max_bonus_distance * 0.3
        
        return 0.0
    
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
    
    def _is_obstacle_collision(
        self, 
        from_point: Tuple[float, float], 
        to_point: Tuple[float, float]
    ) -> bool:
        """Check if line segment collides with any obstacles."""
        for obstacle in self.obstacles:
            if self._line_intersects_rect(from_point, to_point, obstacle):
                return True
        return False
    
    def _line_intersects_rect(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        obstacle: Obstacle
    ) -> bool:
        """Check if line segment intersects with rectangular obstacle."""
        # Simple bounding box check for now
        x1, y1 = p1
        x2, y2 = p2
        
        # Line bounding box
        line_min_x, line_max_x = min(x1, x2), max(x1, x2)
        line_min_y, line_max_y = min(y1, y2), max(y1, y2)
        
        # Obstacle bounding box
        obs_min_x, obs_max_x = min(obstacle.x1, obstacle.x2), max(obstacle.x1, obstacle.x2)
        obs_min_y, obs_max_y = min(obstacle.y1, obstacle.y2), max(obstacle.y1, obstacle.y2)
        
        # Check if bounding boxes overlap
        return not (
            line_max_x < obs_min_x or line_min_x > obs_max_x or
            line_max_y < obs_min_y or line_min_y > obs_max_y
        )
    
    def _smooth_path(self, path: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Smooth path by removing unnecessary waypoints."""
        if len(path) <= 2:
            return path
        
        smoothed = [path[0]]
        
        i = 0
        while i < len(path) - 1:
            j = len(path) - 1
            
            # Find furthest point we can reach directly
            while j > i + 1:
                if not self._is_obstacle_collision(path[i], path[j]):
                    break
                j -= 1
            
            smoothed.append(path[j])
            i = j
        
        return smoothed
    
    def _analyze_route(
        self,
        from_device: str,
        to_device: str,
        path: List[Tuple[float, float]],
        wire_type: WireType,
        routing_mode: RoutingMode,
        circuit_current: float
    ) -> RoutingResult:
        """Analyze routing result and calculate costs."""
        
        # Calculate total length
        total_length = 0.0
        for i in range(len(path) - 1):
            total_length += self._distance(path[i], path[i + 1])
        
        # Count turns
        turn_count = self._count_turns(path)
        
        # Calculate cost
        wire_spec = self.WIRE_SPECS[wire_type]
        material_cost = total_length * wire_spec.cost_per_foot
        installation_cost = total_length * 2.5  # $2.50 per foot installation
        total_cost = material_cost + installation_cost
        
        # Check conduit requirements
        conduits_used = self._analyze_conduit_usage(path, wire_spec)
        
        # Determine obstacles avoided
        obstacles_avoided = self._get_obstacles_avoided(path)
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(
            path, routing_mode, turn_count, obstacles_avoided
        )
        
        # Generate optimization notes
        optimization_notes = self._generate_optimization_notes(
            path, wire_type, routing_mode, turn_count, total_length
        )
        
        return RoutingResult(
            device_from=from_device,
            device_to=to_device,
            path_points=path,
            wire_type=wire_type,
            total_length_ft=total_length,
            total_cost=total_cost,
            conduits_used=conduits_used,
            turn_count=turn_count,
            routing_mode=routing_mode,
            confidence_score=confidence,
            obstacles_avoided=obstacles_avoided,
            optimization_notes=optimization_notes
        )
    
    def _count_turns(self, path: List[Tuple[float, float]]) -> int:
        """Count the number of turns in the path."""
        if len(path) < 3:
            return 0
        
        turns = 0
        for i in range(1, len(path) - 1):
            # Calculate direction vectors
            v1 = (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
            v2 = (path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])
            
            # Check if direction changed significantly
            if abs(v1[0] * v2[1] - v1[1] * v2[0]) > 0.1:  # Cross product for angle
                turns += 1
        
        return turns
    
    def _analyze_conduit_usage(
        self, 
        path: List[Tuple[float, float]], 
        wire_spec: WireSpec
    ) -> List[str]:
        """Analyze which conduits could be used for this route."""
        conduits_used = []
        
        for conduit_id, conduit in self.conduits.items():
            # Check if path is near this conduit
            path_near_conduit = any(
                self._point_to_line_distance(
                    point, conduit.start_point, conduit.end_point
                ) < 2.0  # Within 2 feet
                for point in path
            )
            
            if path_near_conduit:
                # Check if conduit has capacity
                available_fill = conduit.max_fill_area - conduit.current_fill_area
                if available_fill >= wire_spec.conduit_fill_area:
                    conduits_used.append(conduit_id)
        
        return conduits_used
    
    def _get_obstacles_avoided(self, path: List[Tuple[float, float]]) -> List[str]:
        """Get list of obstacles that were avoided by this path."""
        avoided = []
        
        for i, obstacle in enumerate(self.obstacles):
            # Check if any path segment comes close to obstacle
            obstacle_avoided = False
            for j in range(len(path) - 1):
                distance = self._point_to_line_distance(
                    ((obstacle.x1 + obstacle.x2) / 2, (obstacle.y1 + obstacle.y2) / 2),
                    path[j], path[j + 1]
                )
                if distance < 5.0:  # Within 5 feet
                    obstacle_avoided = True
                    break
            
            if obstacle_avoided:
                avoided.append(f"{obstacle.obstacle_type}_{i}")
        
        return avoided
    
    def _calculate_confidence_score(
        self,
        path: List[Tuple[float, float]],
        routing_mode: RoutingMode,
        turn_count: int,
        obstacles_avoided: List[str]
    ) -> float:
        """Calculate confidence score for routing result."""
        base_score = 0.8
        
        # Bonus for avoiding obstacles
        obstacle_bonus = min(len(obstacles_avoided) * 0.05, 0.15)
        
        # Penalty for excessive turns
        turn_penalty = min(turn_count * 0.02, 0.1)
        
        # Mode-specific adjustments
        mode_bonus = 0.1 if routing_mode == RoutingMode.SHORTEST_PATH else 0.05
        
        return min(base_score + obstacle_bonus + mode_bonus - turn_penalty, 1.0)
    
    def _generate_optimization_notes(
        self,
        path: List[Tuple[float, float]],
        wire_type: WireType,
        routing_mode: RoutingMode,
        turn_count: int,
        total_length: float
    ) -> List[str]:
        """Generate optimization suggestions for the route."""
        notes = []
        
        if turn_count > 4:
            notes.append(f"Route has {turn_count} turns - consider straighter path")
        
        if total_length > 100:
            notes.append("Long wire run - verify voltage drop compliance")
        
        if routing_mode != RoutingMode.CONDUIT_SHARED and self.conduits:
            notes.append("Consider sharing conduit runs for cost savings")
        
        wire_spec = self.WIRE_SPECS[wire_type]
        if wire_spec.cost_per_foot > 1.0:
            notes.append("Premium wire type - verify if required by code")
        
        return notes
    
    def _clear_cache(self) -> None:
        """Clear routing cache when environment changes."""
        self.routing_cache.clear()


def create_smart_routing_engine(grid_resolution: float = 1.0) -> SmartRoutingEngine:
    """Factory function to create smart routing engine."""
    return SmartRoutingEngine(grid_resolution)


# Example usage and testing
if __name__ == "__main__":
    # Create routing engine
    router = create_smart_routing_engine(grid_resolution=2.0)
    
    # Set up environment
    router.set_device_location("PANEL1", (0, 0))
    router.set_device_location("SMOKE_001", (50, 30))
    router.set_device_location("SMOKE_002", (80, 45))
    
    # Add obstacles
    router.add_obstacle(Obstacle(20, 10, 30, 25, obstacle_type="column"))
    router.add_obstacle(Obstacle(60, 20, 70, 40, obstacle_type="equipment"))
    
    # Add conduit
    router.add_conduit(Conduit(
        id="conduit_main",
        start_point=(0, 0),
        end_point=(100, 0),
        diameter_inches=1.0
    ))
    
    print("🔌 AutoFire AI Wire Routing Engine Demo")
    print("=" * 50)
    
    # Test different routing modes
    routing_modes = [
        RoutingMode.SHORTEST_PATH,
        RoutingMode.LOWEST_COST,
        RoutingMode.FEWEST_TURNS,
        RoutingMode.CONDUIT_SHARED
    ]
    
    for mode in routing_modes:
        print(f"\n🛤️  Routing Mode: {mode.value.replace('_', ' ').title()}")
        print("-" * 40)
        
        result = router.route_wire(
            from_device="PANEL1",
            to_device="SMOKE_001",
            wire_type=WireType.FPLR_14,
            routing_mode=mode
        )
        
        print(f"Path: {len(result.path_points)} waypoints")
        print(f"Length: {result.total_length_ft:.1f} ft")
        print(f"Cost: ${result.total_cost:.2f}")
        print(f"Turns: {result.turn_count}")
        print(f"Confidence: {result.confidence_score:.1%}")
        print(f"Obstacles Avoided: {len(result.obstacles_avoided)}")
        
        if result.optimization_notes:
            print(f"Notes: {', '.join(result.optimization_notes[:2])}")
    
    print(f"\n" + "=" * 50)
    print("🎉 Smart wire routing engine fully operational!")