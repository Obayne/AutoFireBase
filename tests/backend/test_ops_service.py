"""Tests for backend OpsService (geometry operations service)."""

from backend.geom_repo import EntityRef, InMemoryGeomRepo
from backend.models import PointDTO
from backend.ops_service import OpsService


class TestOpsService:
    """Test suite for OpsService."""

    def test_create_segment_basic(self):
        """Test creating a segment via OpsService."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        a = PointDTO(x=0.0, y=0.0)
        b = PointDTO(x=10.0, y=10.0)

        ref = service.create_segment(a, b)

        assert isinstance(ref, EntityRef)
        assert ref.kind == "segment"
        assert ref.id.startswith("segment:")

        # Verify it was stored in repo
        stored = repo.get_segment(ref.id)
        assert stored is not None
        assert stored.a == a
        assert stored.b == b

    def test_create_multiple_segments(self):
        """Test creating multiple segments."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        ref1 = service.create_segment(PointDTO(0, 0), PointDTO(1, 1))
        ref2 = service.create_segment(PointDTO(2, 2), PointDTO(3, 3))

        assert ref1.id != ref2.id
        assert repo.get_segment(ref1.id) is not None
        assert repo.get_segment(ref2.id) is not None

    def test_trim_segment_to_line_not_implemented(self):
        """Test trim_segment_to_line returns False (not yet implemented)."""
        repo = InMemoryGeomRepo()
        service = OpsService(repo=repo)

        seg_ref = service.create_segment(PointDTO(0, 0), PointDTO(10, 10))
        result = service.trim_segment_to_line(seg_ref, cut_a=PointDTO(5, 0), cut_b=PointDTO(5, 10))

        assert result is False  # TODO placeholder returns False
