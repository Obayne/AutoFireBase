"""CAD Core package (geometry and algorithms).

This module acts as a small adapter: prefer implementations provided under
`lv_cad.cad_core` when available (new, migrated code). If the new package is
not importable, fall back to the legacy implementations present in this
package.

The adapter is intentionally minimal and only redirects the public API when
the new implementation is available. This keeps changes incremental and low
risk during migration.
"""

import importlib
import logging

_logger = logging.getLogger(__name__)


def _prefer_lv_cad():
    try:
        mod = importlib.import_module("lv_cad.cad_core")
        _logger.info("Using lv_cad.cad_core implementation")
        return mod
    except Exception:
        _logger.debug("lv_cad.cad_core not available; using legacy cad_core")
        return None


_lv = _prefer_lv_cad()
if _lv is not None:
    # Export everything from the new implementation for callers that import
    # `cad_core` directly. Using explicit attribute delegation keeps the
    # import surface familiar while allowing gradual migration.
    for _name in getattr(_lv, "__all__", []):
        globals()[_name] = getattr(_lv, _name)
    __all__ = list(getattr(_lv, "__all__", []))
else:
    # Legacy package remains the source of truth. Leave __all__ to be
    # populated by submodules (or remain empty) so behavior is unchanged.
    __all__ = []
