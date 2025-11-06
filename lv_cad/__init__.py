"""lv_cad package — new, cleaner implementations for LV CAD migration.

This package is introduced as part of a gradual strangler migration. New
implementations of core subsystems (cad_core, io, utils) will live under
`lv_cad.*`. Existing code will continue to import the legacy modules while a
shim/adapter redirects to `lv_cad` when available.
"""

__all__ = ["cad_core"]
