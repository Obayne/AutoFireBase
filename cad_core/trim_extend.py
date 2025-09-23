"""Enhanced trim and extend operations for lines and arcs.

This module provides robust trim/extend algorithms with comprehensive edge case handling.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass

from .lines import Point, Line, intersection_line_line, intersection_segment_segment, is_point_on_segment


# For now, focus on Line operations only
GeometryElement = Line


@dataclass
class Arc:
    """Simple arc representation for fillet operations."""
    center: Point
    radius: float
    start_angle: float  # in radians
    end_angle: float    # in radians
    
    def start_point(self) -> Point:
        """Get the start point of the arc."""
        return Point(
            self.center.x + self.radius * math.cos(self.start_angle),
            self.center.y + self.radius * math.sin(self.start_angle)
        )
    
    def end_point(self) -> Point:
        """Get the end point of the arc."""
        return Point(
            self.center.x + self.radius * math.cos(self.end_angle),
            self.center.y + self.radius * math.sin(self.end_angle)
        )


@dataclass
class TrimResult:
    """Result of a trim operation."""
    trimmed_element: Optional[GeometryElement]
    success: bool
    reason: str = ""


@dataclass
class ExtendResult:
    """Result of an extend operation."""
    extended_element: Optional[GeometryElement]
    success: bool
    reason: str = ""


@dataclass
class FilletResult:
    """Result of a fillet operation."""
    arc: Optional[Arc]
    trimmed_line1: Optional[Line]
    trimmed_line2: Optional[Line]
    success: bool
    reason: str = ""


def distance_point_to_point(p1: Point, p2: Point) -> float:
    """Calculate distance between two points."""
    return math.hypot(p2.x - p1.x, p2.y - p1.y)


def line_from_points(p1: Point, p2: Point) -> Line:
    """Create a line from two points."""
    return Line(p1, p2)


def find_line_line_intersections(line1: Line, line2: Line, as_infinite: bool = True) -> List[Point]:
    """Find intersection points between two lines.
    
    Args:
        line1: First line
        line2: Second line
        as_infinite: If True, treat lines as infinite; if False, as segments
        
    Returns:
        List of intersection points (0 or 1 points)
    """
    if as_infinite:
        intersection = intersection_line_line(line1, line2)
        return [intersection] if intersection else []
    else:
        intersection = intersection_segment_segment(line1, line2)
        return [intersection] if intersection else []


def trim_line_to_boundary(line: Line, boundary: Line, end: str = "b") -> TrimResult:
    """Trim a line to a boundary line.
    
    Args:
        line: Line to trim
        boundary: Boundary line
        end: Which end to trim ('a' or 'b')
        
    Returns:
        TrimResult with the trimmed line or error information
    """
    if end not in ("a", "b"):
        return TrimResult(None, False, "Invalid end parameter, must be 'a' or 'b'")
    
    # Find intersection with infinite lines
    intersection = intersection_line_line(line, boundary)
    
    if not intersection:
        return TrimResult(None, False, "No intersection found with boundary")
    
    # Create new line with trimmed endpoint
    if end == "a":
        new_line = Line(intersection, line.b)
    else:
        new_line = Line(line.a, intersection)
    
    # Validate that we actually trimmed something
    endpoint = line.a if end == "a" else line.b
    if distance_point_to_point(endpoint, intersection) < 1e-9:
        return TrimResult(None, False, "Intersection point is too close to endpoint")
    
    return TrimResult(new_line, True, "Line trimmed successfully")


def extend_line_to_boundary(line: Line, boundary: Line, end: str = "b") -> ExtendResult:
    """Extend a line to meet a boundary line.
    
    Args:
        line: Line to extend
        boundary: Boundary line
        end: Which end to extend ('a' or 'b')
        
    Returns:
        ExtendResult with the extended line or error information
    """
    if end not in ("a", "b"):
        return ExtendResult(None, False, "Invalid end parameter, must be 'a' or 'b'")
    
    # Find intersection with infinite lines
    intersection = intersection_line_line(line, boundary)
    
    if not intersection:
        return ExtendResult(None, False, "No intersection found with boundary")
    
    # Check if intersection is in the direction of extension
    endpoint = line.a if end == "a" else line.b
    other_end = line.b if end == "a" else line.a
    
    # Direction vector from other end to endpoint
    direction = Point(endpoint.x - other_end.x, endpoint.y - other_end.y)
    
    # Vector from other end to intersection
    to_intersection = Point(intersection.x - other_end.x, intersection.y - other_end.y)
    
    # Check if intersection is in the extension direction
    dot_product = direction.x * to_intersection.x + direction.y * to_intersection.y
    distance_to_intersection = distance_point_to_point(other_end, intersection)
    distance_to_endpoint = distance_point_to_point(other_end, endpoint)
    
    # Intersection should be further from other_end than the current endpoint
    if dot_product <= 0 or distance_to_intersection <= distance_to_endpoint:
        return ExtendResult(None, False, "Intersection is not in extension direction")
    
    # Create new line with extended endpoint
    if end == "a":
        new_line = Line(intersection, line.b)
    else:
        new_line = Line(line.a, intersection)
    
    return ExtendResult(new_line, True, "Line extended successfully")


def trim_multiple_lines(lines: List[Line], cutting_elements: List[Line]) -> List[TrimResult]:
    """Trim multiple lines against multiple cutting lines.
    
    For each line, attempts to trim against all cutting elements and returns
    the result that produces the shortest trimmed line.
    
    Args:
        lines: Lines to trim
        cutting_elements: Lines to use as cutting boundaries
        
    Returns:
        List of TrimResult objects, one for each input line
    """
    results = []
    
    for line in lines:
        best_result = TrimResult(None, False, "No valid cuts found")
        shortest_length = float('inf')
        
        for cutter in cutting_elements:
            # Try trimming both ends
            for end in ["a", "b"]:
                result = trim_line_to_boundary(line, cutter, end)
                if result.success and result.trimmed_element:
                    trimmed_line = result.trimmed_element
                    length = distance_point_to_point(trimmed_line.a, trimmed_line.b)
                    if length < shortest_length:
                        shortest_length = length
                        best_result = result
        
        results.append(best_result)
    
    return results


def extend_multiple_lines(lines: List[Line], boundary_elements: List[Line]) -> List[ExtendResult]:
    """Extend multiple lines to boundary lines.
    
    For each line, attempts to extend against all boundary elements and returns
    the result that produces the shortest extension.
    
    Args:
        lines: Lines to extend
        boundary_elements: Lines to use as extension boundaries
        
    Returns:
        List of ExtendResult objects, one for each input line
    """
    results = []
    
    for line in lines:
        best_result = ExtendResult(None, False, "No valid extensions found")
        shortest_extension = float('inf')
        
        for boundary in boundary_elements:
            # Try extending both ends
            for end in ["a", "b"]:
                result = extend_line_to_boundary(line, boundary, end)
                if result.success and result.extended_element:
                    extended_line = result.extended_element
                    original_length = distance_point_to_point(line.a, line.b)
                    new_length = distance_point_to_point(extended_line.a, extended_line.b)
                    extension_length = new_length - original_length
                    
                    if extension_length < shortest_extension:
                        shortest_extension = extension_length
                        best_result = result
        
        results.append(best_result)
    
    return results


def break_line_at_points(line: Line, break_points: List[Point], tolerance: float = 1e-9) -> List[Line]:
    """Break a line into segments at specified points.
    
    Args:
        line: Line to break
        break_points: Points where the line should be broken
        tolerance: Tolerance for point-on-line checking
        
    Returns:
        List of line segments
    """
    # Filter break points that actually lie on the line
    valid_breaks = []
    for point in break_points:
        if is_point_on_segment(point, line, tolerance):
            valid_breaks.append(point)
    
    if not valid_breaks:
        return [line]
    
    # Sort break points along the line
    def parameter_on_line(point: Point) -> float:
        """Get parameter t where point = line.a + t * (line.b - line.a)"""
        dx = line.b.x - line.a.x
        dy = line.b.y - line.a.y
        
        if abs(dx) > abs(dy):
            return (point.x - line.a.x) / dx if abs(dx) > tolerance else 0
        else:
            return (point.y - line.a.y) / dy if abs(dy) > tolerance else 0
    
    # Sort by parameter along line
    sorted_breaks = sorted(valid_breaks, key=parameter_on_line)
    
    # Create segments
    segments = []
    current_start = line.a
    
    for break_point in sorted_breaks:
        if distance_point_to_point(current_start, break_point) > tolerance:
            segments.append(Line(current_start, break_point))
        current_start = break_point
    
    # Add final segment to line end
    if distance_point_to_point(current_start, line.b) > tolerance:
        segments.append(Line(current_start, line.b))
    
    return segments


def angle_between_vectors(v1: Point, v2: Point) -> float:
    """Calculate angle between two vectors."""
    dot = v1.x * v2.x + v1.y * v2.y
    det = v1.x * v2.y - v1.y * v2.x
    return math.atan2(det, dot)


def normalize_vector(v: Point) -> Point:
    """Normalize a vector to unit length."""
    length = math.hypot(v.x, v.y)
    if length < 1e-9:
        return Point(0, 0)
    return Point(v.x / length, v.y / length)


def perpendicular_vector(v: Point) -> Point:
    """Get a vector perpendicular to the input vector."""
    return Point(-v.y, v.x)


def fillet_two_lines(line1: Line, line2: Line, radius: float) -> FilletResult:
    """Create a fillet arc between two lines.
    
    Args:
        line1: First line
        line2: Second line
        radius: Fillet radius
        
    Returns:
        FilletResult with the fillet arc and trimmed lines
    """
    if radius <= 0:
        return FilletResult(None, None, None, False, "Radius must be positive")
    
    # Find intersection of infinite lines
    intersection = intersection_line_line(line1, line2)
    if not intersection:
        return FilletResult(None, None, None, False, "Lines do not intersect")
    
    # Get direction vectors
    dir1 = Point(line1.b.x - line1.a.x, line1.b.y - line1.a.y)
    dir2 = Point(line2.b.x - line2.a.x, line2.b.y - line2.a.y)
    
    # Normalize direction vectors
    dir1_norm = normalize_vector(dir1)
    dir2_norm = normalize_vector(dir2)
    
    # Check if lines are parallel
    cross_product = dir1_norm.x * dir2_norm.y - dir1_norm.y * dir2_norm.x
    if abs(cross_product) < 1e-9:
        return FilletResult(None, None, None, False, "Lines are parallel")
    
    # Calculate angle between lines
    angle = angle_between_vectors(dir1_norm, dir2_norm)
    half_angle = angle / 2
    
    # Distance from intersection to arc center
    if abs(math.sin(half_angle)) < 1e-9:
        return FilletResult(None, None, None, False, "Invalid angle for fillet")
    
    center_distance = radius / abs(math.sin(half_angle))
    
    # Direction to arc center (bisector of the angle)
    bisector_x = (dir1_norm.x + dir2_norm.x) / 2
    bisector_y = (dir1_norm.y + dir2_norm.y) / 2
    bisector_norm = normalize_vector(Point(bisector_x, bisector_y))
    
    # Arc center position
    center = Point(
        intersection.x + bisector_norm.x * center_distance,
        intersection.y + bisector_norm.y * center_distance
    )
    
    # Calculate tangent points on each line
    # Distance from intersection to tangent points
    tangent_distance = radius / abs(math.tan(half_angle / 2)) if abs(math.tan(half_angle / 2)) > 1e-9 else radius
    
    tangent1 = Point(
        intersection.x - dir1_norm.x * tangent_distance,
        intersection.y - dir1_norm.y * tangent_distance
    )
    
    tangent2 = Point(
        intersection.x - dir2_norm.x * tangent_distance,
        intersection.y - dir2_norm.y * tangent_distance
    )
    
    # Calculate start and end angles for the arc
    start_angle = math.atan2(tangent1.y - center.y, tangent1.x - center.x)
    end_angle = math.atan2(tangent2.y - center.y, tangent2.x - center.x)
    
    # Ensure arc goes the shorter way
    if abs(end_angle - start_angle) > math.pi:
        if end_angle > start_angle:
            end_angle -= 2 * math.pi
        else:
            start_angle -= 2 * math.pi
    
    # Create the arc
    arc = Arc(center, radius, start_angle, end_angle)
    
    # Create trimmed lines
    # Determine which endpoints to keep based on which are further from intersection
    dist1a = distance_point_to_point(line1.a, intersection)
    dist1b = distance_point_to_point(line1.b, intersection)
    
    if dist1a > dist1b:
        trimmed_line1 = Line(line1.a, tangent1)
    else:
        trimmed_line1 = Line(tangent1, line1.b)
    
    dist2a = distance_point_to_point(line2.a, intersection)
    dist2b = distance_point_to_point(line2.b, intersection)
    
    if dist2a > dist2b:
        trimmed_line2 = Line(line2.a, tangent2)
    else:
        trimmed_line2 = Line(tangent2, line2.b)
    
    return FilletResult(arc, trimmed_line1, trimmed_line2, True, "Fillet created successfully")


def fillet_multiple_line_pairs(line_pairs: List[Tuple[Line, Line]], radius: float) -> List[FilletResult]:
    """Create fillets for multiple line pairs.
    
    Args:
        line_pairs: List of (line1, line2) tuples
        radius: Fillet radius for all pairs
        
    Returns:
        List of FilletResult objects
    """
    results = []
    for line1, line2 in line_pairs:
        result = fillet_two_lines(line1, line2, radius)
        results.append(result)
    return results


__all__ = [
    "TrimResult",
    "ExtendResult",
    "FilletResult",
    "Arc",
    "GeometryElement",
    "trim_line_to_boundary",
    "extend_line_to_boundary",
    "trim_multiple_lines",
    "extend_multiple_lines",
    "break_line_at_points",
    "find_line_line_intersections",
    "fillet_two_lines",
    "fillet_multiple_line_pairs",
]