from __future__ import annotations

"""
Operations service that composes `cad_core` algorithms with the backend repository.

Stub implementation for wiring; extend with concrete operations as features land.
"""

from dataclasses import dataclass
from typing import Optional

from .geom_repo import InMemoryGeomRepo, EntityRef
from .models import PointDTO, SegmentDTO


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

