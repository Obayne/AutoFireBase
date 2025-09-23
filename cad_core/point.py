from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def almost_equals(self, other: "Point", tol: float = 1e-9) -> bool:
        return abs(self.x - other.x) <= tol and abs(self.y - other.y) <= tol

    def move(self, dx: float, dy: float) -> "Point":
        return Point(self.x + dx, self.y + dy)

