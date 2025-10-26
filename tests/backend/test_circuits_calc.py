from backend.circuits import voltage_drop_percent, battery_capacity_ah, summarize_panel_circuits


class FauxPanel:
    def __init__(self, name="P1"):
        self.panel_type = "main"
        self.name = name
        self.circuits = {
            "NAC1": {"type": "NAC", "devices": list(range(10))},
            "SLC1": {"type": "SLC", "devices": list(range(20))},
        }


class FauxWire:
    def __init__(self, length_ft, cid, gauge="18"):
        self.length_ft = length_ft
        self.circuit_id = cid
        self.wire_gauge = gauge


def test_voltage_drop_basic():
    # 100 ft loop, 0.6A, 18 AWG ~ 3% drop at 24V
    drop = voltage_drop_percent(100.0, 0.6, "18", 24.0)
    assert 2.5 <= drop <= 3.5


def test_battery_capacity_calc():
    # 24h @0.1A + 5min @0.6A, derate 1.25
    ah = battery_capacity_ah(24.0, 5.0, 0.1, 0.6, 1.25)
    assert 3.0 <= ah <= 3.2  # ~3.06Ah


def test_summarize_panel_circuits():
    panel = FauxPanel()
    wires = [
        FauxWire(100.0, "NAC1", "18"),
        FauxWire(120.0, "SLC1", "18"),
    ]
    out = summarize_panel_circuits([panel], wires)
    # Expect two rows
    assert len(out) == 2
    # Find NAC1 row
    nac = next(r for r in out if r.circuit_id == "NAC1")
    assert nac.device_count == 10
    assert nac.length_ft == 100.0
    assert nac.gauge == "18"
    assert nac.drop_percent > 0.0
    assert nac.status in ("PASS", "WARN", "FAIL")


def test_device_current_heuristics_affect_totals():
    class FauxDevice:
        def __init__(self, name):
            self.name = name
            self.part_number = ""

    class P:
        def __init__(self):
            self.panel_type = "main"
            self.name = "P1"
            self.circuits = {
                "NAC1": {"type": "NAC", "devices": [FauxDevice("Horn Strobe"), FauxDevice("Strobe")]},
                "SLC1": {"type": "SLC", "devices": [FauxDevice("Smoke Detector"), FauxDevice("Smoke Detector")]},
            }

    wires = [FauxWire(150.0, "NAC1", "18"), FauxWire(150.0, "SLC1", "18")]
    out = summarize_panel_circuits([P()], wires)
    nac = next(r for r in out if r.circuit_id == "NAC1")
    slc = next(r for r in out if r.circuit_id == "SLC1")
    # NAC should draw more current than SLC
    assert nac.current_a > slc.current_a
    # NAC VD should be higher than SLC VD given same length/gauge
    assert nac.drop_percent >= slc.drop_percent
