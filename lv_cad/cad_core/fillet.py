"""Fillet utilities migrated into lv_cad (initial copy).

This module provides a minimal, compatible `fillet_line_line` implementation
copied from the legacy `cad_core.fillet`. It intentionally re-uses the
`cad_core.lines` Point/Line types so unit tests can compare results directly
while we migrate types later.
"""

from __future__ import annotations

import math

from cad_core.lines import Line, Point, intersection_line_line


def _len(v: Point) -> float:
    return math.hypot(v.x, v.y)


def _norm(v: Point) -> Point:
    L = _len(v)
    if L <= 0.0:
        return Point(0.0, 0.0)
    return Point(v.x / L, v.y / L)


def _sub(a: Point, b: Point) -> Point:
    return Point(a.x - b.x, a.y - b.y)


def _add(a: Point, b: Point) -> Point:
    return Point(a.x + b.x, a.y + b.y)


def _scale(v: Point, s: float) -> Point:
    return Point(v.x * s, v.y * s)


def _dot(a: Point, b: Point) -> float:
    return a.x * b.x + a.y * b.y


def fillet_line_line(l1: Line, l2: Line, radius: float, tol: float = 1e-9):
    """Compute fillet between two infinite lines.

    Returns (p1, p2, center) where p1 lies on l1, p2 lies on l2, and the
    arc of radius `radius` centered at `center` is tangent to both lines.

    None if lines are parallel or radius is non-positive.
    """

    if radius <= tol:
        return None

    ip = intersection_line_line(l1, l2, tol=tol)
    if ip is None:
        return None

    def away_dir(L: Line) -> Point:
        d_a = _len(_sub(L.a, ip))
        d_b = _len(_sub(L.b, ip))
        v = _sub(L.b, ip) if d_b >= d_a else _sub(L.a, ip)
        return _norm(v)

    u1 = away_dir(l1)
    u2 = away_dir(l2)

    c = max(-1.0, min(1.0, _dot(u1, u2)))
    theta = math.acos(c)
    if theta < tol or abs(math.pi - theta) < tol:
        return None

    half = theta / 2.0
    t = radius * math.tan(half)
    b = _norm(_add(u1, u2))
    if _len(b) <= tol:
        return None
    d = radius / math.sin(half)

    p1 = _add(ip, _scale(u1, t))
    p2 = _add(ip, _scale(u2, t))
    center = _add(ip, _scale(b, d))
    return (p1, p2, center)


__all__ = ["fillet_line_line"]
