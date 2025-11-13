"""Fillet wrappers (parity-first).

These delegate to legacy cad_core.fillet implementations until lv_cad
provides native versions. This keeps behavior stable during migration.
"""

from __future__ import annotations

from math import acos, isfinite, sin, tan
from typing import Any

from ..geometry.point import Point

try:  # legacy fallback imports
    from cad_core.fillet import (
        fillet_circle_circle as _legacy_fillet_circle_circle,
    )
    from cad_core.fillet import (
        fillet_line_circle as _legacy_fillet_line_circle,
    )
    from cad_core.fillet import (
        fillet_line_line as _legacy_fillet_line_line,
    )
except ImportError:  # pragma: no cover
    _legacy_fillet_line_line = None  # type: ignore[assignment]
    _legacy_fillet_line_circle = None  # type: ignore[assignment]
    _legacy_fillet_circle_circle = None  # type: ignore[assignment]

# unified convenience wrapper (example signature kept simple for now)


def fillet(*args: Any, **kwargs: Any):  # noqa: ANN401 - intentionally generic
    """General fillet convenience wrapper.

    For now just forwards to line-line variant if available.
    """
    if _legacy_fillet_line_line is None:  # pragma: no cover
        raise RuntimeError("Legacy fillet implementation unavailable.")
    return _legacy_fillet_line_line(*args, **kwargs)


def fillet_line_line(*args: Any, **kwargs: Any):  # noqa: ANN401
    if _legacy_fillet_line_line is None:  # pragma: no cover
        raise RuntimeError("Legacy fillet_line_line unavailable.")
    return _legacy_fillet_line_line(*args, **kwargs)


def fillet_line_circle(*args: Any, **kwargs: Any):  # noqa: ANN401
    if _legacy_fillet_line_circle is None:  # pragma: no cover
        raise RuntimeError("Legacy fillet_line_circle unavailable.")
    return _legacy_fillet_line_circle(*args, **kwargs)


def fillet_circle_circle(*args: Any, **kwargs: Any):  # noqa: ANN401
    if _legacy_fillet_circle_circle is None:  # pragma: no cover
        raise RuntimeError("Legacy fillet_circle_circle unavailable.")
    return _legacy_fillet_circle_circle(*args, **kwargs)


# -------------------- Native implementations (opt-in, API stable) --------------------


def _dot(ax: float, ay: float, bx: float, by: float) -> float:
    return ax * bx + ay * by


def _norm(ax: float, ay: float) -> float:
    return (ax * ax + ay * ay) ** 0.5


def _cross(ax: float, ay: float, bx: float, by: float) -> float:
    return ax * by - ay * bx


def _clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _line_intersection(a1: Point, a2: Point, b1: Point, b2: Point) -> Point | None:
    r_x, r_y = a2.x - a1.x, a2.y - a1.y
    s_x, s_y = b2.x - b1.x, b2.y - b1.y
    denom = _cross(r_x, r_y, s_x, s_y)
    if abs(denom) < 1e-12:
        return None
    t = _cross(b1.x - a1.x, b1.y - a1.y, s_x, s_y) / denom
    return Point(a1.x + t * r_x, a1.y + t * r_y)


def fillet_line_line_native(
    a1: Point, a2: Point, b1: Point, b2: Point, radius: float
) -> tuple[Point, Point, Point] | None:
    """Compute a 2D fillet arc tangent to two lines.

    Returns (tangent_on_A, center, tangent_on_B) as Points, or None if no fillet.
    The two lines are defined by points (a1,a2) and (b1,b2). Lines are treated as infinite;
    the chosen tangency lies along the rays that go away from the intersection towards the
    farther endpoint on each line, providing a stable external-corner fillet without pick points.
    """
    if radius <= 0.0:
        return None

    I = _line_intersection(a1, a2, b1, b2)
    if I is None:
        return None

    # Choose direction on each line from intersection toward the farther endpoint
    def dir_from_intersection(p: Point, q: Point) -> tuple[float, float]:
        dp_x, dp_y = p.x - I.x, p.y - I.y
        dq_x, dq_y = q.x - I.x, q.y - I.y
        if _norm(dp_x, dp_y) >= _norm(dq_x, dq_y):
            vx, vy = dp_x, dp_y
        else:
            vx, vy = dq_x, dq_y
        n = _norm(vx, vy)
        if n < 1e-12:
            return (0.0, 0.0)
        return (vx / n, vy / n)

    ux, uy = dir_from_intersection(a1, a2)
    vx, vy = dir_from_intersection(b1, b2)

    if _norm(ux, uy) < 1e-12 or _norm(vx, vy) < 1e-12:
        return None

    # Orient directions to form the smaller interior angle (maximize dot product)
    if _dot(ux, uy, vx, vy) < 0.0:
        ux, uy = -ux, -uy

    # Angle between rays
    c = _clamp(_dot(ux, uy, vx, vy), -1.0, 1.0)
    theta = acos(c)
    if not isfinite(theta) or theta <= 1e-6 or theta >= 3.1415925 - 1e-6:
        return None

    half = 0.5 * theta
    t = radius / tan(half)
    s = radius / sin(half)

    # Tangent points along each ray
    T1 = Point(I.x + ux * t, I.y + uy * t)
    T2 = Point(I.x + vx * t, I.y + vy * t)

    # Center along the angle bisector (normalized sum of unit directions)
    wx, wy = ux + vx, uy + vy
    wn = _norm(wx, wy)
    if wn < 1e-12:
        return None
    wx, wy = wx / wn, wy / wn
    C = Point(I.x + wx * s, I.y + wy * s)

    return (T1, C, T2)
