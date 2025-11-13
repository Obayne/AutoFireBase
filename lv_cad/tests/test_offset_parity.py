import importlib
import pytest

from lv_cad.geometry.point import Point
from lv_cad.operations import offset_polyline as new_offset


def _legacy_available() -> bool:
    try:
        # Any of these being importable is sufficient for parity attempt
        m = importlib.import_module("cad_core.offset")
        return hasattr(m, "offset_polyline") or hasattr(m, "offset")
    except ModuleNotFoundError:
        return False


@pytest.mark.skipif(not _legacy_available(), reason="legacy offset not available")
def test_offset_parity_square():
    pts = [
        Point(0.0, 0.0),
        Point(10.0, 0.0),
        Point(10.0, 10.0),
        Point(0.0, 10.0),
        Point(0.0, 0.0),
    ]

    # Call legacy
    legacy_mod = importlib.import_module("cad_core.offset")
    legacy_fn = getattr(legacy_mod, "offset_polyline", getattr(legacy_mod, "offset"))
    legacy_res = legacy_fn([(p.x, p.y) for p in pts], 1.0)

    # Call new
    new_res = new_offset(pts, 1.0)

    # Compare length and basic shape properties
    assert isinstance(new_res, list)
    assert len(new_res) == len(legacy_res)
