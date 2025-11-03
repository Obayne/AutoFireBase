from __future__ import annotations

from backend.connections import Connection, ConnectionMethod
from backend.riser_export import export_riser_data


def test_export_riser_basic_connection():
    panels = [
        {"id": "FACP-1", "name": "Main FACP"},
        {"id": "PSN-1", "name": "NAC Panel"},
    ]
    circuits = [
        {"id": "NAC1", "panel_id": "FACP-1", "type": "NAC"},
    ]
    connections = [
        Connection(
            method=ConnectionMethod.REVERSE_POLARITY,
            source_panel="FACP-1",
            source_circuit="NAC1",
            target_id="PSN-1",
            target_kind="panel",
        )
    ]

    out = export_riser_data(panels=panels, circuits=circuits, connections=connections)
    assert out["stats"]["counts"]["connections"] == 1
    row = out["connections"][0]
    assert row["method"] == ConnectionMethod.REVERSE_POLARITY.value
    assert row["valid_panel"] is True
    assert row["valid_circuit"] is True
    assert "FACP-1:NAC1" in row["label"]
