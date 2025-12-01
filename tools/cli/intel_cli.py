"""
Layer Intelligence CLI - Batch Processing & Automation Tool
============================================================

**PURPOSE**: Headless command-line interface for batch CAD analysis and automation.
**INTEGRATION**: Wraps autofire_layer_intelligence.py for non-GUI workflows.

**Use Cases**:
- Batch analysis of multiple CAD files
- CI/CD pipeline integration for automated testing
- Scheduled analysis jobs and reporting
- Automation scripts for construction set processing

**Output**: JSON format suitable for automation, logging, and integration with other tools.

Wraps autofire_layer_intelligence.CADLayerIntelligence to analyze CAD files,
construction sets, and run coverage optimization.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from autofire_layer_intelligence import CADLayerIntelligence  # type: ignore  # noqa: E402
from backend.monitoring import init_monitoring  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="LV CAD Layer Intelligence (headless)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("analyze", help="Analyze a single CAD file (DWG/DXF/PDF stub)")
    sp.add_argument("file")

    sp = sub.add_parser("analyze-set", help="Analyze a set of CAD files")
    sp.add_argument("files", nargs="+")

    sp = sub.add_parser("optimize", help="Run coverage optimization demo")
    sp.add_argument("--devices", help="Optional initial placements JSON", default=None)

    return p


def main(argv: list[str] | None = None) -> int:
    init_monitoring()
    args = build_parser().parse_args(argv)
    intel = CADLayerIntelligence()

    if args.cmd == "analyze":
        data = intel.analyze_cad_file(args.file)
        print(json.dumps(data, indent=2))
        return 0

    if args.cmd == "analyze-set":
        data = intel.analyze_construction_set(args.files)  # type: ignore[attr-defined]
        print(json.dumps(data, indent=2))
        return 0

    if args.cmd == "optimize":
        placements: list[dict[str, Any]] | None = None
        if args.devices:
            try:
                placements = json.loads(args.devices)
            except Exception as e:
                print(json.dumps({"error": f"invalid devices JSON: {e}"}))
                return 2
        # Provide a minimal building geometry stub via engine if needed
        # The enhanced engine supports a demo optimize flow
        result = intel.optimize_coverage(placements or [])  # type: ignore[attr-defined]
        print(json.dumps(result, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
