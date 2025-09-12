from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from .lines import Line, Point, intersection_line_line


def _len(v: Point) -> float:
    return math.hypot(v.x, v.y)


def _norm(v: Point) -> Point:
    l = _len(v)
    if l <= 0.0:
        return Point(0.0, 0.0)
    return Point(v.x / l, v.y / l)


def _sub(a: Point, b: Point) -> Point:
    return Point(a.x - b.x, a.y - b.y)


def _add(a: Point, b: Point) -> Point:
    return Point(a.x + b.x, a.y + b.y)


def _scale(v: Point, s: float) -> Point:
    return Point(v.x * s, v.y * s)


def _dot(a: Point, b: Point) -> float:
    return a.x * b.x + a.y * b.y


def fillet_line_line(l1: Line, l2: Line, radius: float, tol: float = 1e-9) -> Optional[Tuple[Point, Point, Point]]:
    """Compute fillet between two infinite lines.

    Returns (p1, p2, center) where p1 lies on l1, p2 lies on l2, and the
    arc of radius `radius` centered at `center` is tangent to both lines.

    None if lines are parallel or radius is non-positive.
    """

    if radius <= tol:
        return None

    I = intersection_line_line(l1, l2, tol=tol)
    if I is None:
        return None

    # Choose directions away from intersection along each line
    # Prefer the endpoint farther from I to get a stable direction.
    def away_dir(L: Line) -> Point:
        d_a = _len(_sub(L.a, I))
        d_b = _len(_sub(L.b, I))
        v = _sub(L.a, I) if d_a >= d_b else _sub(L.b, I)
        return _norm(v)

    u1 = away_dir(l1)
    u2 = away_dir(l2)

    # Clamp dot product to avoid numeric drift
    c = max(-1.0, min(1.0, _dot(u1, u2)))
    theta = math.acos(c)  # angle between directions (0..pi)
    # If nearly collinear or opposite, fillet is ill-defined
    if theta < tol or abs(math.pi - theta) < tol:
        return None

    half = theta / 2.0
    # Distance from intersection to tangent points
    t = radius * math.tan(half)
    # Angle bisector direction
    b = _norm(_add(u1, u2))
    if _len(b) <= tol:
        # u1 ~ -u2 (straight line), no fillet
        return None
    # Center distance from intersection along bisector
    d = radius / math.sin(half)

    p1 = _add(I, _scale(u1, t))
    p2 = _add(I, _scale(u2, t))
    center = _add(I, _scale(b, d))
    return (p1, p2, center)


__all__ = ["fillet_line_line"]

