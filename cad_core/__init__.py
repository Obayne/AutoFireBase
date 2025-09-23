"""CAD Core package (geometry and algorithms).

Contains pure-Python geometry utilities and operations (trim, fillet, extend, snaps).
"""

# Avoid importing submodules with heavy dependencies on import. Expose minimal namespace here.
__all__ = []

# Core operations
from .trim_extend import (
    TrimResult,
    ExtendResult,
    FilletResult,
    Arc,  # Use Arc from trim_extend for fillet operations
    trim_line_to_boundary,
    extend_line_to_boundary,
    trim_multiple_lines,
    extend_multiple_lines,
    break_line_at_points,
    find_line_line_intersections,
    fillet_two_lines,
    fillet_multiple_line_pairs,
)

__all__ = []

