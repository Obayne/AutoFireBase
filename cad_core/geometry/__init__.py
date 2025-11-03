"""Geometry module for professional 2D CAD operations.

This module provides high-precision 2D geometry primitives and operations
for CAD applications, including points, lines, arcs, and geometric algorithms.
"""

from .point import ORIGIN, UNIT_X, UNIT_Y, Point, centroid, midpoint

__all__ = [
    "Point",
    "ORIGIN",
    "UNIT_X",
    "UNIT_Y",
    "midpoint",
    "centroid",
]
