from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..geometry.point import Point


def _try_legacy() -> Any | None:
    """Return a legacy offset function if available, else None.

    Tries a few likely legacy locations. This is parity-first during migration.
    """
    # Candidates: cad_core.offset.offset_polyline, cad_core.offset, cad_core.operations.offset
    import importlib

    candidates: list[tuple[str, str]] = [
        ("cad_core.offset", "offset_polyline"),
        ("cad_core.offset", "offset"),
        ("cad_core.operations.offset", "offset_polyline"),
    ]
    for mod, attr in candidates:
        try:
            m = importlib.import_module(mod)
            fn = getattr(m, attr, None)
            if callable(fn):
                return fn
        except ModuleNotFoundError:
            continue
        except AttributeError:
            continue
    return None


def offset_polyline(points: Sequence[Point], distance: float) -> list[Point]:
    """Parity-first offset for a 2D polyline.

    Delegates to legacy implementation if present; raises ImportError otherwise.
    Returns a list of Points representing the offset path.
    """
    legacy = _try_legacy()
    if legacy is None:
        raise ImportError("Legacy offset implementation not found")

    # Convert to legacy-friendly tuples if needed
    in_pts = [(p.x, p.y) for p in points]
    out = legacy(in_pts, float(distance))
    if not out:
        return []
    # Accept either sequence of tuples or dict-like with x,y
    result: list[Point] = []
    for v in out:
        if isinstance(v, dict):
            result.append(Point(float(v.get("x", 0.0)), float(v.get("y", 0.0))))
        else:
            x, y = v
            result.append(Point(float(x), float(y)))
    return result
