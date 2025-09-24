from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from .models import CircleDTO, PointDTO, SegmentDTO


@dataclass(frozen=True)
class EntityRef:
    kind: str
    id: str


class InMemoryGeomRepo:
    """
    Minimal in-memory repository for geometry primitives.

    - Deterministic ID generation by simple counters per kind
    - No global state; create an instance per use case
    """

    def __init__(self) -> None:
        self._points: dict[str, PointDTO] = {}
        self._segments: dict[str, SegmentDTO] = {}
        self._circles: dict[str, CircleDTO] = {}
        self._counters: dict[str, int] = {"point": 0, "segment": 0, "circle": 0}

    def _next_id(self, kind: str) -> str:
        n = self._counters[kind] + 1
        self._counters[kind] = n
        return f"{kind}:{n}"

    # CRUD: points
    def add_point(self, p: PointDTO) -> EntityRef:
        eid = self._next_id("point")
        self._points[eid] = p
        return EntityRef("point", eid)

    def get_point(self, eid: str) -> PointDTO | None:
        return self._points.get(eid)

    def update_point(self, eid: str, p: PointDTO) -> bool:
        if eid in self._points:
            self._points[eid] = p
            return True
        return False

    def iter_points(self) -> Iterator[tuple[str, PointDTO]]:
        return iter(self._points.items())

    # CRUD: segments
    def add_segment(self, s: SegmentDTO) -> EntityRef:
        eid = self._next_id("segment")
        self._segments[eid] = s
        return EntityRef("segment", eid)

    def get_segment(self, eid: str) -> SegmentDTO | None:
        return self._segments.get(eid)

    def update_segment(self, eid: str, s: SegmentDTO) -> bool:
        if eid in self._segments:
            self._segments[eid] = s
            return True
        return False

    def iter_segments(self) -> Iterator[tuple[str, SegmentDTO]]:
        return iter(self._segments.items())

    # CRUD: circles
    def add_circle(self, c: CircleDTO) -> EntityRef:
        eid = self._next_id("circle")
        self._circles[eid] = c
        return EntityRef("circle", eid)

    def get_circle(self, eid: str) -> CircleDTO | None:
        return self._circles.get(eid)

    def update_circle(self, eid: str, c: CircleDTO) -> bool:
        if eid in self._circles:
            self._circles[eid] = c
            return True
        return False

    def iter_circles(self) -> Iterator[tuple[str, CircleDTO]]:
        return iter(self._circles.items())
