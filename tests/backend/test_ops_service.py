from backend.geom_repo import InMemoryGeomRepo
from backend.models import PointDTO, SegmentDTO
from backend.ops_service import OpsService


def test_create_segment():
    """Test creating a segment through OpsService."""
    repo = InMemoryGeomRepo()
    service = OpsService(repo)

    p1 = PointDTO(0.0, 0.0)
    p2 = PointDTO(10.0, 0.0)

    seg_ref = service.create_segment(p1, p2)
    assert seg_ref.kind == "segment"
    assert seg_ref.id.startswith("segment:")

    # Verify segment was stored in repo
    seg = repo.get_segment(seg_ref.id)
    assert seg == SegmentDTO(p1, p2)


def test_trim_segment_to_line_success():
    """Test trimming a segment to intersection with a cutting line."""
    repo = InMemoryGeomRepo()
    service = OpsService(repo)

    # Create a horizontal segment from (0,0) to (10,0)
    seg_ref = repo.add_segment(SegmentDTO(PointDTO(0.0, 0.0), PointDTO(10.0, 0.0)))

    # Cut it with a vertical line at x=5
    cut_a = PointDTO(5.0, -1.0)
    cut_b = PointDTO(5.0, 1.0)

    # Trim the 'b' end to the intersection
    result = service.trim_segment_to_line(seg_ref, cut_a, cut_b, end="b")
    assert result is True

    # Verify segment was trimmed to (0,0) -> (5,0)
    trimmed = repo.get_segment(seg_ref.id)
    assert trimmed is not None
    assert trimmed.a == PointDTO(0.0, 0.0)
    assert abs(trimmed.b.x - 5.0) < 1e-9
    assert abs(trimmed.b.y - 0.0) < 1e-9


def test_trim_segment_to_line_trim_a_end():
    """Test trimming the 'a' end of a segment."""
    repo = InMemoryGeomRepo()
    service = OpsService(repo)

    # Create a horizontal segment from (0,0) to (10,0)
    seg_ref = repo.add_segment(SegmentDTO(PointDTO(0.0, 0.0), PointDTO(10.0, 0.0)))

    # Cut it with a vertical line at x=3
    cut_a = PointDTO(3.0, -1.0)
    cut_b = PointDTO(3.0, 1.0)

    # Trim the 'a' end to the intersection
    result = service.trim_segment_to_line(seg_ref, cut_a, cut_b, end="a")
    assert result is True

    # Verify segment was trimmed to (3,0) -> (10,0)
    trimmed = repo.get_segment(seg_ref.id)
    assert trimmed is not None
    assert abs(trimmed.a.x - 3.0) < 1e-9
    assert abs(trimmed.a.y - 0.0) < 1e-9
    assert trimmed.b == PointDTO(10.0, 0.0)


def test_trim_segment_parallel_lines_returns_false():
    """Test that trimming with parallel lines returns False."""
    repo = InMemoryGeomRepo()
    service = OpsService(repo)

    # Create a horizontal segment
    seg_ref = repo.add_segment(SegmentDTO(PointDTO(0.0, 0.0), PointDTO(10.0, 0.0)))

    # Try to cut with another horizontal line (parallel)
    cut_a = PointDTO(0.0, 5.0)
    cut_b = PointDTO(10.0, 5.0)

    result = service.trim_segment_to_line(seg_ref, cut_a, cut_b)
    assert result is False

    # Verify segment was not modified
    seg = repo.get_segment(seg_ref.id)
    assert seg == SegmentDTO(PointDTO(0.0, 0.0), PointDTO(10.0, 0.0))


def test_trim_nonexistent_segment_returns_false():
    """Test that trimming a non-existent segment returns False."""
    repo = InMemoryGeomRepo()
    service = OpsService(repo)

    from backend.geom_repo import EntityRef

    fake_ref = EntityRef("segment", "segment:999")
    result = service.trim_segment_to_line(
        fake_ref, PointDTO(5.0, -1.0), PointDTO(5.0, 1.0)
    )
    assert result is False
