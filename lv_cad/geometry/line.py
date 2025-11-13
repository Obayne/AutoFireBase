from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Line:
    x1: float
    y1: float
    x2: float
    y2: float

    def to_dict(self) -> dict[str, float | str]:
        return {
            "type": "Line",
            "x1": float(self.x1),
            "y1": float(self.y1),
            "x2": float(self.x2),
            "y2": float(self.y2),
        }

    @staticmethod
    def from_dict(d: dict[str, float | int | str]) -> "Line":
        return Line(
            float(d.get("x1", 0.0)),
            float(d.get("y1", 0.0)),
            float(d.get("x2", 0.0)),
            float(d.get("y2", 0.0)),
        )
