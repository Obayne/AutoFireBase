from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Vector:
    x: float
    y: float

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> Vector:
        length = self.length()
        if length == 0:
            return Vector(0, 0)
        return Vector(self.x / length, self.y / length)

    def dot(self, other: Vector) -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vector) -> float:
        return self.x * other.y - self.y * other.x

    def __add__(self, other: Vector) -> Vector:
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector) -> Vector:
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector:
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Vector:
        return Vector(self.x / scalar, self.y / scalar)