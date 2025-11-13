"""Fillet wrappers (parity-first).

These delegate to legacy cad_core.fillet implementations until lv_cad
provides native versions. This keeps behavior stable during migration.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:  # legacy fallback imports
    from cad_core.fillet import (
        fillet_circle_circle as _legacy_fillet_circle_circle,
    )
    from cad_core.fillet import (
        fillet_line_circle as _legacy_fillet_line_circle,
    )
    from cad_core.fillet import (
        fillet_line_line as _legacy_fillet_line_line,
    )
except ImportError:  # pragma: no cover
    _legacy_fillet_line_line: Callable[..., Any] | None = None
    _legacy_fillet_line_circle: Callable[..., Any] | None = None
    _legacy_fillet_circle_circle: Callable[..., Any] | None = None

# unified convenience wrapper (example signature kept simple for now)


def fillet(*args: Any, **kwargs: Any):  # noqa: ANN401 - intentionally generic
    """General fillet convenience wrapper.

    For now just forwards to line-line variant if available.
    """
    if _legacy_fillet_line_line is None:  # pragma: no cover
        raise RuntimeError("Legacy fillet implementation unavailable.")
    return _legacy_fillet_line_line(*args, **kwargs)


def fillet_line_line(*args: Any, **kwargs: Any):  # noqa: ANN401
    if _legacy_fillet_line_line is None:  # pragma: no cover
        raise RuntimeError("Legacy fillet_line_line unavailable.")
    return _legacy_fillet_line_line(*args, **kwargs)


def fillet_line_circle(*args: Any, **kwargs: Any):  # noqa: ANN401
    if _legacy_fillet_line_circle is None:  # pragma: no cover
        raise RuntimeError("Legacy fillet_line_circle unavailable.")
    return _legacy_fillet_line_circle(*args, **kwargs)


def fillet_circle_circle(*args: Any, **kwargs: Any):  # noqa: ANN401
    if _legacy_fillet_circle_circle is None:  # pragma: no cover
        raise RuntimeError("Legacy fillet_circle_circle unavailable.")
    return _legacy_fillet_circle_circle(*args, **kwargs)
