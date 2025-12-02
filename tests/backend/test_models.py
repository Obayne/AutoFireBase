"""Tests for backend DTOs (data transfer objects)."""

import pytest

from backend.models import CircleDTO, FilletArcDTO, PointDTO, SegmentDTO


class TestPointDTO:
    """Test PointDTO dataclass."""

    def test_creation(self):
        """Test creating a PointDTO."""
        p = PointDTO(x=10.0, y=20.0)
        assert p.x == 10.0
        assert p.y == 20.0

    def test_equality(self):
        """Test PointDTO equality comparison."""
        p1 = PointDTO(x=5.0, y=10.0)
        p2 = PointDTO(x=5.0, y=10.0)
        p3 = PointDTO(x=5.0, y=11.0)

        assert p1 == p2
        assert p1 != p3

    def test_frozen(self):
        """Test PointDTO is immutable (frozen)."""
        p = PointDTO(x=1.0, y=2.0)
        with pytest.raises(AttributeError):
            p.x = 99.0

    def test_hashable(self):
        """Test PointDTO can be used in sets and dict keys."""
        p1 = PointDTO(x=1.0, y=2.0)
        p2 = PointDTO(x=1.0, y=2.0)
        p3 = PointDTO(x=3.0, y=4.0)

        point_set = {p1, p2, p3}
        assert len(point_set) == 2  # p1 and p2 are equal

        point_dict = {p1: "first", p3: "second"}
        assert point_dict[p2] == "first"  # p2 equals p1


class TestSegmentDTO:
    """Test SegmentDTO dataclass."""

    def test_creation(self):
        """Test creating a SegmentDTO."""
        a = PointDTO(x=0.0, y=0.0)
        b = PointDTO(x=10.0, y=10.0)
        seg = SegmentDTO(a=a, b=b)

        assert seg.a == a
        assert seg.b == b

    def test_equality(self):
        """Test SegmentDTO equality comparison."""
        s1 = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(10, 10))
        s2 = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(10, 10))
        s3 = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(5, 5))

        assert s1 == s2
        assert s1 != s3

    def test_frozen(self):
        """Test SegmentDTO is immutable (frozen)."""
        seg = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(1, 1))
        with pytest.raises(AttributeError):
            seg.a = PointDTO(99, 99)

    def test_hashable(self):
        """Test SegmentDTO can be used in sets and dict keys."""
        s1 = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(1, 1))
        s2 = SegmentDTO(a=PointDTO(0, 0), b=PointDTO(1, 1))

        seg_set = {s1, s2}
        assert len(seg_set) == 1  # s1 and s2 are equal


class TestCircleDTO:
    """Test CircleDTO dataclass."""

    def test_creation(self):
        """Test creating a CircleDTO."""
        center = PointDTO(x=5.0, y=5.0)
        circ = CircleDTO(center=center, r=10.0)

        assert circ.center == center
        assert circ.r == 10.0

    def test_equality(self):
        """Test CircleDTO equality comparison."""
        c1 = CircleDTO(center=PointDTO(0, 0), r=5.0)
        c2 = CircleDTO(center=PointDTO(0, 0), r=5.0)
        c3 = CircleDTO(center=PointDTO(0, 0), r=10.0)

        assert c1 == c2
        assert c1 != c3

    def test_frozen(self):
        """Test CircleDTO is immutable (frozen)."""
        circ = CircleDTO(center=PointDTO(0, 0), r=5.0)
        with pytest.raises(AttributeError):
            circ.r = 99.0

    def test_hashable(self):
        """Test CircleDTO can be used in sets and dict keys."""
        c1 = CircleDTO(center=PointDTO(0, 0), r=5.0)
        c2 = CircleDTO(center=PointDTO(0, 0), r=5.0)

        circ_set = {c1, c2}
        assert len(circ_set) == 1


class TestFilletArcDTO:
    """Test FilletArcDTO dataclass."""

    def test_creation(self):
        """Test creating a FilletArcDTO."""
        center = PointDTO(x=5.0, y=5.0)
        t1 = PointDTO(x=0.0, y=5.0)
        t2 = PointDTO(x=5.0, y=0.0)
        fillet = FilletArcDTO(center=center, r=5.0, t1=t1, t2=t2)

        assert fillet.center == center
        assert fillet.r == 5.0
        assert fillet.t1 == t1
        assert fillet.t2 == t2

    def test_equality(self):
        """Test FilletArcDTO equality comparison."""
        f1 = FilletArcDTO(center=PointDTO(0, 0), r=5.0, t1=PointDTO(5, 0), t2=PointDTO(0, 5))
        f2 = FilletArcDTO(center=PointDTO(0, 0), r=5.0, t1=PointDTO(5, 0), t2=PointDTO(0, 5))
        f3 = FilletArcDTO(
            center=PointDTO(0, 0), r=10.0, t1=PointDTO(5, 0), t2=PointDTO(0, 5)  # different radius
        )

        assert f1 == f2
        assert f1 != f3

    def test_frozen(self):
        """Test FilletArcDTO is immutable (frozen)."""
        fillet = FilletArcDTO(center=PointDTO(0, 0), r=5.0, t1=PointDTO(5, 0), t2=PointDTO(0, 5))
        with pytest.raises(AttributeError):
            fillet.r = 99.0

    def test_hashable(self):
        """Test FilletArcDTO can be used in sets and dict keys."""
        f1 = FilletArcDTO(center=PointDTO(0, 0), r=5.0, t1=PointDTO(5, 0), t2=PointDTO(0, 5))
        f2 = FilletArcDTO(center=PointDTO(0, 0), r=5.0, t1=PointDTO(5, 0), t2=PointDTO(0, 5))

        fillet_set = {f1, f2}
        assert len(fillet_set) == 1
