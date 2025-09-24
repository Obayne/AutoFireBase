from backend.geom_repo import InMemoryGeomRepo
from backend.models import CircleDTO, PointDTO, SegmentDTO
from backend.ops_service import OpsService


def test_ops_extend_segment_to_circle_updates_repo():
    repo = InMemoryGeomRepo()
    svc = OpsService(repo=repo)

    # Seed a segment along +X from origin
    seg_ref = repo.add_segment(SegmentDTO(PointDTO(0, 0), PointDTO(1, 0)))
    # Define a circle of radius 5 centered at origin
    circle = CircleDTO(center=PointDTO(0, 0), r=5.0)

    ok = svc.extend_segment_to_circle(seg_ref, circle, end="b")
    assert ok is True
    updated = repo.get_segment(seg_ref.id)
    assert updated is not None
    assert abs(updated.b.x - 5.0) < 1e-9 and abs(updated.b.y - 0.0) < 1e-9
