from backend import device_docs as legacy
from lv_cad.backend import device_docs as migrated


def test_lookup_docs_for_spec_parity():
    # Known token that maps to fallback URL
    args = dict(name="smoke")
    a = legacy.lookup_docs_for_spec(**args)
    b = migrated.lookup_docs_for_spec(**args)
    assert a == b


def test_lookup_docs_for_item_parity_with_dict():
    item = {"name": "Heat Sensor", "part_number": "HS-1", "manufacturer": "Acme"}
    a = legacy.lookup_docs_for_item(item)
    b = migrated.lookup_docs_for_item(item)
    assert a == b
