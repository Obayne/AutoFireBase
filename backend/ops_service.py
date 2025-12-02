from __future__ import annotations

import logging
from dataclasses import dataclass

from .geom_repo import EntityRef, InMemoryGeomRepo
from .models import PointDTO, SegmentDTO

logger = logging.getLogger(__name__)


@dataclass
class OpsService:
    repo: InMemoryGeomRepo

    # Example: create a segment from two points
    def create_segment(self, a: PointDTO, b: PointDTO) -> EntityRef:
        seg = SegmentDTO(a=a, b=b)
        return self.repo.add_segment(seg)

    # Enhanced geometry operations for CAD integration

    def trim_segment_by_cutter(self, segment: SegmentDTO, cutter: SegmentDTO) -> SegmentDTO:
        """
        Trim segment by a cutter line

        Args:
            segment: The segment to trim
            cutter: The cutting line

        Returns:
            Trimmed segment
        """
        logger.info("Executing trim operation")

        # Find intersection point
        intersection = self._find_line_intersection(segment, cutter)

        if intersection:
            # Trim to intersection point
            return SegmentDTO(a=segment.a, b=intersection)
        else:
            # No intersection, return original segment
            logger.warning("No intersection found for trim operation")
            return segment

    def extend_segment_to_intersection(self, segment: SegmentDTO, target: SegmentDTO) -> SegmentDTO:
        """
        Extend segment to intersect with target line

        Args:
            segment: The segment to extend
            target: The target line to intersect

        Returns:
            Extended segment
        """
        logger.info("Executing extend operation")

        # Calculate extended line from segment
        extended_end = self._extend_line(segment, 100.0)  # Extend by 100 units
        extended_segment = SegmentDTO(a=segment.a, b=extended_end)

        # Find intersection with target
        intersection = self._find_line_intersection(extended_segment, target)

        if intersection:
            return SegmentDTO(a=segment.a, b=intersection)
        else:
            logger.warning("No intersection found for extend operation")
            return segment

    def intersect_segments(self, segments: list[SegmentDTO]) -> list[PointDTO]:
        """
        Find all intersection points between segments

        Args:
            segments: List of segments to check for intersections

        Returns:
            List of intersection points
        """
        logger.info(f"Finding intersections for {len(segments)} segments")

        intersections = []

        for i in range(len(segments)):
            for j in range(i + 1, len(segments)):
                intersection = self._find_line_intersection(segments[i], segments[j])
                if intersection:
                    intersections.append(intersection)

        logger.info(f"Found {len(intersections)} intersection points")
        return intersections

    def _find_line_intersection(self, seg1: SegmentDTO, seg2: SegmentDTO) -> PointDTO | None:
        """Find intersection point of two line segments"""
        # Line 1: seg1.a to seg1.b
        x1, y1 = seg1.a.x, seg1.a.y
        x2, y2 = seg1.b.x, seg1.b.y

        # Line 2: seg2.a to seg2.b
        x3, y3 = seg2.a.x, seg2.a.y
        x4, y4 = seg2.b.x, seg2.b.y  # Calculate denominators
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if abs(denom) < 1e-10:  # Lines are parallel
            return None

        # Calculate intersection parameters
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        # Check if intersection is within both segments
        if 0 <= t <= 1 and 0 <= u <= 1:
            # Calculate intersection point
            px = x1 + t * (x2 - x1)
            py = y1 + t * (y2 - y1)
            return PointDTO(x=px, y=py)

        return None

    def _extend_line(self, segment: SegmentDTO, distance: float) -> PointDTO:
        """Extend a line segment by a given distance"""
        # Calculate direction vector
        dx = segment.b.x - segment.a.x
        dy = segment.b.y - segment.a.y

        # Calculate length
        length = (dx**2 + dy**2) ** 0.5

        if length == 0:
            return segment.b

        # Normalize direction vector
        unit_dx = dx / length
        unit_dy = dy / length

        # Extend by distance
        new_x = segment.b.x + unit_dx * distance
        new_y = segment.b.y + unit_dy * distance

        return PointDTO(x=new_x, y=new_y)

    # Legacy method for compatibility
    def trim_segment_to_line(self, seg_ref: EntityRef, cut_a: PointDTO, cut_b: PointDTO) -> bool:
        _ = (seg_ref, cut_a, cut_b)
        # TODO: integrate with cad_core.trim operation
        return False
