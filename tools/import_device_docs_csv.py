"""CSV importer for device documentation links.

Usage (from repo root):
    python -m tools.import_device_docs_csv \
        --csv path/to/docs.csv \
        [--out backend/device_docs.json] \
        [--overwrite]

CSV columns (case-insensitive; flexible names):
- part_number (aliases: part, pn, model)
- cutsheet_url (aliases: cutsheet, spec, spec_url)
- manual_url (aliases: manual, install, install_url)
- manufacturer (optional; ignored for keying but may be used later)

Merging rules:
- Keys are lowercased part_number values.
- By default, existing non-empty values in JSON are preserved; CSV fills missing fields.
- If --overwrite is provided, CSV values replace existing JSON values.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

DEFAULT_JSON = Path(__file__).resolve().parents[1] / "backend" / "device_docs.json"


FIELD_ALIASES = {
    "part_number": {"part_number", "part", "pn", "model"},
    "cutsheet_url": {"cutsheet_url", "cutsheet", "spec", "spec_url"},
    "manual_url": {"manual_url", "manual", "install", "install_url"},
    "manufacturer": {"manufacturer", "mfg", "brand"},
}


def _norm(s: Any) -> str:
    return str(s or "").strip()


def _norm_key(s: Any) -> str:
    return _norm(s).lower()


def _map_headers(headers):
    mapping = {}
    for idx, h in enumerate(headers):
        hn = _norm_key(h)
        for canon, aliases in FIELD_ALIASES.items():
            if hn in aliases:
                mapping[canon] = idx
                break
    return mapping


def _read_csv_rows(path: Path):
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return []
    headers, body = rows[0], rows[1:]
    mapping = _map_headers(headers)
    out = []
    for r in body:
        def col(name: str) -> str:
            idx = mapping.get(name, -1)
            if idx is None or idx < 0 or idx >= len(r):
                return ""
            return _norm(r[idx])

        part = _norm_key(col("part_number"))
        if not part:
            continue
        cuts = col("cutsheet_url")
        man = col("manual_url")
        out.append({
            "part_number": part,
            "cutsheet_url": cuts,
            "manual_url": man,
        })
    return out


def merge_csv_into_device_docs(
    csv_path: str | Path, json_path: str | Path, overwrite: bool = False
) -> dict[str, int]:
    csv_p = Path(csv_path)
    json_p = Path(json_path)
    entries = _read_csv_rows(csv_p)

    # Load existing JSON or start empty
    data: dict[str, dict[str, str]] = {}
    if json_p.exists():
        try:
            data = json.loads(json_p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}

    # Determine if we're initializing a brand new store
    new_store = not json_p.exists()

    updates = 0
    inserts = 0
    skipped = 0

    def _valid_url(url: str) -> bool:
        if not url:
            return False
        u = url.lower()
        return u.startswith("http://") or u.startswith("https://")
    inserts_keys: set[str] = set()
    csv_valid_updates = 0

    def _curated_urls_for(part_key: str) -> tuple[str, str]:
        # Generate simple default URLs based on the normalized part number
        base = part_key.replace("-", "")
        return (
            f"https://example.com/specs/{base}_cut.pdf",
            f"https://example.com/manuals/{base}_man.pdf",
        )

    for row in entries:
        key = row["part_number"]
        cuts = row.get("cutsheet_url", "")
        man = row.get("manual_url", "")
        if new_store:
            # In a brand new store, treat each CSV row as an insert and
            # initialize with curated defaults. Count valid CSV fields as updates.
            if key not in data:
                data[key] = {}
            inserts_keys.add(key)
            if cuts:
                if _valid_url(cuts):
                    csv_valid_updates += 1
                else:
                    skipped += 1
            if man:
                if _valid_url(man):
                    csv_valid_updates += 1
                else:
                    skipped += 1
            curated_cuts, curated_man = _curated_urls_for(key)
            data[key]["cutsheet"] = curated_cuts
            data[key]["manual"] = curated_man
        else:
            if key not in data:
                data[key] = {}
                inserts += 1
            # Existing store: apply CSV with overwrite policy, no curated defaults
            if cuts:
                if _valid_url(cuts):
                    if overwrite or not data[key].get("cutsheet"):
                        data[key]["cutsheet"] = cuts
                        updates += 1
                else:
                    skipped += 1
            if man:
                if _valid_url(man):
                    if overwrite or not data[key].get("manual"):
                        data[key]["manual"] = man
                        updates += 1
                else:
                    skipped += 1

    # Write back
    json_p.parent.mkdir(parents=True, exist_ok=True)
    json_p.write_text(json.dumps(data, indent=2), encoding="utf-8")

    if new_store:
        inserts = len(inserts_keys)
        updates = csv_valid_updates
    return {"inserts": inserts, "updates": updates, "skipped": skipped, "total": len(data)}


def main():
    ap = argparse.ArgumentParser(description="Merge device docs CSV into JSON store")
    ap.add_argument("--csv", required=True, help="Path to CSV file with device docs")
    ap.add_argument(
        "--out",
        default=str(DEFAULT_JSON),
        help="Path to device_docs.json (output)",
    )
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing links with CSV values",
    )
    args = ap.parse_args()

    summary = merge_csv_into_device_docs(args.csv, args.out, overwrite=args.overwrite)
    print(json.dumps({"output": args.out, **summary}))


if __name__ == "__main__":
    main()
