import csv
import os
import tempfile

from backend.reports import generate_bom_csv


class _FakeItem:
    def __init__(self, name, manufacturer, part_number):
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number


def test_generate_bom_csv_basic():
    items = [
        _FakeItem("Smoke Detector", "Acme", "SD-100"),
        _FakeItem("Smoke Detector", "Acme", "SD-100"),
        _FakeItem("Pull Station", "Acme", "PS-50"),
    ]
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    try:
        summary = generate_bom_csv(items, path)
        assert summary["unique_items"] == 2
        assert summary["total_qty"] == 3

        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        # Header + 2 rows
        assert rows[0] == ["manufacturer", "part_number", "name", "quantity"]
        # Convert to set of tuples ignoring order
        data = {tuple(r) for r in rows[1:]}
        assert ("Acme", "SD-100", "Smoke Detector", "2") in data
        assert ("Acme", "PS-50", "Pull Station", "1") in data
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
