"""Device documentation lookup helpers migrated to lv_cad.backend (parity copy)."""

from __future__ import annotations

import os
from typing import Any

# Keep same default behavior as legacy module
DEFAULT_CUTSHEET_DIR = os.environ.get("AUTOFIRE_CUTSHEETS_DIR", r"C:\\Dev\\cutsheets")

_KNOWN_URLS = {
    "smoke": "https://example.com/docs/smoke-detector.pdf",
    "heat": "https://example.com/docs/heat-detector.pdf",
}


def _find_local_doc_for_token(token: str, folder: str | None = None) -> str | None:
    if not token:
        return None
    base = folder or DEFAULT_CUTSHEET_DIR
    try:
        token_l = token.lower()
        for root, _, files in os.walk(base):
            for fn in files:
                name_l = fn.lower()
                if token_l in name_l or token_l.replace(" ", "") in name_l:
                    if any(
                        name_l.endswith(ext) for ext in (".pdf", ".docx", ".doc", ".rtf", ".txt")
                    ):
                        return os.path.join(root, fn)
    except Exception:
        return None
    return None


def lookup_docs_for_item(item: Any) -> dict:
    try:
        if isinstance(item, dict):
            pn = item.get("part_number") or ""
            name = item.get("name") or ""
            mfg = item.get("manufacturer") or ""
        else:
            pn = ""
            name = ""
            mfg = ""
            try:
                data = item.data(0, 0)
                if isinstance(data, dict):
                    pn = data.get("part_number", "")
                    name = data.get("name", "")
                    mfg = data.get("manufacturer", "")
            except Exception:
                pn = getattr(item, "part_number", "")
                name = getattr(item, "name", "")
                mfg = getattr(item, "manufacturer", "")

        result = {"cutsheet": None, "manual": None}
        for token in (pn, name, mfg):
            if token:
                local = _find_local_doc_for_token(str(token))
                if local:
                    result["cutsheet"] = local
                    break

        for token in (pn, name, mfg):
            if token:
                manual_local = _find_local_doc_for_token(f"{token} manual")
                if manual_local:
                    result["manual"] = manual_local
                    break

        name_l = (name or "").lower()
        for key, url in _KNOWN_URLS.items():
            if key in name_l:
                if not result["cutsheet"]:
                    result["cutsheet"] = url
                if not result["manual"]:
                    result["manual"] = url

        return result
    except Exception:
        return {"cutsheet": None, "manual": None}


def lookup_docs_for_spec(
    *,
    manufacturer: str | None = None,
    model: str | None = None,
    name: str | None = None,
    part_number: str | None = None,
) -> dict:
    try:
        tokens = [part_number or "", model or "", name or "", manufacturer or ""]
        result = {"cutsheet": None, "manual": None}
        for t in tokens:
            if t:
                local = _find_local_doc_for_token(str(t))
                if local and not result["cutsheet"]:
                    result["cutsheet"] = local
                manual_local = _find_local_doc_for_token(f"{t} manual")
                if manual_local and not result["manual"]:
                    result["manual"] = manual_local

        nm = (name or model or "").lower()
        for key, url in _KNOWN_URLS.items():
            if key in nm:
                if not result["cutsheet"]:
                    result["cutsheet"] = url
                if not result["manual"]:
                    result["manual"] = url

        return result
    except Exception:
        return {"cutsheet": None, "manual": None}


def list_available_docs(folder: str | None = None) -> list[str]:
    base = folder or DEFAULT_CUTSHEET_DIR
    out: list[str] = []
    try:
        for root, _, files in os.walk(base):
            for fn in files:
                if any(
                    fn.lower().endswith(ext) for ext in (".pdf", ".docx", ".doc", ".rtf", ".txt")
                ):
                    out.append(os.path.join(root, fn))
    except Exception:
        return []
    return out


def download_doc(url: str, folder: str | None = None, timeout: int = 20) -> str | None:
    try:
        import urllib.parse
        import urllib.request

        base = folder or DEFAULT_CUTSHEET_DIR
        os.makedirs(base, exist_ok=True)
        parsed = urllib.parse.urlparse(url)
        fname = os.path.basename(parsed.path) or "downloaded_doc"
        fname = fname.replace("/", "_").replace("\\\\", "_")
        dest = os.path.join(base, fname)

        with urllib.request.urlopen(url, timeout=timeout) as resp:
            try:
                cd = resp.getheader("Content-Disposition")
                if cd and "filename=" in cd:
                    import re

                    m = re.search(r'filename\*=.*?""(.+?)$', cd)
                    if m:
                        fname = m.group(1)
                        dest = os.path.join(base, fname)
            except Exception:
                pass

            with open(dest, "wb") as out_f:
                out_f.write(resp.read())
        return dest
    except Exception:
        return None
