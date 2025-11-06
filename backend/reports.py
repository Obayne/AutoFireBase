"""Minimal reporting helpers used by ModelSpaceWindow.

These functions are lightweight shims so UI actions calling into
backend.reports do not fail. They produce small CSV/ZIP placeholders.
"""

from __future__ import annotations

import csv
import os
import zipfile
from collections import defaultdict
from collections.abc import Iterable
from typing import Any


def _normalize_item(i) -> dict[str, Any]:
    """Try to extract name/manufacturer/part_number/qty from various item types."""
    out = {"name": "", "manufacturer": "", "part_number": "", "qty": 1}
    try:
        # dict-like
        if isinstance(i, dict):
            out["name"] = i.get("name", "")
            out["manufacturer"] = i.get("manufacturer", "")
            out["part_number"] = i.get("part_number", "")
            out["qty"] = int(i.get("qty", 1) or 1)
            return out
        # QGraphicsItem-like objects may expose attributes
        name = getattr(i, "name", None)
        if name:
            out["name"] = str(name)
        else:
            # try item.data if available
            try:
                data = i.data(0)
                if isinstance(data, dict):
                    out["name"] = data.get("name", out["name"])
                    out["manufacturer"] = data.get("manufacturer", out["manufacturer"])
                    out["part_number"] = data.get("part_number", out["part_number"])
            except Exception:
                pass
        out["manufacturer"] = out.get("manufacturer") or getattr(i, "manufacturer", "")
        out["part_number"] = out.get("part_number") or getattr(i, "part_number", "")
    except Exception:
        pass
    return out


def generate_bom_csv(devices: Iterable[Any], out_path: str) -> dict[str, Any]:
    """Generate a BOM CSV. Returns a summary dict.

    devices may be dicts or QGraphicsItems—this function handles both.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    counts = defaultdict(int)
    _rows = []
    total_qty = 0
    for d in devices:
        ni = _normalize_item(d)
        key = (ni.get("name", ""), ni.get("manufacturer", ""), ni.get("part_number", ""))
        counts[key] += int(ni.get("qty", 1) or 1)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Name", "Manufacturer", "Part Number", "Quantity"])
        for (name, mfg, pn), qty in counts.items():
            w.writerow([name, mfg, pn, qty])
            total_qty += int(qty or 0)

    return {
        "bom_path": out_path,
        "unique_items": len(counts),
        "total_qty": total_qty,
    }


def generate_cable_schedule_csv(wire_items: Iterable[Any], out_path: str) -> dict[str, Any]:
    """Generate a very small cable schedule summary CSV and return stats."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    total_len = 0.0
    segments = 0
    for w in wire_items:
        try:
            ln = float(getattr(w, "length_ft", 0.0) or 0.0)
            total_len += ln
            segments += 1
        except Exception:
            continue

    # write CSV summary
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["SegmentIndex", "Length_ft"])
        idx = 0
        for w_item in wire_items:
            idx += 1
            try:
                ln = float(getattr(w_item, "length_ft", 0.0) or 0.0)
            except Exception:
                ln = 0.0
            w.writerow([idx, f"{ln:.2f}"])

    return {
        "cable_path": out_path,
        "groups": max(1, segments),
        "total_length_ft": total_len,
        "segments": segments,
    }


def export_report_bundle(
    device_items: Iterable[Any], wire_items: Iterable[Any], folder: str
) -> dict[str, Any]:
    os.makedirs(folder, exist_ok=True)
    bom_path = os.path.join(folder, "bom.csv")
    cable_path = os.path.join(folder, "cable_schedule.csv")
    riser_path = os.path.join(folder, "riser.csv")
    compliance_path = os.path.join(folder, "compliance.csv")

    bom = generate_bom_csv(device_items, bom_path)
    cable = generate_cable_schedule_csv(wire_items, cable_path)

    # minimal riser/compliance placeholders
    with open(riser_path, "w", newline="", encoding="utf-8") as f:
        f.write("Riser placeholder\n")
    with open(compliance_path, "w", newline="", encoding="utf-8") as f:
        f.write("Compliance placeholder\n")

    return {
        "bom_path": bom.get("bom_path"),
        "bom_unique": bom.get("unique_items", 0),
        "bom_qty": bom.get("total_qty", 0),
        "cable_path": cable.get("cable_path"),
        "cable_groups": cable.get("groups", 0),
        "cable_segments": cable.get("segments", 0),
        "cable_length_ft": cable.get("total_length_ft", 0.0),
        "riser_path": riser_path,
        "riser_rows": 0,
        "compliance_path": compliance_path,
        "compliance_rows": 0,
    }


def export_html_submittal(
    device_items: Iterable[Any], wire_items: Iterable[Any], folder: str
) -> dict[str, Any]:
    os.makedirs(folder, exist_ok=True)
    index_path = os.path.join(folder, "index.html")
    docs_path = os.path.join(folder, "device_documents.html")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Submittal Index (placeholder)</h1>\n")
        f.write("<ul>\n")
        f.write(f'<li><a href="{os.path.basename(docs_path)}">Device Docs</a></li>\n')
        f.write("</ul>\n</body></html>")

    with open(docs_path, "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Device Documents (placeholder)</h1></body></html>")

    return {"index_path": index_path, "docs_path": docs_path}


def export_report_bundle_zip(
    device_items: Iterable[Any], wire_items: Iterable[Any], zip_path: str
) -> dict[str, Any]:
    tmp_dir = os.path.splitext(zip_path)[0] + "_tmp"
    summary = export_report_bundle(device_items, wire_items, tmp_dir)
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w") as z:
        # add the files we know
        for p in [
            summary.get("bom_path"),
            summary.get("cable_path"),
            summary.get("riser_path"),
            summary.get("compliance_path"),
        ]:
            if p and os.path.exists(p):
                z.write(p, arcname=os.path.basename(p))
            else:
                z.writestr(
                    os.path.basename(p) if p else "placeholder.txt", "Missing file placeholder"
                )
        # add HTML submittal
        html = export_html_submittal(device_items, wire_items, tmp_dir)
        if html.get("index_path") and os.path.exists(html.get("index_path")):
            z.write(html.get("index_path"), arcname=os.path.basename(html.get("index_path")))

    return {"zip_path": zip_path}


def generate_riser_csv(*_args, out_path: str) -> dict[str, Any]:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Riser placeholder\n")
    return {"riser_path": out_path}


def generate_compliance_summary_csv(*_args, out_path: str) -> dict[str, Any]:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Compliance placeholder\n")
    return {"compliance_path": out_path}
