from pathlib import Path
from zipfile import ZipFile

from backend.reports import export_report_bundle_zip


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


a_files = {
    "index.html",
    "device_documents.html",
    "bom.csv",
    "cable_schedule.csv",
    "riser.csv",
    "compliance_summary.csv",
}


def test_export_report_bundle_zip(tmp_path: Path):
    devices = [
        FauxItem("Smoke Detector", "Acme", "SD-100"),
        FauxItem("Horn/Strobe", "Acme", "HS-200"),
    ]
    wires = [FauxWire(100.0, "SLC", "SLC1", "18")]

    zip_path = tmp_path / "submittal_bundle.zip"
    summary = export_report_bundle_zip(devices, wires, str(zip_path))

    # Check zip exists and includes expected files
    assert zip_path.exists()
    with ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())
    # allow for any subset superset check, but ensure at least these are present
    assert a_files.issubset(names)

    # Summary should include zip_path and basic counts
    assert summary.get("zip_path") == str(zip_path)
    assert "bom_path" in summary and "riser_path" in summary
