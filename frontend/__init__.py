"""Frontend package (Qt UI).

Legacy UI code currently lives in `app/`. As modules are migrated,
imports should come from `frontend.*` rather than `app.*`.

Dev Hooks
---------
If the environment variable `FRONTEND_OPS_TOOLS` is set to a truthy value,
register passive ops tools for development via `frontend.integration`.
This avoids altering active UI while enabling quick tool discovery.
"""

from __future__ import annotations

import os


def _maybe_activate_dev_hooks() -> None:
    if os.getenv("FRONTEND_OPS_TOOLS"):
        try:
            from .integration import register_ops_tools

            register_ops_tools()
        except Exception:
            # Dev-only hook; ignore failures to keep package import safe
            pass


_maybe_activate_dev_hooks()
