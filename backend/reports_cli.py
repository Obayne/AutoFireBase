"""Headless CLI for generating reports and submittals.

Usage:
  python -m backend.reports_cli --out ./artifacts/reports --demo
  python -m backend.reports_cli --zip ./artifacts/reports/submittal_bundle.zip --demo

Notes:
- --demo generates a small set of faux items and wires for testing.
- If --zip is provided, a ZIP is created. Otherwise, HTML submittal + CSVs are written to --out.
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Any

from backend.reports import export_html_submittal, export_report_bundle_zip


@dataclass
class _FauxItem:
    name: str | None = None
    manufacturer: str | None = None
    part_number: str | None = None


@dataclass
class _FauxWire:
    length: float
    circuit_type: str | None = None
    circuit_id: str | None = None
    wire_gauge: str | None = None


def _demo_inputs() -> tuple[list[Any], list[Any]]:
    devices = [
        _FauxItem("Smoke Detector", "Acme", "SD-100"),
        _FauxItem("Horn/Strobe", "Acme", "HS-200"),
    ]
    wires = [_FauxWire(100.0, "SLC", "SLC1", "18")]
    return devices, wires


def run_cli(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate reports and submittals headlessly")
    ap.add_argument("--out", help="Output folder for HTML/CSVs")
    ap.add_argument("--zip", help="Output ZIP path for full bundle")
    ap.add_argument("--demo", action="store_true", help="Use demo devices/wires")
    args = ap.parse_args(argv)

    if not args.out and not args.zip:
        ap.error("one of --out or --zip is required")

    if args.demo:
        device_items, wire_items = _demo_inputs()
    else:
        # In the future, load a project file; for now require demo mode
        device_items, wire_items = _demo_inputs()

    if args.zip:
        out_zip = os.path.abspath(args.zip)
        os.makedirs(os.path.dirname(out_zip), exist_ok=True)
        export_report_bundle_zip(device_items, wire_items, out_zip)
        print(out_zip)
        return 0

    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)
    export_html_submittal(device_items, wire_items, out_dir)
    print(out_dir)
    return 0


def main():
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
