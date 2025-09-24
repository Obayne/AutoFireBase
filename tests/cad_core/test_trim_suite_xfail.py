import pytest


@pytest.mark.xfail(reason="arc trim/extend not implemented yet")
def test_trim_arc_by_line_xfail():
    # Placeholder for future API: trim an Arc to a Line cutter
    # Expected: returns a new Arc with end snapped to intersection tangent point
    pytest.xfail("not implemented")


@pytest.mark.xfail(reason="segment-circle extend not implemented yet")
def test_extend_segment_to_circle_xfail():
    # Placeholder: extend a segment endpoint to intersect a circle
    # Expected: new segment endpoint lies on the circle at nearest intersection
    pytest.xfail("not implemented")


@pytest.mark.xfail(reason="line-arc trim not implemented yet")
def test_trim_line_by_arc_xfail():
    # Placeholder: trim a line by an arc cutter (finite arc)
    # Expected: moves chosen endpoint to intersection with the arc if exists
    pytest.xfail("not implemented")
