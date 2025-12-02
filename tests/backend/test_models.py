"""Tests for backend DTO models (PointDTO, SegmentDTO)."""

from backend.models import PointDTO, SegmentDTO


class TestPointDTO:
    """Test suite for PointDTO model."""

    def test_point_creation(self):
        """Test basic point creation."""
        p = PointDTO(x=10.0, y=20.0)
        assert p.x == 10.0
        assert p.y == 20.0

    def test_point_zero(self):
        """Test point at origin."""
        p = PointDTO(x=0.0, y=0.0)
        assert p.x == 0.0
        assert p.y == 0.0

    def test_point_negative_coordinates(self):
        """Test point with negative coordinates."""
        p = PointDTO(x=-5.5, y=-10.2)
        assert p.x == -5.5
        assert p.y == -10.2

    def test_point_equality(self):
        """Test point equality comparison."""
        p1 = PointDTO(x=1.0, y=2.0)
        p2 = PointDTO(x=1.0, y=2.0)
        p3 = PointDTO(x=1.0, y=3.0)

        assert p1 == p2
        assert p1 != p3


class TestSegmentDTO:
    """Test suite for SegmentDTO model."""

    def test_segment_creation(self):
        """Test basic segment creation."""
        a = PointDTO(x=0.0, y=0.0)
        b = PointDTO(x=10.0, y=10.0)
        seg = SegmentDTO(a=a, b=b)

        assert seg.a == a
        assert seg.b == b

    def test_segment_horizontal(self):
        """Test horizontal segment."""
        a = PointDTO(x=0.0, y=5.0)
        b = PointDTO(x=10.0, y=5.0)
        seg = SegmentDTO(a=a, b=b)

        assert seg.a.y == seg.b.y
        assert seg.a.x < seg.b.x

    def test_segment_vertical(self):
        """Test vertical segment."""
        a = PointDTO(x=5.0, y=0.0)
        b = PointDTO(x=5.0, y=10.0)
        seg = SegmentDTO(a=a, b=b)

        assert seg.a.x == seg.b.x
        assert seg.a.y < seg.b.y

    def test_segment_diagonal(self):
        """Test diagonal segment."""
        a = PointDTO(x=0.0, y=0.0)
        b = PointDTO(x=5.0, y=5.0)
        seg = SegmentDTO(a=a, b=b)

        assert seg.a.x != seg.b.x
        assert seg.a.y != seg.b.y

    def test_segment_equality(self):
        """Test segment equality comparison."""
        a1 = PointDTO(x=0.0, y=0.0)
        b1 = PointDTO(x=10.0, y=10.0)
        a2 = PointDTO(x=0.0, y=0.0)
        b2 = PointDTO(x=10.0, y=10.0)

        seg1 = SegmentDTO(a=a1, b=b1)
        seg2 = SegmentDTO(a=a2, b=b2)

        assert seg1 == seg2
