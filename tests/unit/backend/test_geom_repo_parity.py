from backend.models import PointDTO, SegmentDTO, CircleDTO


def test_geom_repo_point_segment_circle_parity():
    import backend.geom_repo as legacy
    from lv_cad.backend.geom_repo import InMemoryGeomRepo as NewRepo

    repo_legacy = legacy.InMemoryGeomRepo()
    repo_new = NewRepo()

    # points
    p = PointDTO(1.0, 2.0)
    ref_l = repo_legacy.add_point(p)
    ref_n = repo_new.add_point(p)
    assert ref_l.kind == ref_n.kind
    assert repo_legacy.get_point(ref_l.id) == repo_new.get_point(ref_n.id)

    # segments
    s = SegmentDTO(PointDTO(0.0, 0.0), PointDTO(1.0, 1.0))
    rs_l = repo_legacy.add_segment(s)
    rs_n = repo_new.add_segment(s)
    assert rs_l.kind == rs_n.kind
    assert repo_legacy.get_segment(rs_l.id) == repo_new.get_segment(rs_n.id)

    # circles
    c = CircleDTO(PointDTO(0.0, 0.0), 1.0)
    rc_l = repo_legacy.add_circle(c)
    rc_n = repo_new.add_circle(c)
    assert rc_l.kind == rc_n.kind
    assert repo_legacy.get_circle(rc_l.id) == repo_new.get_circle(rc_n.id)
