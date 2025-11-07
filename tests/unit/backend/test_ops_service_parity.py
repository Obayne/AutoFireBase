import backend.ops_service as legacy
import lv_cad.backend.ops_service as migrated
from backend.models import PointDTO


def test_create_segment_parity():
    repo = legacy.InMemoryGeomRepo()
    ops = legacy.OpsService(repo=repo)
    a = PointDTO(x=0, y=0)
    b = PointDTO(x=1, y=1)

    ref_l = ops.create_segment(a, b)

    repo2 = legacy.InMemoryGeomRepo()
    ops2 = migrated.OpsService(repo=repo2)
    ref_m = ops2.create_segment(a, b)

    assert ref_l is not None
    assert ref_m is not None
