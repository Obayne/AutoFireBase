import csv
from pathlib import Path

from backend.reports import generate_compliance_summary_csv, generate_riser_csv


class FauxDevice:
    def __init__(self, name="Device"):
        self.name = name


class FauxPanel:
    def __init__(self, name):
        self.panel_type = "main"
        self.name = name
        self.circuits = {
            "SLC1": {
                "type": "SLC",
                "devices": [FauxDevice(), FauxDevice()],
                "status": "connected",
            },
            "NAC1": {"type": "NAC", "devices": [FauxDevice()], "status": "partial"},
            "SLC2": {
                "type": "SLC",
                "devices": [FauxDevice() for _ in range(22)],
                "status": "connected",
            },
        }


def test_generate_riser_and_compliance(tmp_path: Path):
    items = [FauxPanel("FACP-1")]

    riser_path = tmp_path / "riser.csv"
    comp_path = tmp_path / "compliance.csv"

    rsum = generate_riser_csv(items, str(riser_path))
    csum = generate_compliance_summary_csv(items, str(comp_path))

    assert rsum["rows"] == 3
    assert csum["rows"] == 3

    # Riser rows
    rrows = list(csv.DictReader(riser_path.open("r", encoding="utf-8")))
    assert {r["circuit_id"] for r in rrows} == {"SLC1", "NAC1", "SLC2"}

    # Compliance rows and outcomes
    crows = list(csv.DictReader(comp_path.open("r", encoding="utf-8")))
    by_id = {r["circuit_id"]: r for r in crows}
    assert by_id["SLC1"]["outcome"] == "PASS"
    assert by_id["NAC1"]["outcome"] == "WARN"  # partial
    assert by_id["SLC2"]["outcome"] == "FAIL"  # capacity > 20
