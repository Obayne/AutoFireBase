from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Vector:
    dx: float
    dy: float


@dataclass(frozen=True)
class LineSegment:
    a: Point
    b: Point

