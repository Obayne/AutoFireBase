"""lv_cad – extracted CAD geometry/operations package (parity-first).

Public surface intentionally small during migration.
"""

from . import geometry, operations, util
from .geometry.point import Point, Vector  # re-export convenience
from .geometry.line import Line
from .geometry.arc import Arc
from .operations.fillet import fillet  # parity wrapper

__all__ = [
    "geometry",
    "operations",
    "util",
    "Point",
    "Vector",
    "Line",
    "Arc",
    "fillet",
]

try:
    from importlib.metadata import version as _version
except ModuleNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
else:  # pragma: no cover
    from importlib.metadata import PackageNotFoundError

    try:
        __version__ = _version("lv_cad")
    except PackageNotFoundError:
        __version__ = "0.0.0"
