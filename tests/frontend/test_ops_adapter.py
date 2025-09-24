import pytest

from frontend.integration import build_adapter, register_ops_tools


def test_build_adapter_and_extend_segment():
    from backend.models import PointDTO, SegmentDTO

    adapter = build_adapter()
    if not hasattr(adapter.svc, "extend_segment_to_circle"):
        pytest.skip("backend OpsService does not expose extend_segment_to_circle on this branch")
    seg_ref = adapter.repo.add_segment(SegmentDTO(PointDTO(0, 0), PointDTO(1, 0)))
    ok = adapter.extend_segment_to_circle(seg_ref.id, 0.0, 0.0, 5.0, end="b")
    assert ok is True
    seg = adapter.repo.get_segment(seg_ref.id)
    assert seg is not None
    assert abs(seg.b.x - 5.0) < 1e-9 and abs(seg.b.y - 0.0) < 1e-9


def test_register_ops_tools_registers_factory():
    register_ops_tools()
    from frontend.tool_registry import get

    spec = get("ops.extend_to_circle")
    assert spec is not None and callable(spec.factory)
