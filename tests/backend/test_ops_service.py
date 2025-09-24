from backend.geom_repo import InMemoryGeomRepo
from backend.models import PointDTO
from backend.ops_service import OpsService


def test_create_segment_adds_entity_to_repo():
    repo = InMemoryGeomRepo()
    svc = OpsService(repo=repo)

    ref = svc.create_segment(PointDTO(0.0, 0.0), PointDTO(1.0, 1.0))
    assert ref.kind == "segment"
    assert ref.id.startswith("segment:")

    seg = repo.get_segment(ref.id)
    assert seg is not None
    assert seg.a == PointDTO(0.0, 0.0)
    assert seg.b == PointDTO(1.0, 1.0)
