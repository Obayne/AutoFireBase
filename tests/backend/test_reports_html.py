from pathlib import Path

from backend.reports import export_html_submittal


class FauxItem:
    def __init__(self, name=None, manufacturer=None, part_number=None):
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number


class FauxWire:
    def __init__(self, length, circuit_type=None, circuit_id=None, gauge=None):
        self.length = length
        self.circuit_type = circuit_type
        self.circuit_id = circuit_id
        self.wire_gauge = gauge


def test_export_html_submittal(tmp_path: Path):
    devices = [
        FauxItem("Smoke Detector", "Acme", "SD-100"),
        FauxItem("Horn/Strobe", "Acme", "HS-200"),
    ]
    wires = [FauxWire(100.0, "SLC", "SLC1", "18")]

    out = export_html_submittal(devices, wires, str(tmp_path))
    index = Path(out["index_path"])  # type: ignore[index]
    assert index.exists()
    html = index.read_text(encoding="utf-8")
    assert "<table>" in html and "Bill of Materials" in html and "Cable Schedule" in html
