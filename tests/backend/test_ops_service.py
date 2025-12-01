"""Tests for backend operations service (OpsService)."""

from backend.geom_repo import InMemoryGeomRepo
from backend.models import PointDTO, SegmentDTO
from backend.ops_service import OpsService


class TestOpsService:
    """Test suite for OpsService geometry operations."""

    def test_service_initialization(self):
        """Test service initializes with repository."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        assert service.repo is repo

    def test_create_segment(self):
        """Test creating a segment via service."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        a = PointDTO(x=0.0, y=0.0)
        b = PointDTO(x=10.0, y=10.0)

        ref = service.create_segment(a, b)

        assert ref is not None
        segment = repo.get_segment(ref.id)
        assert segment.a == a
        assert segment.b == b

    def test_trim_segment_by_cutter_with_intersection(self):
        """Test trimming a segment that intersects with cutter."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        # Horizontal segment from (0,5) to (10,5)
        segment = SegmentDTO(a=PointDTO(x=0.0, y=5.0), b=PointDTO(x=10.0, y=5.0))

        # Vertical cutter at x=5
        cutter = SegmentDTO(a=PointDTO(x=5.0, y=0.0), b=PointDTO(x=5.0, y=10.0))

        result = service.trim_segment_by_cutter(segment, cutter)

        assert result is not None
        assert result.a.x == 0.0
        assert result.a.y == 5.0
        # Should be trimmed to intersection point (5,5)
        assert abs(result.b.x - 5.0) < 1e-9
        assert abs(result.b.y - 5.0) < 1e-9

    def test_trim_segment_no_intersection(self):
        """Test trimming segments that don't intersect."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        # Horizontal segment
        segment = SegmentDTO(a=PointDTO(x=0.0, y=0.0), b=PointDTO(x=10.0, y=0.0))

        # Parallel horizontal cutter (no intersection)
        cutter = SegmentDTO(a=PointDTO(x=0.0, y=5.0), b=PointDTO(x=10.0, y=5.0))

        result = service.trim_segment_by_cutter(segment, cutter)

        # Should return original segment when no intersection
        assert result.a == segment.a
        assert result.b == segment.b

    def test_extend_segment_to_intersection(self):
        """Test extending a segment to intersect with target."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        # Short horizontal segment
        segment = SegmentDTO(a=PointDTO(x=0.0, y=5.0), b=PointDTO(x=3.0, y=5.0))

        # Vertical target at x=10
        target = SegmentDTO(a=PointDTO(x=10.0, y=0.0), b=PointDTO(x=10.0, y=10.0))

        result = service.extend_segment_to_intersection(segment, target)

        assert result is not None
        assert result.a.x == 0.0
        assert result.a.y == 5.0
        # Should be extended to intersection (10,5)
        assert abs(result.b.x - 10.0) < 1e-9
        assert abs(result.b.y - 5.0) < 1e-9

    def test_extend_segment_parallel_lines(self):
        """Test extending segments that are parallel (no intersection)."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        segment = SegmentDTO(a=PointDTO(x=0.0, y=0.0), b=PointDTO(x=10.0, y=0.0))

        target = SegmentDTO(a=PointDTO(x=0.0, y=5.0), b=PointDTO(x=10.0, y=5.0))

        result = service.extend_segment_to_intersection(segment, target)

        # Should return original when lines are parallel
        assert result.a == segment.a
        assert result.b == segment.b

    def test_intersect_segments_crossing(self):
        """Test finding intersection of crossing segments."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        seg1 = SegmentDTO(a=PointDTO(x=0.0, y=0.0), b=PointDTO(x=10.0, y=10.0))

        seg2 = SegmentDTO(a=PointDTO(x=0.0, y=10.0), b=PointDTO(x=10.0, y=0.0))

        intersections = service.intersect_segments([seg1, seg2])

        assert len(intersections) == 1
        # Intersection should be at (5,5)
        assert abs(intersections[0].x - 5.0) < 1e-9
        assert abs(intersections[0].y - 5.0) < 1e-9

    def test_intersect_segments_multiple(self):
        """Test finding multiple intersections."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        # Create a cross pattern
        seg1 = SegmentDTO(a=PointDTO(x=0.0, y=5.0), b=PointDTO(x=10.0, y=5.0))  # Horizontal
        seg2 = SegmentDTO(a=PointDTO(x=5.0, y=0.0), b=PointDTO(x=5.0, y=10.0))  # Vertical
        seg3 = SegmentDTO(a=PointDTO(x=0.0, y=0.0), b=PointDTO(x=10.0, y=10.0))  # Diagonal

        intersections = service.intersect_segments([seg1, seg2, seg3])

        # Should find 3 intersections: seg1-seg2, seg1-seg3, seg2-seg3
        assert len(intersections) == 3

    def test_intersect_segments_none(self):
        """Test with non-intersecting segments."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        seg1 = SegmentDTO(a=PointDTO(x=0.0, y=0.0), b=PointDTO(x=1.0, y=0.0))
        seg2 = SegmentDTO(a=PointDTO(x=0.0, y=5.0), b=PointDTO(x=1.0, y=5.0))

        intersections = service.intersect_segments([seg1, seg2])

        assert len(intersections) == 0
