"""Professional 2D Point with double precision for CAD applications.

This module provides a Point class that uses IEEE 754 double precision
floating point arithmetic for accurate geometric calculations in CAD systems.
"""

from __future__ import annotations

import math
from typing import Tuple


class Point:
    """2D point with double precision coordinates.

    Provides accurate arithmetic operations for CAD applications where
    sub-millimeter precision is required. All operations maintain
    double precision throughout.

    Attributes:
        x: X coordinate (double precision)
        y: Y coordinate (double precision)
    """

    __slots__ = ("x", "y")

    def __init__(self, x: float | int = 0.0, y: float | int = 0.0):
        """Initialize point with double precision coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = float(x)
        self.y = float(y)

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        return f"Point({self.x}, {self.y})"

    def __str__(self) -> str:
        """Return string representation for display."""
        return f"({self.x:.6f}, {self.y:.6f})"

    def __eq__(self, other: object) -> bool:
        """Test equality with tolerance for floating point precision."""
        if not isinstance(other, Point):
            return NotImplemented

        # Use epsilon comparison for floating point equality
        epsilon = 1e-12  # Very small tolerance for double precision
        return abs(self.x - other.x) < epsilon and abs(self.y - other.y) < epsilon

    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        # Round to avoid floating point precision issues in hashing
        return hash((round(self.x, 12), round(self.y, 12)))

    def __add__(self, other: Point) -> Point:
        """Add two points (vector addition)."""
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        """Subtract two points (vector subtraction)."""
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float | int) -> Point:
        """Multiply point by scalar."""
        return Point(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float | int) -> Point:
        """Right multiply by scalar (scalar * point)."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float | int) -> Point:
        """Divide point by scalar."""
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide point by zero")
        return Point(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Point:
        """Negate point coordinates."""
        return Point(-self.x, -self.y)

    def distance_to(self, other: Point) -> float:
        """Calculate Euclidean distance to another point.

        Args:
            other: Target point

        Returns:
            Distance between points
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def distance_squared_to(self, other: Point) -> float:
        """Calculate squared distance to another point.

        More efficient when you only need to compare distances
        since it avoids the square root calculation.

        Args:
            other: Target point

        Returns:
            Squared distance between points
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy

    def magnitude(self) -> float:
        """Calculate magnitude (distance from origin)."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def magnitude_squared(self) -> float:
        """Calculate squared magnitude."""
        return self.x * self.x + self.y * self.y

    def normalize(self) -> Point:
        """Return normalized point (unit vector).

        Returns:
            Point with magnitude 1.0, or zero point if magnitude is zero

        Raises:
            ValueError: If point has zero magnitude
        """
        mag = self.magnitude()
        if mag < 1e-12:  # Very small tolerance for zero
            raise ValueError("Cannot normalize zero-magnitude point")
        return Point(self.x / mag, self.y / mag)

    def normalized(self) -> Point:
        """Return normalized point without modifying original."""
        return self.normalize()

    def dot(self, other: Point) -> float:
        """Calculate dot product with another point.

        Args:
            other: Other point/vector

        Returns:
            Dot product (scalar)
        """
        return self.x * other.x + self.y * other.y

    def cross(self, other: Point) -> float:
        """Calculate 2D cross product (scalar result).

        In 2D, cross product returns the z-component of the 3D cross product.
        Positive result means counter-clockwise rotation from self to other.

        Args:
            other: Other point/vector

        Returns:
            Cross product scalar (z-component)
        """
        return self.x * other.y - self.y * other.x

    def angle_to(self, other: Point) -> float:
        """Calculate angle to another point in radians.

        Args:
            other: Target point

        Returns:
            Angle in radians (0 to 2π)
        """
        return math.atan2(other.y - self.y, other.x - self.x)

    def angle(self) -> float:
        """Calculate angle from origin in radians.

        Returns:
            Angle in radians (0 to 2π)
        """
        return math.atan2(self.y, self.x)

    def rotate(self, angle: float, center: Point | None = None) -> Point:
        """Rotate point around center by angle.

        Args:
            angle: Rotation angle in radians (positive = counter-clockwise)
            center: Center of rotation (default: origin)

        Returns:
            Rotated point
        """
        if center is None:
            center = Point(0, 0)

        # Translate to origin
        translated = self - center

        # Rotate
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        rotated = Point(
            translated.x * cos_a - translated.y * sin_a, translated.x * sin_a + translated.y * cos_a
        )

        # Translate back
        return rotated + center

    def lerp(self, other: Point, t: float) -> Point:
        """Linear interpolation between two points.

        Args:
            other: Target point
            t: Interpolation parameter (0.0 = self, 1.0 = other)

        Returns:
            Interpolated point
        """
        return Point(self.x + t * (other.x - self.x), self.y + t * (other.y - self.y))

    def is_finite(self) -> bool:
        """Check if coordinates are finite (not inf or nan)."""
        return math.isfinite(self.x) and math.isfinite(self.y)

    def is_zero(self, tolerance: float = 1e-12) -> bool:
        """Check if point is at origin within tolerance."""
        return abs(self.x) < tolerance and abs(self.y) < tolerance

    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple for compatibility."""
        return (self.x, self.y)

    @classmethod
    def from_tuple(cls, coords: Tuple[float | int, float | int]) -> Point:
        """Create point from tuple.

        Args:
            coords: (x, y) coordinate tuple

        Returns:
            New Point instance
        """
        return cls(coords[0], coords[1])

    @classmethod
    def from_polar(cls, radius: float, angle: float) -> Point:
        """Create point from polar coordinates.

        Args:
            radius: Distance from origin
            angle: Angle in radians

        Returns:
            New Point instance
        """
        return cls(radius * math.cos(angle), radius * math.sin(angle))


# Common point constants
ORIGIN = Point(0.0, 0.0)
UNIT_X = Point(1.0, 0.0)
UNIT_Y = Point(0.0, 1.0)


def midpoint(p1: Point, p2: Point) -> Point:
    """Calculate midpoint between two points.

    Args:
        p1: First point
        p2: Second point

    Returns:
        Midpoint between p1 and p2
    """
    return Point((p1.x + p2.x) * 0.5, (p1.y + p2.y) * 0.5)


def centroid(points: list[Point]) -> Point:
    """Calculate centroid of multiple points.

    Args:
        points: List of points

    Returns:
        Centroid point

    Raises:
        ValueError: If points list is empty
    """
    if not points:
        raise ValueError("Cannot calculate centroid of empty point list")

    sum_x = sum(p.x for p in points)
    sum_y = sum(p.y for p in points)
    count = len(points)

    return Point(sum_x / count, sum_y / count)
