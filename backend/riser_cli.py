"""Headless CLI to export a simple riser JSON summary.

Usage (demo):
  python -m backend.riser_cli --out artifacts/riser_demo.json --demo
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

from .connections import Connection, ConnectionMethod
from .riser_export import export_riser_data


def _demo_project() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[Connection]]:
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
    return panels, circuits, connections


essential_desc = "Export a riser JSON representation from simple inputs"


def run_cli(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=essential_desc)
    ap.add_argument("--out", required=True, help="Output JSON file path")
    ap.add_argument("--demo", action="store_true", help="Use a minimal demo project")
    args = ap.parse_args(argv)

    if args.demo:
        panels, circuits, connections = _demo_project()
    else:
        # For v1, only demo is supported from CLI; integration will read live project state later.
        panels, circuits, connections = _demo_project()

    data = export_riser_data(panels=panels, circuits=circuits, connections=connections)

    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(out_path)
    return 0


def main() -> None:
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
