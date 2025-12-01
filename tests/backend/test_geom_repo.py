"""Tests for backend geometry repository (InMemoryGeomRepo)."""

from backend.geom_repo import EntityRef, InMemoryGeomRepo
from backend.models import PointDTO, SegmentDTO


class TestInMemoryGeomRepo:
    """Test suite for in-memory geometry repository."""

    def test_repo_initialization(self):
        """Test repository initializes with empty storage."""
        repo = InMemoryGeomRepo()
        assert repo is not None

    def test_add_segment(self):
        """Test adding a segment to repository."""
        repo = InMemoryGeomRepo()
        a = PointDTO(x=0.0, y=0.0)
        b = PointDTO(x=10.0, y=10.0)
        seg = SegmentDTO(a=a, b=b)

        ref = repo.add_segment(seg)

        assert isinstance(ref, EntityRef)
        assert ref.id is not None
        assert ref.kind == "segment"

    def test_get_segment(self):
        """Test retrieving a segment from repository."""
        repo = InMemoryGeomRepo()
        a = PointDTO(x=5.0, y=5.0)
        b = PointDTO(x=15.0, y=15.0)
        seg = SegmentDTO(a=a, b=b)

        ref = repo.add_segment(seg)
        retrieved = repo.get_segment(ref.id)

        assert retrieved is not None
        assert retrieved.a.x == 5.0
        assert retrieved.a.y == 5.0
        assert retrieved.b.x == 15.0
        assert retrieved.b.y == 15.0

    def test_get_nonexistent_segment(self):
        """Test retrieving a non-existent segment returns None."""
        repo = InMemoryGeomRepo()

        result = repo.get_segment("segment:999")

        assert result is None

    def test_multiple_segments(self):
        """Test adding and retrieving multiple segments."""
        repo = InMemoryGeomRepo()

        seg1 = SegmentDTO(a=PointDTO(x=0.0, y=0.0), b=PointDTO(x=10.0, y=0.0))
        seg2 = SegmentDTO(a=PointDTO(x=0.0, y=0.0), b=PointDTO(x=0.0, y=10.0))
        seg3 = SegmentDTO(a=PointDTO(x=10.0, y=0.0), b=PointDTO(x=10.0, y=10.0))

        ref1 = repo.add_segment(seg1)
        ref2 = repo.add_segment(seg2)
        ref3 = repo.add_segment(seg3)

        # Verify all can be retrieved
        assert repo.get_segment(ref1.id) is not None
        assert repo.get_segment(ref2.id) is not None
        assert repo.get_segment(ref3.id) is not None

        # Verify correct data
        retrieved1 = repo.get_segment(ref1.id)
        assert retrieved1.b.x == 10.0
        assert retrieved1.b.y == 0.0

    def test_entity_ref_uniqueness(self):
        """Test that each segment gets a unique entity reference."""
        repo = InMemoryGeomRepo()

        seg1 = SegmentDTO(a=PointDTO(x=0.0, y=0.0), b=PointDTO(x=1.0, y=1.0))
        seg2 = SegmentDTO(a=PointDTO(x=0.0, y=0.0), b=PointDTO(x=1.0, y=1.0))

        ref1 = repo.add_segment(seg1)
        ref2 = repo.add_segment(seg2)

        assert ref1.id != ref2.id
