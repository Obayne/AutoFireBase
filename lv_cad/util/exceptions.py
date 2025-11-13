"""Typed exception hierarchy for lv_cad."""


class InvalidGeometryError(Exception):
    """Raised when input geometry is invalid (degenerate, zero-length, etc.)."""


class TopologyError(Exception):
    """Raised when a requested topological operation cannot be performed."""


class NumericPrecisionError(Exception):
    """Raised when numeric robustness/tolerance constraints are violated."""
