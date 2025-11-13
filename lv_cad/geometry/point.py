from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

    def to_dict(self) -> dict[str, float | str]:
        return {"type": "Point", "x": float(self.x), "y": float(self.y)}

    @staticmethod
    def from_dict(d: dict[str, float | int | str]) -> Point:
        return Point(x=float(d["x"]), y=float(d["y"]))

    def translate(self, dx: float, dy: float) -> Point:
        return Point(self.x + dx, self.y + dy)


@dataclass(frozen=True, slots=True)
class Vector:
    dx: float
    dy: float

    def to_tuple(self) -> tuple[float, float]:
        return (float(self.dx), float(self.dy))
