"""Lightweight report generators.

Currently provides:
- generate_bom_csv: aggregate placed devices into a CSV Bill of Materials.
- generate_cable_schedule_csv: summarize wire segments to a cable schedule CSV.
- generate_riser_csv: summarize panel circuits/devices to a riser CSV.
- generate_compliance_summary_csv: summarize basic compliance status per circuit.
- export_report_bundle: convenience to write multiple reports to a folder.
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict
from collections.abc import Iterable
from typing import Any
from urllib.parse import quote as urlquote
from zipfile import ZIP_DEFLATED, ZipFile

from backend import branding
from backend.device_docs import export_device_docs_html


def _item_signature(it: Any) -> tuple[str, str, str]:
    """Return a (manufacturer, part_number, name) signature for a scene item.

    Falls back to sensible defaults if metadata is missing.
    """
    manufacturer = getattr(it, "manufacturer", None) or ""
    part_number = getattr(it, "part_number", None) or ""
    # Prefer explicit name; fallback to device_type; then class name
    name = getattr(it, "name", None) or getattr(it, "device_type", None) or type(it).__name__
    # Normalize whitespace
    manufacturer = str(manufacturer).strip()
    part_number = str(part_number).strip()
    name = str(name).strip()
    return manufacturer, part_number, name


def generate_bom_csv(items: Iterable[Any], dest_path: str) -> dict[str, int]:
    """Generate a BOM CSV from an iterable of scene items.

    - Groups by (manufacturer, part_number, name)
    - Writes CSV with header: manufacturer,part_number,name,quantity
    - Returns summary dict: {"unique_items": N, "total_qty": Q}
    """
    if not items:
        items = []

    # Aggregate quantities
    counts: dict[tuple[str, str, str], int] = defaultdict(int)
    total_qty = 0
    for it in items:
        # Only include device-like items (have a name or part number)
        mfg, pn, name = _item_signature(it)
        if not (mfg or pn or name):
            continue
        counts[(mfg, pn, name)] += 1
        total_qty += 1

    # Ensure destination directory
    out_dir = os.path.dirname(os.path.abspath(dest_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Write CSV
    with open(dest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["manufacturer", "part_number", "name", "quantity"])
        for (mfg, pn, name), qty in sorted(
            counts.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])
        ):
            writer.writerow([mfg, pn, name, qty])

    return {"unique_items": len(counts), "total_qty": total_qty}


def _wire_signature(it: Any) -> tuple[str, str, str]:
    """Return a (circuit_type, circuit_id, gauge) signature for a wire/segment-like item.

    Attributes are optional; falls back to sensible defaults.
    """
    circuit_type = getattr(it, "circuit_type", None) or getattr(it, "type", None) or ""
    circuit_id = getattr(it, "circuit_id", None) or ""
    gauge = (
        getattr(it, "wire_gauge", None)
        or getattr(it, "awg", None)
        or getattr(it, "gauge", None)
        or ""
    )
    return str(circuit_type).strip(), str(circuit_id).strip(), str(gauge).strip()


def _wire_length(it: Any) -> float:
    """Extract a numeric length from an item, defaulting to 0.0 if not available."""
    try:
        # Prefer explicit feet; else generic length assumed feet
        if hasattr(it, "length_ft"):
            return float(getattr(it, "length_ft"))
        if hasattr(it, "length"):
            return float(getattr(it, "length"))
        return 0.0
    except (TypeError, ValueError, AttributeError):
        return 0.0


def generate_cable_schedule_csv(items: Iterable[Any], dest_path: str) -> dict[str, int | float]:
    """Generate a cable schedule CSV from wire/segment-like items.

    - Groups by (circuit_type, circuit_id, gauge)
    - Sums total length and counts segments per group
    - Writes CSV with header: circuit_type,circuit_id,gauge,segment_count,total_length_ft
    - Returns summary dict with totals
    """
    if not items:
        items = []

    totals: dict[tuple[str, str, str], dict[str, float | int]] = defaultdict(
        lambda: {"segment_count": 0, "total_length_ft": 0.0}
    )
    total_segments = 0
    total_length_ft = 0.0
    for it in items:
        ct, cid, gauge = _wire_signature(it)
        length = _wire_length(it)
        key = (ct, cid, gauge)
        group = totals[key]
        group["segment_count"] = int(group["segment_count"]) + 1
        group["total_length_ft"] = float(group["total_length_ft"]) + float(length)
        total_segments += 1
        total_length_ft += float(length)

    out_dir = os.path.dirname(os.path.abspath(dest_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(dest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["circuit_type", "circuit_id", "gauge", "segment_count", "total_length_ft"]
        )
        for (ct, cid, gauge), agg in sorted(
            totals.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])
        ):
            writer.writerow(
                [ct, cid, gauge, int(agg["segment_count"]), f"{float(agg['total_length_ft']):.2f}"]
            )

    return {
        "groups": len(totals),
        "total_segments": total_segments,
        "total_length_ft": float(f"{total_length_ft:.2f}"),
    }


def export_report_bundle(
    device_items: Iterable[Any], wire_items: Iterable[Any], folder: str
) -> dict[str, str | int | float]:
    """Export a basic report bundle (BOM + Cable Schedule) into a folder.

    Returns a dict summary containing output paths and simple totals.
    """
    os.makedirs(folder, exist_ok=True)
    bom_path = os.path.join(folder, "bom.csv")
    cable_path = os.path.join(folder, "cable_schedule.csv")
    riser_path = os.path.join(folder, "riser.csv")
    compliance_path = os.path.join(folder, "compliance_summary.csv")

    bom = generate_bom_csv(device_items, bom_path)
    cable = generate_cable_schedule_csv(wire_items, cable_path)
    # Riser/compliance work off device/panel topology
    riser = generate_riser_csv(device_items, riser_path)
    compliance = generate_compliance_summary_csv(device_items, compliance_path)

    return {
        "bom_path": bom_path,
    "cable_path": cable_path,
    "riser_path": riser_path,
    "compliance_path": compliance_path,
        "bom_unique": bom.get("unique_items", 0),
        "bom_qty": bom.get("total_qty", 0),
        "cable_groups": cable.get("groups", 0),
        "cable_segments": cable.get("total_segments", 0),
        "cable_length_ft": cable.get("total_length_ft", 0.0),
        "riser_rows": riser.get("rows", 0),
        "compliance_rows": compliance.get("rows", 0),
    }


def _csv_to_html_table(path: str, title: str) -> str:
    """Convert a CSV file to an HTML table with a caption.

    Keeps it simple; assumes first row is header.
    """
    rows: list[list[str]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = [list(r) for r in reader]
    if not rows:
        return ""
    head, body = rows[0], rows[1:]
    thead = "".join(f"<th>{h}</th>" for h in head)
    tbody = "\n".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body)
    caption = f"<caption>{title}</caption>" if title else ""
    return f"<table>{caption}<thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>"


def export_html_submittal(
    device_items: Iterable[Any], wire_items: Iterable[Any], folder: str
) -> dict[str, str]:
    """Export a simple HTML submittal (index.html) that embeds all report tables.

    Also writes CSVs side-by-side and links to them for convenience.
    Returns dict with paths to index.html and the CSVs.
    """
    os.makedirs(folder, exist_ok=True)
    bundle = export_report_bundle(device_items, wire_items, folder)
    # Additionally, write device documents table HTML
    docs_html_path = os.path.join(folder, "device_documents.html")
    try:
        docs_written = export_device_docs_html(device_items, docs_html_path)
    except (OSError, RuntimeError):
        docs_written = ""

    bom = str(bundle["bom_path"])  # ensure str for type-checkers
    cable = str(bundle["cable_path"])  # ensure str for type-checkers
    riser = str(bundle["riser_path"])  # ensure str for type-checkers
    comp = str(bundle["compliance_path"])  # ensure str for type-checkers

    # Build HTML content with print-friendly CSS (page breaks, repeating headers)
    css = """
    <style>
    body { font-family: Segoe UI, Roboto, Arial, sans-serif; color: #222; }
    h1, h2 { margin: 0.4rem 0; }
    .meta { color: #555; margin-bottom: 1rem; }
    .section { margin: 1rem 0 1.2rem; }
    table { border-collapse: collapse; width: 100%; margin: 0.6rem 0; }
    caption { text-align: left; font-weight: bold; margin-bottom: .5rem; }
    th, td { border: 1px solid #ccc; padding: 6px 8px; font-size: 13px; }
    th { background: #f6f6f6; }
    .links a { margin-right: 1rem; }
    .print-note { display: none; color: #555; font-size: 12px; }
    @media print {
      @page { size: auto; margin: 12mm; }
      .links { display: none; }
      iframe { display: none; }
      .print-note { display: block; }
      .section { break-inside: avoid-page; page-break-inside: avoid; }
      h2:not(:first-of-type) { break-before: page; page-break-before: always; }
      thead { display: table-header-group; }
      tfoot { display: table-footer-group; }
    }
    </style>
    """

    # Convert CSVs to HTML tables
    bom_html = _csv_to_html_table(bom, "Bill of Materials")
    cable_html = _csv_to_html_table(cable, "Cable Schedule")
    riser_html = _csv_to_html_table(riser, "Riser")
    comp_html = _csv_to_html_table(comp, "Compliance Summary")

    def rel(p: str) -> str:
        return os.path.basename(p)

    product = branding.PRODUCT_NAME
    version_label = branding.full_product_label()
    html = f"""
    <!doctype html>
    <html>
    <head>
    <meta charset="utf-8" />
    <title>{product} Submittal</title>
    {css}
    </head>
    <body>
      <h1>{product} Submittal</h1>
      <div class="meta">Generated by {version_label}</div>
            <div class="links">
        Download CSVs:
        <a href="{urlquote(rel(bom))}" download>BOM</a>
        <a href="{urlquote(rel(cable))}" download>Cable Schedule</a>
        <a href="{urlquote(rel(riser))}" download>Riser</a>
        <a href="{urlquote(rel(comp))}" download>Compliance</a>
                <a href="{urlquote(rel(docs_written))}">Device Documents</a>
      </div>

            <div class="section">
                <h2>Bill of Materials</h2>
                {bom_html}
            </div>

            <div class="section">
                <h2>Cable Schedule</h2>
                {cable_html}
            </div>

            <div class="section">
                <h2>Riser</h2>
                {riser_html}
            </div>

            <div class="section">
                <h2>Compliance Summary</h2>
                {comp_html}
            </div>

            <div class="section">
                <h2>Device Documents</h2>
                <iframe
                    src="{urlquote(rel(docs_written))}"
                    style="width:100%; height:480px; border:1px solid #ddd;"
                ></iframe>
                <div class="print-note">
                    Device Documents appendix not shown in print. See separate file:
                    <strong>{urlquote(rel(docs_written))}</strong>
                </div>
            </div>
    </body>
    </html>
    """

    index_path = os.path.join(folder, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "index_path": index_path,
        "bom_path": bom,
        "cable_path": cable,
        "riser_path": riser,
        "compliance_path": comp,
        "device_docs_path": docs_written,
    }


def export_report_bundle_zip(
    device_items: Iterable[Any], wire_items: Iterable[Any], zip_path: str
) -> dict[str, str | int | float]:
    """Export the full report bundle into a ZIP archive.

    Produces a ZIP containing: index.html, device_documents.html, and all CSVs.
    Returns the export_report_bundle() summary plus the zip_path.
    """
    out_dir = os.path.dirname(os.path.abspath(zip_path))
    os.makedirs(out_dir, exist_ok=True)

    # Stage outputs into the target folder of the zip file
    # We reuse the directory where the zip lives to avoid temp dirs.
    staging_dir = os.path.join(out_dir, "_report_bundle_tmp")
    os.makedirs(staging_dir, exist_ok=True)

    # Generate submittal + CSVs
    submittal = export_html_submittal(device_items, wire_items, staging_dir)

    # Files to include
    files = [
        submittal.get("index_path", ""),
        submittal.get("device_docs_path", ""),
        submittal.get("bom_path", ""),
        submittal.get("cable_path", ""),
        submittal.get("riser_path", ""),
        submittal.get("compliance_path", ""),
    ]
    files = [f for f in files if f and os.path.exists(str(f))]

    # Write ZIP
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for fpath in files:
            arcname = os.path.basename(str(fpath))
            zf.write(str(fpath), arcname=arcname)

    # Clean up staging
    try:
        for f in files:
            try:
                os.remove(str(f))
            except OSError:
                pass
        os.rmdir(staging_dir)
    except OSError:
        # Non-fatal; leave artifacts if removal fails
        pass

    summary = export_report_bundle(device_items, wire_items, out_dir)
    summary["zip_path"] = zip_path
    return summary


def _iter_panels(items: Iterable[Any]) -> list[Any]:
    """Return panel-like items: have panel_type == 'main' and a circuits dict."""
    panels: list[Any] = []
    for it in items or []:
        if getattr(it, "panel_type", None) == "main" and hasattr(it, "circuits"):
            panels.append(it)
    return panels


def generate_riser_csv(items: Iterable[Any], dest_path: str) -> dict[str, int]:
    """Generate a simple riser CSV from panel circuits.

    Columns: panel_name, circuit_id, circuit_type, device_count
    """
    panels = _iter_panels(items)
    rows: list[tuple[str, str, str, int]] = []
    for p in panels:
        panel_name = getattr(p, "name", "Panel")
        circuits = getattr(p, "circuits", {}) or {}
        for cid, cdata in circuits.items():
            ctype = str(cdata.get("type", "")).strip()
            devs = cdata.get("devices", []) or []
            rows.append((panel_name, str(cid), ctype, len(devs)))

    out_dir = os.path.dirname(os.path.abspath(dest_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(dest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["panel_name", "circuit_id", "circuit_type", "device_count"])
        for panel_name, cid, ctype, cnt in rows:
            writer.writerow([panel_name, cid, ctype, cnt])
    return {"rows": len(rows)}


def generate_compliance_summary_csv(items: Iterable[Any], dest_path: str) -> dict[str, int]:
    """Generate a basic compliance summary per circuit.

    Heuristics:
    - capacity: warn if > 20 devices on a circuit (toy rule consistent with panel code)
    - status: propagate circuit status if available (connected/partial/ready)
    - outcome: FAIL if capacity exceeded; WARN if partial; PASS otherwise

    Columns: panel_name, circuit_id, circuit_type, device_count, status, outcome
    """
    panels = _iter_panels(items)
    rows: list[tuple[str, str, str, int, str, str]] = []
    for p in panels:
        panel_name = getattr(p, "name", "Panel")
        circuits = getattr(p, "circuits", {}) or {}
        for cid, cdata in circuits.items():
            ctype = str(cdata.get("type", "")).strip()
            devs = cdata.get("devices", []) or []
            status = str(cdata.get("status", "")).strip() or "ready"
            count = len(devs)
            if count > 20:
                outcome = "FAIL"
            elif status == "partial":
                outcome = "WARN"
            else:
                outcome = "PASS"
            rows.append((panel_name, str(cid), ctype, count, status, outcome))

    out_dir = os.path.dirname(os.path.abspath(dest_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(dest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "panel_name",
                "circuit_id",
                "circuit_type",
                "device_count",
                "status",
                "outcome",
            ]
        )
        for row in rows:
            writer.writerow(list(row))
    return {"rows": len(rows)}
