"""
Model Space - Infinite precision design environment for professional CAD

Model space is where all design work happens at real-world scale and precision.
Follows AutoCAD model space standards with coordinate system integration.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import uuid4

from ..geometry import Point
from ..units import Units, UnitSystem

logger = logging.getLogger(__name__)


@dataclass
class Bounds:
    """Bounding rectangle in model space coordinates."""

    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def center(self) -> Point:
        """Get center point of bounds."""
        return Point((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2)

    def width(self) -> float:
        """Get width in model units."""
        return self.max_x - self.min_x

    def height(self) -> float:
        """Get height in model units."""
        return self.max_y - self.min_y

    def contains(self, point: Point) -> bool:
        """Check if point is within bounds."""
        return self.min_x <= point.x <= self.max_x and self.min_y <= point.y <= self.max_y

    def expand_to_include(self, point: Point) -> "Bounds":
        """Expand bounds to include point."""
        return Bounds(
            min(self.min_x, point.x),
            min(self.min_y, point.y),
            max(self.max_x, point.x),
            max(self.max_y, point.y),
        )

    def intersects(self, other: "Bounds") -> bool:
        """Check if bounds intersect with another bounds."""
        return not (
            self.max_x < other.min_x
            or other.max_x < self.min_x
            or self.max_y < other.min_y
            or other.max_y < self.min_y
        )


class Entity(ABC):
    """Base class for all drawable entities in model space."""

    def __init__(self, entity_id: str | None = None):
        self.id = entity_id or uuid4().hex
        self.layer = "0"  # Default layer
        self.color = "BY_LAYER"
        self.linetype = "CONTINUOUS"
        self.lineweight = "BY_LAYER"
        self.visible = True
        self.locked = False

        # Custom properties for fire alarm entities
        self.properties: Dict[str, Any] = {}

    @abstractmethod
    def get_bounds(self) -> Bounds:
        """Get entity bounding box in model coordinates."""
        pass

    @abstractmethod
    def transform(self, origin: Point, scale: float, rotation: float) -> "Entity":
        """Apply transformation and return new entity."""
        pass

    @abstractmethod
    def copy(self) -> "Entity":
        """Create a copy of this entity."""
        pass


class Line(Entity):
    """Line entity defined by start and end points."""

    def __init__(self, start: Point, end: Point, entity_id: str | None = None):
        super().__init__(entity_id)
        self.start = start
        self.end = end

    def get_bounds(self) -> Bounds:
        """Get line bounding box."""
        return Bounds(
            min(self.start.x, self.end.x),
            min(self.start.y, self.end.y),
            max(self.start.x, self.end.x),
            max(self.start.y, self.end.y),
        )

    def transform(self, origin: Point, scale: float, rotation: float) -> "Line":
        """Transform line and return new line."""
        new_start = (self.start - origin) * scale
        new_start = new_start.rotate(rotation) + origin
        new_end = (self.end - origin) * scale
        new_end = new_end.rotate(rotation) + origin
        return Line(new_start, new_end, self.id)

    def copy(self) -> "Line":
        """Copy line."""
        new_line = Line(self.start, self.end)
        new_line.layer = self.layer
        new_line.color = self.color
        new_line.linetype = self.linetype
        new_line.properties = self.properties.copy()
        return new_line

    def length(self) -> float:
        """Get line length in model units."""
        return self.start.distance_to(self.end)


class Circle(Entity):
    """Circle entity defined by center point and radius."""

    def __init__(self, center: Point, radius: float, entity_id: str | None = None):
        super().__init__(entity_id)
        self.center = center
        self.radius = radius

    def get_bounds(self) -> Bounds:
        """Get circle bounding box."""
        return Bounds(
            self.center.x - self.radius,
            self.center.y - self.radius,
            self.center.x + self.radius,
            self.center.y + self.radius,
        )

    def transform(self, origin: Point, scale: float, rotation: float) -> "Circle":
        """Transform circle and return new circle."""
        new_center = (self.center - origin) * scale
        new_center = new_center.rotate(rotation) + origin
        new_radius = self.radius * scale
        return Circle(new_center, new_radius, self.id)

    def copy(self) -> "Circle":
        """Copy circle."""
        new_circle = Circle(self.center, self.radius)
        new_circle.layer = self.layer
        new_circle.color = self.color
        new_circle.linetype = self.linetype
        new_circle.properties = self.properties.copy()
        return new_circle


class Arc(Entity):
    """Arc entity defined by center, radius, start angle, and end angle."""

    def __init__(
        self,
        center: Point,
        radius: float,
        start_angle: float,
        end_angle: float,
        entity_id: str | None = None,
    ):
        super().__init__(entity_id)
        self.center = center
        self.radius = radius
        self.start_angle = start_angle  # In radians
        self.end_angle = end_angle  # In radians

    def get_bounds(self) -> Bounds:
        """Get arc bounding box."""
        # Simplified - assumes arc doesn't cross axis-aligned extremes
        import math

        start_x = self.center.x + self.radius * math.cos(self.start_angle)
        start_y = self.center.y + self.radius * math.sin(self.start_angle)
        end_x = self.center.x + self.radius * math.cos(self.end_angle)
        end_y = self.center.y + self.radius * math.sin(self.end_angle)

        return Bounds(
            min(start_x, end_x), min(start_y, end_y), max(start_x, end_x), max(start_y, end_y)
        )

    def transform(self, origin: Point, scale: float, rotation: float) -> "Arc":
        """Transform arc and return new arc."""
        new_center = (self.center - origin) * scale
        new_center = new_center.rotate(rotation) + origin
        new_radius = self.radius * scale
        new_start_angle = self.start_angle + rotation
        new_end_angle = self.end_angle + rotation
        return Arc(new_center, new_radius, new_start_angle, new_end_angle, self.id)

    def copy(self) -> "Arc":
        """Copy arc."""
        new_arc = Arc(self.center, self.radius, self.start_angle, self.end_angle)
        new_arc.layer = self.layer
        new_arc.color = self.color
        new_arc.linetype = self.linetype
        new_arc.properties = self.properties.copy()
        return new_arc


@dataclass
class Layer:
    """Layer definition with properties."""

    name: str
    color: str = "WHITE"
    linetype: str = "CONTINUOUS"
    lineweight: float = 0.25  # in mm
    visible: bool = True
    locked: bool = False
    plottable: bool = True


class ModelSpace:
    """
    Model Space - Infinite precision design environment.

    This is where all design work happens at real-world coordinates and scale.
    Follows AutoCAD model space standards with professional precision.
    """

    def __init__(self, unit_system: UnitSystem | None = None):
        self.unit_system = unit_system or UnitSystem(Units.FEET)

        # Entity storage
        self.entities: Dict[str, Entity] = {}
        self.layers: Dict[str, Layer] = {}

        # Model space bounds (automatically calculated)
        self._bounds: Bounds | None = None
        self._bounds_dirty = True

        # Default layers
        self._create_default_layers()

        logger.info(f"ModelSpace initialized with {self.unit_system.display_units.value} units")

    def _create_default_layers(self):
        """Create default AutoCAD-style layers."""
        self.layers["0"] = Layer("0", "WHITE", "CONTINUOUS")  # Default layer
        self.layers["DEFPOINTS"] = Layer("DEFPOINTS", "WHITE", "CONTINUOUS")  # Non-plotting

        # Fire alarm specific layers
        self.layers["FA-DEVICES"] = Layer("FA-DEVICES", "RED", "CONTINUOUS")
        self.layers["FA-WIRING"] = Layer("FA-WIRING", "CYAN", "CONTINUOUS")
        self.layers["FA-ZONES"] = Layer("FA-ZONES", "GREEN", "CONTINUOUS")
        self.layers["FA-TEXT"] = Layer("FA-TEXT", "YELLOW", "CONTINUOUS")

    def add_entity(self, entity: Entity, layer: str = "0") -> bool:
        """
        Add entity to model space.

        Args:
            entity: Entity to add
            layer: Layer name to place entity on

        Returns:
            True if added successfully
        """
        if layer not in self.layers:
            logger.warning(f"Layer '{layer}' does not exist, creating it")
            self.layers[layer] = Layer(layer)

        entity.layer = layer
        self.entities[entity.id] = entity
        self._bounds_dirty = True

        logger.debug(f"Added {entity.__class__.__name__} to layer '{layer}'")
        return True

    def remove_entity(self, entity_id: str) -> bool:
        """Remove entity from model space."""
        if entity_id in self.entities:
            del self.entities[entity_id]
            self._bounds_dirty = True
            logger.debug(f"Removed entity {entity_id}")
            return True
        return False

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get entity by ID."""
        return self.entities.get(entity_id)

    def get_entities_on_layer(self, layer: str) -> List[Entity]:
        """Get all entities on specified layer."""
        return [entity for entity in self.entities.values() if entity.layer == layer]

    def get_entities_in_bounds(self, bounds: Bounds) -> List[Entity]:
        """Get all entities that intersect with bounds."""
        result = []
        for entity in self.entities.values():
            if entity.visible and bounds.intersects(entity.get_bounds()):
                result.append(entity)
        return result

    def get_bounds(self) -> Bounds | None:
        """
        Get the bounding box of all entities in model space.

        Returns:
            Bounds of all entities, or None if no entities
        """
        if self._bounds_dirty:
            self._calculate_bounds()
        return self._bounds

    def _calculate_bounds(self):
        """Calculate bounds from all visible entities."""
        if not self.entities:
            self._bounds = None
            self._bounds_dirty = False
            return

        visible_entities = [e for e in self.entities.values() if e.visible]
        if not visible_entities:
            self._bounds = None
            self._bounds_dirty = False
            return

        # Start with first entity bounds
        first_bounds = visible_entities[0].get_bounds()
        bounds = Bounds(
            first_bounds.min_x, first_bounds.min_y, first_bounds.max_x, first_bounds.max_y
        )

        # Expand to include all entities
        for entity in visible_entities[1:]:
            entity_bounds = entity.get_bounds()
            bounds = Bounds(
                min(bounds.min_x, entity_bounds.min_x),
                min(bounds.min_y, entity_bounds.min_y),
                max(bounds.max_x, entity_bounds.max_x),
                max(bounds.max_y, entity_bounds.max_y),
            )

        self._bounds = bounds
        self._bounds_dirty = False

    def clear(self):
        """Clear all entities from model space."""
        self.entities.clear()
        self._bounds = None
        self._bounds_dirty = True
        logger.info("ModelSpace cleared")

    def create_layer(self, name: str, color: str = "WHITE", linetype: str = "CONTINUOUS") -> Layer:
        """Create a new layer."""
        layer = Layer(name, color, linetype)
        self.layers[name] = layer
        logger.debug(f"Created layer '{name}'")
        return layer

    def set_layer_visible(self, layer_name: str, visible: bool):
        """Set layer visibility."""
        if layer_name in self.layers:
            self.layers[layer_name].visible = visible
            self._bounds_dirty = True  # Bounds may change with visibility

    def zoom_extents(self) -> Bounds | None:
        """Get bounds for zoom extents operation."""
        bounds = self.get_bounds()
        if bounds:
            # Add 10% padding
            padding_x = bounds.width() * 0.1
            padding_y = bounds.height() * 0.1
            return Bounds(
                bounds.min_x - padding_x,
                bounds.min_y - padding_y,
                bounds.max_x + padding_x,
                bounds.max_y + padding_y,
            )
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get model space statistics."""
        stats = {
            "total_entities": len(self.entities),
            "visible_entities": len([e for e in self.entities.values() if e.visible]),
            "layers": len(self.layers),
            "unit_system": self.unit_system.display_units.value,
            "bounds": self.get_bounds(),
        }

        # Entity type counts
        entity_types: Dict[str, int] = {}
        for entity in self.entities.values():
            entity_type = entity.__class__.__name__
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        stats["entity_types"] = entity_types

        return stats
