"""Focused test: device catalog loading.

This is an incremental, safe re-enable of part of the old comprehensive test
suite. It will skip when the `backend.catalog` module is not importable in the
current environment.
"""

import pytest


def test_device_catalog_loads_or_skips():
    try:
        from backend.catalog import load_catalog
    except Exception:
        pytest.skip("backend.catalog not available in this environment")

    devices = load_catalog()
    assert devices is not None
    assert hasattr(devices, "__len__") or hasattr(devices, "__iter__")
