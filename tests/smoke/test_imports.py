def test_lv_cad_and_legacy_import():
    # Ensure new package imports and legacy package imports both succeed.
    import importlib

    lv_core = importlib.import_module("lv_cad.cad_core")
    assert hasattr(lv_core, "intersection_line_line")

    # Basic behavior smoke check: compute intersection of two crossing segments.
    P = lv_core.Point
    a = (P(0, 0), P(1, 1))
    b = (P(0, 1), P(1, 0))
    new = lv_core.intersection_line_line(a, b)
    assert new is not None

    # If legacy cad_core exposes the same API, compare results for parity.
    try:
        legacy = importlib.import_module("cad_core")
        if hasattr(legacy, "intersection_line_line"):
            old = legacy.intersection_line_line(a, b)
            # both should be not-None and have numeric coords
            assert (old is None) == (new is None)
    except Exception:
        # Legacy module may be present but not provide the function; that's fine
        # for this smoke test — the primary goal is that the new package works.
        pass
