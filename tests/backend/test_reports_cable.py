import csv
from pathlib import Path

from backend.reports import generate_cable_schedule_csv


class FauxWire:
    def __init__(self, length, circuit_type=None, circuit_id=None, gauge=None):
        self.length = length
        self.circuit_type = circuit_type
        self.circuit_id = circuit_id
        self.wire_gauge = gauge


def test_generate_cable_schedule_basic(tmp_path: Path):
    wires = [
        FauxWire(100.0, "SLC", "SLC1", "18"),
        FauxWire(50.0, "SLC", "SLC1", "18"),
        FauxWire(75.5, "NAC", "NAC1", "14"),
        FauxWire(24.5, "NAC", "NAC1", "14"),
        FauxWire(10.0, None, None, None),
    ]

    out = tmp_path / "cable.csv"
    summary = generate_cable_schedule_csv(wires, str(out))

    assert summary["groups"] >= 3
    assert abs(summary["total_length_ft"] - (100 + 50 + 75.5 + 24.5 + 10.0)) < 1e-6

    rows = list(csv.DictReader(out.open("r", encoding="utf-8")))
    assert rows and set(rows[0].keys()) == {
        "circuit_type",
        "circuit_id",
        "gauge",
        "segment_count",
        "total_length_ft",
    }

    # Find SLC1 18AWG row and check totals
    slc_rows = [r for r in rows if r["circuit_type"] == "SLC" and r["circuit_id"] == "SLC1"]
    assert slc_rows
    slc_row = slc_rows[0]
    assert int(slc_row["segment_count"]) == 2
    assert abs(float(slc_row["total_length_ft"]) - 150.0) < 1e-6
