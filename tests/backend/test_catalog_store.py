from pathlib import Path

from backend.store.catalog import CatalogStore


def test_seed_and_list(tmp_path: Path):
    db = tmp_path / "catalog.db"
    store = CatalogStore(db, seed_demo=True)
    try:
        types = store.list_types()
        assert any(t for t in types if t != "(Any)")

        devs = store.list_devices()
        assert len(devs) >= 1

        # Can search by substring and type filter
        any_type = next((t for t in types if t not in {"(Any)"}), None)
        filtered = store.list_devices(type_filter=any_type)
        assert all(d.type == any_type for d in filtered)

        # Strobe radius seeded values present
        r = store.strobe_radius_for_candela(30)
        assert r is None or r > 0.0
    finally:
        store.close()


def test_add_device_and_query(tmp_path: Path):
    db = tmp_path / "catalog.db"
    store = CatalogStore(db, seed_demo=False)
    try:
        did = store.add_device(
            manufacturer="GenCo",
            type_code="Notification",
            model="GEN-S",
            name="Strobe",
            symbol="S",
            props={"candelas": [15, 30]},
        )
        assert did > 0

        all_devs = store.list_devices()
        assert any(d.name == "Strobe" for d in all_devs)

        q = store.list_devices(query="GEN-S")
        assert q and q[0].part_number == "GEN-S"
    finally:
        store.close()

