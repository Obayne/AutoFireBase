from __future__ import annotations

from dataclasses import dataclass

from .geom_repo import EntityRef, InMemoryGeomRepo
from .models import CircleDTO, PointDTO, SegmentDTO

# Local imports of cad_core inside methods to keep module import light


@dataclass
class OpsService:
    repo: InMemoryGeomRepo

    # Example: create a segment from two points
    def create_segment(self, a: PointDTO, b: PointDTO) -> EntityRef:
        seg = SegmentDTO(a=a, b=b)
        return self.repo.add_segment(seg)

    # Example placeholder for future op (trim/extend)
    def trim_segment_to_line(self, seg_ref: EntityRef, cut_a: PointDTO, cut_b: PointDTO) -> bool:
        _ = (seg_ref, cut_a, cut_b)
        # TODO: integrate with cad_core.trim operation
        return False

    # DTO/Core adapters
    @staticmethod
    def _to_core_point(p: PointDTO):
        from cad_core.lines import Point as CorePoint

        return CorePoint(float(p.x), float(p.y))

    @classmethod
    def _to_core_line(cls, s: SegmentDTO):
        from cad_core.lines import Line as CoreLine

        return CoreLine(cls._to_core_point(s.a), cls._to_core_point(s.b))

    @staticmethod
    def _to_dto_segment(core_line) -> SegmentDTO:
        return SegmentDTO(
            a=PointDTO(x=float(core_line.a.x), y=float(core_line.a.y)),
            b=PointDTO(x=float(core_line.b.x), y=float(core_line.b.y)),
        )

    # Integrated CAD operation: extend segment to circle
    def extend_segment_to_circle(
        self, seg_ref: EntityRef, circle: CircleDTO, end: str = "b"
    ) -> bool:
        """Extend a segment stored in the repo to the nearest circle intersection.

        Updates the segment in-place in the repo on success.
        """
        if seg_ref.kind != "segment":
            return False
        seg = self.repo.get_segment(seg_ref.id)
        if seg is None:
            return False

        from cad_core.circle import Circle as CoreCircle
        from cad_core.lines import extend_segment_to_circle

        core_seg = self._to_core_line(seg)
        core_circ = CoreCircle(self._to_core_point(circle.center), float(circle.r))
        out = extend_segment_to_circle(core_seg, core_circ, end=end)
        if out is None:
            return False
        new_seg = self._to_dto_segment(out)
        return self.repo.update_segment(seg_ref.id, new_seg)
