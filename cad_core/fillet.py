from __future__ import annotations

import math

from .arc import arc_from_points
from .circle import Circle
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


def fillet_line_line(
    l1: Line, l2: Line, radius: float, tol: float = 1e-9
) -> tuple[Point, Point, Point] | None:
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
        # Prefer endpoint b when distances are equal to avoid sign flip
        v = _sub(L.b, I) if d_b >= d_a else _sub(L.a, I)
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


def fillet_line_circle(line: Line, circle: Circle, radius: float, tol: float = 1e-9):
    """Fillet between an infinite line and a circle (arc). Returns candidates.

    Returns a list of (p_line, p_circle, center) tuples representing possible
    fillet arcs of the given radius tangent to both.
    """
    if radius <= tol:
        return []

    # Centers must be at distance r from the line (two offsets) and at distance
    # (R ± r) from the circle center. Intersect those loci to find candidates.
    # Line in point-direction form: P = A + t*(B-A). A normal vector n gives
    # offset points at A + n*r and B + n*r, etc.
    A, B = line.a, line.b
    ux = B.x - A.x
    uy = B.y - A.y
    L = math.hypot(ux, uy)
    if L <= tol:
        return []
    # Unit normal candidates (left/right)
    nx, ny = -uy / L, ux / L
    normals = [(nx, ny), (-nx, -ny)]

    results = []
    for nx, ny in normals:
        # Offset line for centers: any point C must satisfy n·(C - A) = r
        # We parametrize center candidates along the original line direction
        # and solve intersection with the circle of radius R' around circle.center.
        # In practice, compute projections by intersecting the offset line with
        # the circle of radius (R ± r), where sign depends on internal/external tangency.
        for Rprime in (abs(circle.radius - radius), circle.radius + radius):
            # Offset line point P0 = A + n*r; direction d = (ux, uy)/L
            px = A.x + nx * radius
            py = A.y + ny * radius
            dx = ux / L
            dy = uy / L
            # Intersect parametric line P(t) with circle centered at C0 with radius Rprime
            # Solve |(P0 + t*d) - C0|^2 = Rprime^2
            cx0 = circle.center.x
            cy0 = circle.center.y
            sx = px - cx0
            sy = py - cy0
            Aq = dx * dx + dy * dy
            Bq = 2 * (sx * dx + sy * dy)
            Cq = sx * sx + sy * sy - Rprime * Rprime
            disc = Bq * Bq - 4 * Aq * Cq
            if disc < -tol:
                continue
            if abs(disc) <= tol:
                ts = [-Bq / (2 * Aq)]
            else:
                root = math.sqrt(max(0.0, disc))
                ts = [(-Bq - root) / (2 * Aq), (-Bq + root) / (2 * Aq)]
            for t in ts:
                cx = px + dx * t
                cy = py + dy * t
                center = Point(cx, cy)
                # Tangent point on line is foot of perpendicular from center
                # to the original (unoffset) line
                # projection t0 = ((center-A)·(B-A)) / |B-A|^2
                t0 = ((center.x - A.x) * ux + (center.y - A.y) * uy) / (L * L)
                plx = A.x + ux * t0
                ply = A.y + uy * t0
                p_line = Point(plx, ply)
                # Tangent point on circle in direction from circle.center to center
                vxc = cx - circle.center.x
                vyc = cy - circle.center.y
                vlen = math.hypot(vxc, vyc)
                if vlen <= tol:
                    continue
                pcx = circle.center.x + (circle.radius / vlen) * vxc
                pcy = circle.center.y + (circle.radius / vlen) * vyc
                p_circ = Point(pcx, pcy)
                results.append((p_line, p_circ, center))
    return results


def fillet_circle_circle(c1: Circle, c2: Circle, radius: float, tol: float = 1e-9):
    """Fillet between two circles (arcs). Returns centers and tangent points.

    Returns list of (p1, p2, center) candidates, where p1 on c1, p2 on c2.
    """
    if radius <= tol:
        return []
    results = []
    # Centers Cf must satisfy |Cf - c1| = r1' and |Cf - c2| = r2', for combinations of
    # r' = |R ± radius| (internal/external tangency).
    for r1p in (abs(c1.radius - radius), c1.radius + radius):
        for r2p in (abs(c2.radius - radius), c2.radius + radius):
            # Intersect circles centered at c1.center and c2.center with radii r1p and r2p
            cc1 = Circle(c1.center, r1p)
            cc2 = Circle(c2.center, r2p)
            from .circle import circle_circle_intersections as cc_inter

            centers = cc_inter(cc1, cc2, tol=tol)
            for center in centers:
                # Tangent points towards center
                v1x = center.x - c1.center.x
                v1y = center.y - c1.center.y
                l1 = math.hypot(v1x, v1y)
                if l1 <= tol:
                    continue
                p1 = Point(
                    c1.center.x + (c1.radius / l1) * v1x,
                    c1.center.y + (c1.radius / l1) * v1y,
                )
                v2x = center.x - c2.center.x
                v2y = center.y - c2.center.y
                l2 = math.hypot(v2x, v2y)
                if l2 <= tol:
                    continue
                p2 = Point(
                    c2.center.x + (c2.radius / l2) * v2x,
                    c2.center.y + (c2.radius / l2) * v2y,
                )
                results.append((p1, p2, center))
    return results


def fillet_segments_line_line(
    seg1: Line, seg2: Line, pick1: Point, pick2: Point, radius: float, tol: float = 1e-9
):
    """Fillet two line segments with given pick points and radius.

    Returns (new_seg1, new_seg2, arc) or None if fillet cannot be constructed.
    - pick points determine which endpoints to move on each segment.
    - arc connects the two tangent points with a short arc.
    """
    res = fillet_line_line(seg1, seg2, radius, tol=tol)
    if res is None:
        return None
    p1, p2, center = res

    # Choose which endpoint to move based on proximity to user pick
    def move_endpoint(seg: Line, pick: Point, target: Point) -> Line:
        d_a = (pick.x - seg.a.x) ** 2 + (pick.y - seg.a.y) ** 2
        d_b = (pick.x - seg.b.x) ** 2 + (pick.y - seg.b.y) ** 2
        if d_a <= d_b:
            return Line(a=target, b=seg.b)
        return Line(a=seg.a, b=target)

    n1 = move_endpoint(seg1, pick1, p1)
    n2 = move_endpoint(seg2, pick2, p2)

    arc = arc_from_points(center, p1, p2, prefer_short=True)
    return (n1, n2, arc)


__all__ += [
    "fillet_line_circle",
    "fillet_circle_circle",
    "fillet_segments_line_line",
]
