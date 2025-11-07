"""Lightweight CAD core replacement (initial).

This module provides a small subset of the original `cad_core` API used by
the application. It is intentionally minimal — just enough to validate the
strangler workflow and run smoke tests. Real, complete implementations will be
added incrementally in follow-up PRs.
"""

from .arc import Arc, arc_from_points
from .commands_clean import CADCommand, CADCommandStack
from .fillet import fillet_line_line
from .lines import Line, Point, intersection_line_line


__all__ = [
    "Point",
    "Line",
    "intersection_line_line",
    "fillet_line_line",
    "Arc",
    "arc_from_points",
    "CADCommand",
    "CADCommandStack",
]
