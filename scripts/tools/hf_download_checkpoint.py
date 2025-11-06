"""Small shim to import the canonical downloader implementation.

The original file had multiple concatenated copies and caused parse errors
for linters/formatters. We keep a tiny shim here that imports the
canonical implementation from a new clean module so tools can parse this
file quickly.
"""

from __future__ import annotations

from .hf_download_checkpoint_clean import main  # type: ignore

if __name__ == "__main__":
    raise SystemExit(main())
