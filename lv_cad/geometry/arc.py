from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Arc:
    cx: float
    cy: float
    r: float
    start_deg: float
    span_deg: float

    def to_dict(self) -> dict[str, float | str]:
        return {
            "type": "Arc",
            "cx": float(self.cx),
            "cy": float(self.cy),
            "r": float(self.r),
            "start_deg": float(self.start_deg),
            "span_deg": float(self.span_deg),
        }

    @staticmethod
    def from_dict(d: dict[str, float | int | str]) -> "Arc":
        return Arc(
            float(d.get("cx", 0.0)),
            float(d.get("cy", 0.0)),
            float(d.get("r", 0.0)),
            float(d.get("start_deg", 0.0)),
            float(d.get("span_deg", 0.0)),
        )
