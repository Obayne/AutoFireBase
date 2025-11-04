"""
Paper Space - Professional print layout system for CAD

Paper space provides the layout environment for creating construction documents
with scaled viewports into model space, annotations, and title blocks.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

from ..geometry import Point
from ..units import Units, UnitSystem
from .model_space import Bounds, Entity, ModelSpace

logger = logging.getLogger(__name__)


class PageSize(Enum):
    """Standard paper sizes for layouts."""

    ANSI_A = "ANSI_A"  # 8.5" x 11"
    ANSI_B = "ANSI_B"  # 11" x 17"
    ANSI_C = "ANSI_C"  # 17" x 22"
    ANSI_D = "ANSI_D"  # 22" x 34"
    ANSI_E = "ANSI_E"  # 34" x 44"

    def dimensions(self) -> tuple[float, float]:
        """Get page dimensions in inches (width, height)."""
        return {
            PageSize.ANSI_A: (8.5, 11.0),
            PageSize.ANSI_B: (11.0, 17.0),
            PageSize.ANSI_C: (17.0, 22.0),
            PageSize.ANSI_D: (22.0, 34.0),
            PageSize.ANSI_E: (34.0, 44.0),
        }[self]

    def display_name(self) -> str:
        """Get display name for UI."""
        return {
            PageSize.ANSI_A: 'Letter (8.5" x 11")',
            PageSize.ANSI_B: 'Tabloid (11" x 17")',
            PageSize.ANSI_C: 'C-Size (17" x 22")',
            PageSize.ANSI_D: 'D-Size (22" x 34")',
            PageSize.ANSI_E: 'E-Size (34" x 44")',
        }[self]


@dataclass
class ViewportScale:
    """Viewport scale definition (e.g., 1/4"=1'-0")."""

    # Paper distance that represents model distance
    paper_distance: float  # In inches
    model_distance: float  # In feet (or base units)

    @classmethod
    def from_string(cls, scale_text: str) -> "ViewportScale":
        """Parse scale from string like '1/4\"=1\'-0\"' or '1:100'."""
        if "=" in scale_text:
            # Architectural scale: 1/4"=1'-0"
            paper_part, model_part = scale_text.split("=")

            # Parse paper part (e.g., "1/4\"" -> 0.25 inches)
            paper_part = paper_part.strip().replace('"', "")
            if "/" in paper_part:
                num, den = paper_part.split("/")
                paper_distance = float(num) / float(den)
            else:
                paper_distance = float(paper_part)

            # Parse model part (e.g., "1'-0\"" -> 1.0 feet)
            model_part = model_part.strip()
            if "'" in model_part:
                # Handle feet-inches format
                if "-" in model_part:
                    feet_part, inch_part = model_part.split("-")
                    feet = float(feet_part.replace("'", ""))
                    inches = float(inch_part.replace('"', ""))
                    model_distance = feet + inches / 12.0
                else:
                    feet = float(model_part.replace("'", "").replace('0"', ""))
                    model_distance = feet
            else:
                model_distance = float(model_part.replace('"', "")) / 12.0  # Convert inches to feet

            return cls(paper_distance, model_distance)

        elif ":" in scale_text:
            # Metric scale: 1:100
            paper_ratio, model_ratio = scale_text.split(":")
            ratio = float(model_ratio) / float(paper_ratio)
            # Assume metric: 1 inch on paper = ratio inches in model
            return cls(1.0, ratio / 12.0)  # Convert to feet

        else:
            raise ValueError(f"Invalid scale format: {scale_text}")

    def to_string(self) -> str:
        """Convert to standard architectural scale string."""
        # Find common architectural fractions
        if abs(self.paper_distance - 0.25) < 0.001:
            paper_str = '1/4"'
        elif abs(self.paper_distance - 0.125) < 0.001:
            paper_str = '1/8"'
        elif abs(self.paper_distance - 0.0625) < 0.001:
            paper_str = '1/16"'
        elif abs(self.paper_distance - 1.0) < 0.001:
            paper_str = '1"'
        else:
            paper_str = f'{self.paper_distance}"'

        # Convert model distance to feet-inches
        feet = int(self.model_distance)
        inches = (self.model_distance - feet) * 12
        if inches < 0.001:
            model_str = f"{feet}'-0\""
        else:
            model_str = f"{feet}'-{inches:.0f}\""

        return f"{paper_str}={model_str}"

    def scale_factor(self) -> float:
        """Get scale factor (model units per paper unit)."""
        return self.model_distance / self.paper_distance


@dataclass
class Viewport:
    """Viewport - window into model space at specific scale."""

    # Viewport rectangle in paper space (inches)
    paper_bounds: Bounds

    # Area of model space to display (in model units)
    model_bounds: Bounds

    # Viewport scale
    scale: ViewportScale

    # Viewport properties
    visible: bool = True
    locked: bool = False
    layer: str = "VIEWPORTS"

    def model_to_paper(self, model_point: Point) -> Point:
        """Transform point from model space to paper space coordinates."""
        # Normalize model point to viewport bounds (0-1)
        norm_x = (model_point.x - self.model_bounds.min_x) / self.model_bounds.width()
        norm_y = (model_point.y - self.model_bounds.min_y) / self.model_bounds.height()

        # Transform to paper space
        paper_x = self.paper_bounds.min_x + norm_x * self.paper_bounds.width()
        paper_y = self.paper_bounds.min_y + norm_y * self.paper_bounds.height()

        return Point(paper_x, paper_y)

    def paper_to_model(self, paper_point: Point) -> Point:
        """Transform point from paper space to model space coordinates."""
        # Normalize paper point to viewport bounds (0-1)
        norm_x = (paper_point.x - self.paper_bounds.min_x) / self.paper_bounds.width()
        norm_y = (paper_point.y - self.paper_bounds.min_y) / self.paper_bounds.height()

        # Transform to model space
        model_x = self.model_bounds.min_x + norm_x * self.model_bounds.width()
        model_y = self.model_bounds.min_y + norm_y * self.model_bounds.height()

        return Point(model_x, model_y)

    def is_point_in_viewport(self, paper_point: Point) -> bool:
        """Check if paper space point is within viewport bounds."""
        return self.paper_bounds.contains(paper_point)

    def update_scale(self, new_scale: ViewportScale):
        """Update viewport scale, adjusting model bounds to maintain view center."""
        center = self.model_bounds.center()

        # Calculate new model bounds based on scale
        scale_ratio = new_scale.scale_factor() / self.scale.scale_factor()
        new_width = self.model_bounds.width() * scale_ratio
        new_height = self.model_bounds.height() * scale_ratio

        self.model_bounds = Bounds(
            center.x - new_width / 2,
            center.y - new_height / 2,
            center.x + new_width / 2,
            center.y + new_height / 2,
        )

        self.scale = new_scale


class PaperSpace:
    """
    Paper Space - Print layout environment with viewports.

    Paper space is where you create construction documents with scaled views
    of model space, annotations, dimensions, and title blocks.
    """

    def __init__(self, name: str = "Layout1", page_size: PageSize = PageSize.ANSI_D):
        self.name = name
        self.page_size = page_size

        # Paper space uses inches as coordinate system
        self.unit_system = UnitSystem(Units.INCHES, Units.INCHES)

        # Paper space entities (annotations, title blocks, etc.)
        self.entities: Dict[str, Entity] = {}

        # Viewports into model space
        self.viewports: List[Viewport] = []

        # Paper space bounds
        width, height = page_size.dimensions()
        self.page_bounds = Bounds(0.0, 0.0, width, height)

        # Layout properties
        self.margin = 0.5  # Inches
        self.title_block_height = 3.0  # Inches

        logger.info(f"PaperSpace '{name}' created with {page_size.display_name()}")

    def add_viewport(
        self,
        paper_x: float,
        paper_y: float,
        paper_width: float,
        paper_height: float,
        model_center: Point,
        scale: ViewportScale | str,
        model_space: ModelSpace | None = None,
    ) -> Viewport:
        """
        Add viewport to paper space.

        Args:
            paper_x, paper_y: Viewport position in paper space (inches)
            paper_width, paper_height: Viewport size in paper space (inches)
            model_center: Center point in model space to view
            scale: Viewport scale (ViewportScale object or string like "1/4\"=1'-0\"")
            model_space: Optional model space for automatic bounds calculation

        Returns:
            Created viewport
        """
        if isinstance(scale, str):
            scale = ViewportScale.from_string(scale)

        # Create paper bounds
        paper_bounds = Bounds(paper_x, paper_y, paper_x + paper_width, paper_y + paper_height)

        # Calculate model bounds based on scale and paper size
        model_width = paper_width * scale.scale_factor()
        model_height = paper_height * scale.scale_factor()

        model_bounds = Bounds(
            model_center.x - model_width / 2,
            model_center.y - model_height / 2,
            model_center.x + model_width / 2,
            model_center.y + model_height / 2,
        )

        viewport = Viewport(paper_bounds, model_bounds, scale)
        self.viewports.append(viewport)

        logger.info(f"Added viewport at ({paper_x}, {paper_y}) with scale {scale.to_string()}")
        return viewport

    def remove_viewport(self, viewport: Viewport) -> bool:
        """Remove viewport from paper space."""
        try:
            self.viewports.remove(viewport)
            logger.info("Viewport removed")
            return True
        except ValueError:
            return False

    def get_viewport_at_point(self, paper_point: Point) -> Viewport | None:
        """Get viewport containing the given paper space point."""
        for viewport in self.viewports:
            if viewport.visible and viewport.is_point_in_viewport(paper_point):
                return viewport
        return None

    def add_annotation(self, entity: Entity) -> bool:
        """Add annotation entity to paper space (text, dimensions, etc.)."""
        self.entities[entity.id] = entity
        logger.debug(f"Added {entity.__class__.__name__} annotation to paper space")
        return True

    def remove_annotation(self, entity_id: str) -> bool:
        """Remove annotation from paper space."""
        if entity_id in self.entities:
            del self.entities[entity_id]
            return True
        return False

    def get_printable_bounds(self) -> Bounds:
        """Get printable area bounds (page minus margins)."""
        return Bounds(
            self.margin,
            self.margin,
            self.page_bounds.max_x - self.margin,
            self.page_bounds.max_y - self.margin - self.title_block_height,
        )

    def auto_arrange_viewports(
        self, model_space: ModelSpace, num_viewports: int = 1
    ) -> List[Viewport]:
        """Automatically arrange viewports to show model space content."""
        printable = self.get_printable_bounds()
        model_bounds = model_space.get_bounds()

        if not model_bounds:
            logger.warning("No model space content to arrange viewports for")
            return []

        # Clear existing viewports
        self.viewports.clear()

        if num_viewports == 1:
            # Single viewport filling most of the page
            viewport_width = printable.width() * 0.9
            viewport_height = printable.height() * 0.9
            viewport_x = printable.min_x + (printable.width() - viewport_width) / 2
            viewport_y = printable.min_y + (printable.height() - viewport_height) / 2

            # Calculate appropriate scale
            model_width = model_bounds.width()
            model_height = model_bounds.height()
            scale_x = viewport_width / model_width
            scale_y = viewport_height / model_height
            scale_factor = min(scale_x, scale_y)

            # Convert to architectural scale
            if scale_factor > 1.0 / 96.0:  # 1/8" scale
                scale = ViewportScale(0.125, 1.0)  # 1/8"=1'-0"
            elif scale_factor > 1.0 / 192.0:  # 1/16" scale
                scale = ViewportScale(0.0625, 1.0)  # 1/16"=1'-0"
            else:
                scale = ViewportScale(0.03125, 1.0)  # 1/32"=1'-0"

            viewport = self.add_viewport(
                viewport_x,
                viewport_y,
                viewport_width,
                viewport_height,
                model_bounds.center(),
                scale,
                model_space,
            )
            return [viewport]

        else:
            logger.warning(
                f"Multi-viewport arrangement not yet implemented for {num_viewports} viewports"
            )
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get paper space statistics."""
        return {
            "name": self.name,
            "page_size": self.page_size.display_name(),
            "dimensions": self.page_size.dimensions(),
            "viewports": len(self.viewports),
            "annotations": len(self.entities),
            "printable_area": self.get_printable_bounds(),
        }
