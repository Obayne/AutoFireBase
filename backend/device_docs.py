"""Device documentation lookup helpers.

This module looks for local cutsheet documents in a designated folder
(`C:\\Dev\\cutsheets` by default) and falls back to a small set of
example URLs. It provides two main helpers used by the UI:

- lookup_docs_for_item(item) -> str | None
- lookup_docs_for_spec(spec) -> str | None

It also exposes `list_available_docs()` for discovery.
"""

from __future__ import annotations

import os
from typing import Any

# Configurable cutsheet directory. Can be overridden by setting the
# environment variable AUTOFIRE_CUTSHEETS_DIR. Defaults to C:\\Dev\\cutsheets
DEFAULT_CUTSHEET_DIR = os.environ.get("AUTOFIRE_CUTSHEETS_DIR", r"C:\\Dev\\cutsheets")

_KNOWN_URLS = {
    "smoke": "https://example.com/docs/smoke-detector.pdf",
    "heat": "https://example.com/docs/heat-detector.pdf",
}


def _find_local_doc_for_token(token: str, folder: str | None = None) -> str | None:
    """Search the cutsheet folder for a filename that contains `token`.

    Returns an absolute path if found, otherwise None.
    """
    if not token:
        return None
    base = folder or DEFAULT_CUTSHEET_DIR
    try:
        # normalize
        token_l = token.lower()
        for root, _, files in os.walk(base):
            for fn in files:
                name_l = fn.lower()
                # match token or compacted token
                if token_l in name_l or token_l.replace(" ", "") in name_l:
                    # accept common document extensions
                    if any(
                        name_l.endswith(ext) for ext in (".pdf", ".docx", ".doc", ".rtf", ".txt")
                    ):
                        return os.path.join(root, fn)
    except Exception:
        return None
    return None


def lookup_docs_for_item(item: Any) -> dict:
    """Return a dict with available docs for a device item.

    Returns a dictionary with keys 'cutsheet' and 'manual' (values are
    local file paths or URLs, or None). This matches the UI's expected
    contract used by ModelSpaceWindow.
    """
    try:
        # try dict-like access first
        if isinstance(item, dict):
            pn = item.get("part_number") or ""
            name = item.get("name") or ""
            mfg = item.get("manufacturer") or ""
        else:
            # for QTreeWidgetItem or similar, it may expose .data(role)
            pn = ""
            name = ""
            mfg = ""
            try:
                data = item.data(0, 0)  # may raise or return underlying dict
                if isinstance(data, dict):
                    pn = data.get("part_number", "")
                    name = data.get("name", "")
                    mfg = data.get("manufacturer", "")
            except Exception:
                # try attribute access as fallback
                pn = getattr(item, "part_number", "")
                name = getattr(item, "name", "")
                mfg = getattr(item, "manufacturer", "")

        result = {"cutsheet": None, "manual": None}

        # prefer part number then name then manufacturer
        for token in (pn, name, mfg):
            if token:
                local = _find_local_doc_for_token(str(token))
                if local:
                    result["cutsheet"] = local
                    break

        # try to locate a 'manual' by appending keywords
        for token in (pn, name, mfg):
            if token:
                manual_local = _find_local_doc_for_token(f"{token} manual")
                if manual_local:
                    result["manual"] = manual_local
                    break

        # fallback to known URLs by name tokens
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
    """Lookup docs by spec fields and return dict with 'cutsheet' and 'manual'.

    ModelSpaceWindow calls this function with keyword args; we accept those
    and attempt to find local docs or fall back to known URLs.
    """
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

        # fallback to known urls using name/model
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
    """Return a list of files under the cutsheet folder (absolute paths).

    Useful for discovery or building a small index.
    """
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
    """Download a document from `url` into the cutsheet folder.

    Returns the saved file path on success, otherwise None.
    """
    try:
        import urllib.parse
        import urllib.request

        base = folder or DEFAULT_CUTSHEET_DIR
        os.makedirs(base, exist_ok=True)

        # derive filename
        parsed = urllib.parse.urlparse(url)
        fname = os.path.basename(parsed.path) or "downloaded_doc"
        # sanitize
        fname = fname.replace("/", "_").replace("\\\\", "_")
        dest = os.path.join(base, fname)

        # stream download
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            # if server provides filename, try to use it
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
