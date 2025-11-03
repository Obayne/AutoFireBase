from __future__ import annotations

from typing import Any, Iterable

from .connections import Connection, ConnectionMethod


def export_riser_data(
    *,
    panels: Iterable[dict[str, Any]] | None = None,
    circuits: Iterable[dict[str, Any]] | None = None,
    connections: Iterable[Connection] | None = None,
) -> dict[str, Any]:
    """Return a structured riser export (JSON-like dict) summarizing connections.

    Inputs are intentionally generic to decouple from UI/state until v1 wiring.
    """
    panels_list = list(panels or [])
    circuits_list = list(circuits or [])
    conns = list(connections or [])

    # Build quick lookup for validation or enrichment later
    panel_ids = {p.get("id") for p in panels_list}
    circuit_keys = {(c.get("panel_id"), c.get("id")) for c in circuits_list}

    rows: list[dict[str, Any]] = []
    for c in conns:
        src_pair = (c.source_panel, c.source_circuit)
        rows.append(
            {
                "method": c.method.value,
                "label": c.label(),
                "source_panel": c.source_panel,
                "source_circuit": c.source_circuit,
                "target_kind": c.target_kind,
                "target_id": c.target_id,
                "vendor_bus": c.vendor_bus_name,
                "valid_panel": c.source_panel in panel_ids,
                "valid_circuit": src_pair in circuit_keys,
            }
        )

    export: dict[str, Any] = {
        "panels": panels_list,
        "circuits": circuits_list,
        "connections": rows,
        "stats": {
            "counts": {
                "panels": len(panels_list),
                "circuits": len(circuits_list),
                "connections": len(rows),
            }
        },
    }
    return export


__all__ = ["Connection", "ConnectionMethod", "export_riser_data"]
