from __future__ import annotations

from dataclasses import dataclass

from cad_core.lines import Line, Point, trim_line_by_cut

from .geom_repo import EntityRef, InMemoryGeomRepo
from .models import PointDTO, SegmentDTO


def _dto_to_point(p: PointDTO) -> Point:
    """Convert DTO point to cad_core Point."""
    return Point(p.x, p.y)


def _point_to_dto(p: Point) -> PointDTO:
    """Convert cad_core Point to DTO point."""
    return PointDTO(p.x, p.y)


@dataclass
class OpsService:
    repo: InMemoryGeomRepo

    # Example: create a segment from two points
    def create_segment(self, a: PointDTO, b: PointDTO) -> EntityRef:
        seg = SegmentDTO(a=a, b=b)
        return self.repo.add_segment(seg)

    def trim_segment_to_line(
        self, seg_ref: EntityRef, cut_a: PointDTO, cut_b: PointDTO, end: str = "b"
    ) -> bool:
        """Trim a segment to intersection with a cutting line.

        Args:
            seg_ref: Reference to segment in repo
            cut_a: First point of cutting line
            cut_b: Second point of cutting line
            end: Which end to trim ('a' or 'b')

        Returns:
            True if trim succeeded and repo updated, False otherwise
        """
        seg_dto = self.repo.get_segment(seg_ref.id)
        if seg_dto is None:
            return False

        # Convert DTOs to cad_core types
        seg_line = Line(_dto_to_point(seg_dto.a), _dto_to_point(seg_dto.b))
        cutter = Line(_dto_to_point(cut_a), _dto_to_point(cut_b))

        # Perform trim operation
        trimmed = trim_line_by_cut(seg_line, cutter, end=end)
        if trimmed is None:
            return False

        # Convert back to DTO and update repo
        new_seg = SegmentDTO(_point_to_dto(trimmed.a), _point_to_dto(trimmed.b))
        return self.repo.update_segment(seg_ref.id, new_seg)
