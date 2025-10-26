"""Device documentation lookup.

Loads a simple JSON mapping of device identifiers to documentation URLs.

Key matching strategy:
- Primary: part_number (lowercased)
- Secondary: model/name strings (lowercased)
- Manufacturer isn't required but may help in the future for disambiguation.

JSON format (backend/device_docs.json):
{
  "p2r": {"cutsheet": "https://...", "manual": "https://..."},
  "sd-355": {"cutsheet": "https://..."}
}
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional


@lru_cache(maxsize=1)
def _load_docs_table() -> dict[str, dict[str, str]]:
    path = Path(__file__).with_name("device_docs.json")
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            # normalize keys to lowercase with compact loops for readability
            out: dict[str, dict[str, str]] = {}
            for k, v in (data or {}).items():
                norm_k = str(k).lower()
                sub = {}
                for kk, vv in (v or {}).items():
                    sub[str(kk)] = str(vv)
                out[norm_k] = sub
            return out
    except (OSError, json.JSONDecodeError):
        # ignore file/read/parse issues and return empty mapping
        pass
    return {}


def _norm(v: Any) -> str:
    return str(v or "").strip().lower()


def lookup_docs_for_item(item: Any) -> dict[str, str]:
    """Lookup documentation URLs for a device-like item.

    Returns a dict with optional keys: cutsheet, manual.
    """
    table = _load_docs_table()
    if not table:
        return {}

    keys = []
    for name in ("part_number", "model", "name"):
        try:
            val = getattr(item, name, None)
        except Exception:
            val = None
        if val:
            keys.append(_norm(val))

    for k in keys:
        if k in table:
            return dict(table[k])

    return {}


def lookup_docs_for_spec(
    *,
    manufacturer: Optional[str] = None,  # reserved for future disambiguation
    model: Optional[str] = None,
    name: Optional[str] = None,
    part_number: Optional[str] = None,
) -> dict[str, str]:
    """Lookup documentation URLs by loose device spec fields.

    Priority: part_number -> model -> name. Manufacturer is currently unused
    but kept for future refinement.
    """
    table = _load_docs_table()
    if not table:
        return {}
    for key in (_norm(part_number), _norm(model), _norm(name)):
        if key and key in table:
            return dict(table[key])
    return {}


def export_device_docs_html(items, dest_path: str) -> str:
    """Export an HTML table listing devices and their documentation links.

    Columns: manufacturer, part_number, name, cutsheet, manual
    Returns the path written.
    """
    from backend.reports import _item_signature  # reuse signature helper

    # Unique rows by signature
    seen = set()
    rows: list[tuple[str, str, str, str, str]] = []
    for it in items or []:
        mfg, pn, name = _item_signature(it)
        sig = (mfg, pn, name)
        if sig in seen:
            continue
        seen.add(sig)
        docs = lookup_docs_for_item(it)
        cutsheet = docs.get("cutsheet", "")
        manual = docs.get("manual", "")
        rows.append((mfg, pn, name, cutsheet, manual))

    # Build HTML
    def cell_link(url: str) -> str:
        if url:
            return f'<a href="{url}" target="_blank">link</a>'
        return ""

    headers = ["manufacturer", "part_number", "name", "cutsheet", "manual"]
    thead = "".join(f"<th>{h}</th>" for h in headers)
    tbody = "\n".join(
        "<tr>" +
        f"<td>{mfg}</td><td>{pn}</td><td>{name}</td>" +
        f"<td>{cell_link(c)}</td><td>{cell_link(man)}</td>" +
        "</tr>"
        for (mfg, pn, name, c, man) in rows
    )

    html = f"""
    <!doctype html>
    <html><head>
    <meta charset='utf-8'/>
    <title>Device Documents</title>
    <style>
    body {{ font-family: Segoe UI, Roboto, Arial, sans-serif; color: #222; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #ccc; padding: 6px 8px; font-size: 13px; }}
    th {{ background: #f6f6f6; }}
    caption {{ text-align: left; font-weight: bold; margin-bottom: .5rem; }}
    </style>
    </head><body>
    <h1>Device Documents</h1>
    <table>
      <caption>Device documents (cutsheets, manuals)</caption>
      <thead><tr>{thead}</tr></thead>
      <tbody>{tbody}</tbody>
    </table>
    </body></html>
    """

    out_path = Path(dest_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return str(out_path)
