#!/usr/bin/env python3
"""Audit device catalog for cutsheet availability and optionally download missing docs.

Usage:
  python scripts/cutsheet_audit.py        # dry-run, prints summary
  python scripts/cutsheet_audit.py --download

The script will:
 - load the device catalog via app.catalog.load_catalog()
 - for each device, attempt to find a local cutsheet (using backend.device_docs)
 - if a URL is available (fallback), record it
 - optionally download any discovered URLs into the cutsheet folder
 - write a CSV report to artifacts/cutsheet_audit.csv
"""

from __future__ import annotations

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import catalog
from backend import device_docs


def main(download: bool = False) -> int:
    devices = catalog.load_catalog()
    out_dir = os.path.join(os.getcwd(), "artifacts")
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "cutsheet_audit.csv")

    rows: list[list[str]] = []
    print(f"Scanning {len(devices)} devices from catalog...")
    for d in devices:
        name = d.get("name", "")
        pn = d.get("part_number", "")
        mfg = d.get("manufacturer", "")

        # attempt to find local or url; lookup_docs_for_item returns a dict
        docs = {}
        try:
            docs = device_docs.lookup_docs_for_item(d) or {}
        except Exception:
            docs = {}

        local = docs.get("cutsheet")
        _manual = docs.get("manual")

        url = None
        if isinstance(local, str) and (local.startswith("http://") or local.startswith("https://")):
            url = local
            local = None

        missing = not (bool(local) or bool(url))
        rows.append([name, mfg, pn, local or "", url or "", str(missing)])

    # write csv
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "manufacturer", "part_number", "local_path", "url", "missing"])
        w.writerows(rows)

    print(f"Audit written to: {report_path}")

    if download:
        # download any URL entries
        print("Downloading discovered URLs...")
        downloaded = 0
        for row in rows:
            url = row[4]
            if url:
                got = device_docs.download_doc(url)
                if got:
                    downloaded += 1
                    print(f"Downloaded: {url} -> {got}")
                else:
                    print(f"Failed to download: {url}")
        print(f"Downloaded {downloaded} documents")

    # print summary
    total = len(rows)
    missing_count = sum(1 for r in rows if r[5] == "True")
    urls = sum(1 for r in rows if r[4])
    local = sum(1 for r in rows if r[3])

    print("Summary:")
    print(f"  total devices: {total}")
    print(f"  local docs: {local}")
    print(f"  remote URLs found: {urls}")
    print(f"  missing: {missing_count}")

    return 0


if __name__ == "__main__":
    download_flag = "--download" in sys.argv
    sys.exit(main(download=download_flag))
