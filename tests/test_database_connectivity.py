"""Focused test: database connectivity and basic fetches.

This test connects using `db.loader.connect()` and attempts to call
`fetch_panels`, `fetch_devices`, and `fetch_wires` if available. It will be
skipped when `db.loader` cannot be imported in the current environment.
"""

import pytest


def test_database_connectivity_or_skip():
    try:
        from db import loader as db_loader
    except Exception:
        pytest.skip("db.loader not available in this environment")

    con = db_loader.connect()
    try:
        if hasattr(db_loader, "fetch_panels"):
            panels = db_loader.fetch_panels(con)
            assert panels is not None
        if hasattr(db_loader, "fetch_devices"):
            devices = db_loader.fetch_devices(con)
            assert devices is not None
        if hasattr(db_loader, "fetch_wires"):
            wires = db_loader.fetch_wires(con)
            assert wires is not None
    finally:
        try:
            con.close()
        except Exception:
            pass
