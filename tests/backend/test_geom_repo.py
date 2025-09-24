from backend.geom_repo import InMemoryGeomRepo
from backend.models import CircleDTO, PointDTO, SegmentDTO


def test_add_and_get_point_segment_circle():
    repo = InMemoryGeomRepo()

    p_ref = repo.add_point(PointDTO(1.0, 2.0))
    assert p_ref.kind == "point" and p_ref.id.startswith("point:")
    p = repo.get_point(p_ref.id)
    assert p == PointDTO(1.0, 2.0)

    s_ref = repo.add_segment(SegmentDTO(PointDTO(0, 0), PointDTO(1, 1)))
    assert s_ref.kind == "segment" and s_ref.id.startswith("segment:")
    s = repo.get_segment(s_ref.id)
    assert s == SegmentDTO(PointDTO(0, 0), PointDTO(1, 1))

    c_ref = repo.add_circle(CircleDTO(PointDTO(0, 0), 5.0))
    assert c_ref.kind == "circle" and c_ref.id.startswith("circle:")
    c = repo.get_circle(c_ref.id)
    assert c == CircleDTO(PointDTO(0, 0), 5.0)


def test_update_entities_returns_true_on_success():
    repo = InMemoryGeomRepo()
    p_ref = repo.add_point(PointDTO(0.0, 0.0))
    assert repo.update_point(p_ref.id, PointDTO(9.0, 9.0)) is True
    assert repo.get_point(p_ref.id) == PointDTO(9.0, 9.0)

    s_ref = repo.add_segment(SegmentDTO(PointDTO(0, 0), PointDTO(1, 1)))
    assert repo.update_segment(s_ref.id, SegmentDTO(PointDTO(2, 2), PointDTO(3, 3))) is True
    assert repo.get_segment(s_ref.id) == SegmentDTO(PointDTO(2, 2), PointDTO(3, 3))

    c_ref = repo.add_circle(CircleDTO(PointDTO(0, 0), 1.0))
    assert repo.update_circle(c_ref.id, CircleDTO(PointDTO(1, 1), 2.0)) is True
    assert repo.get_circle(c_ref.id) == CircleDTO(PointDTO(1, 1), 2.0)


def test_update_unknown_ids_returns_false():
    repo = InMemoryGeomRepo()
    assert repo.update_point("point:999", PointDTO(0, 0)) is False
    assert repo.update_segment("segment:999", SegmentDTO(PointDTO(0, 0), PointDTO(1, 1))) is False
    assert repo.update_circle("circle:999", CircleDTO(PointDTO(0, 0), 1.0)) is False
