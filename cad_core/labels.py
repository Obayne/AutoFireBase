"""Wirepath label formatting helpers.

Keeps UI-agnostic formatting concentrated here. The core entrypoint
`format_wirepath_label` can be used by the frontend labels manager.
"""

from __future__ import annotations

from typing import Dict

from .conduit_fill import compute_fill_pct


def _format_wire_bundle(wires: Dict[int, int]) -> str:
    # Example: {18: 10, 12: 2} -> "10x18AWG + 2x12AWG"
    parts: list[str] = []
    for awg in sorted(wires.keys(), reverse=True):
        count = int(wires[awg])
        if count <= 0:
            continue
        parts.append(f"{count}x{awg}AWG")
    return " + ".join(parts) if parts else ""


def format_wirepath_label(
    *,
    conduit_kind: str,
    trade_size: str,
    wires: Dict[int, int],
    hide_fill: bool = False,
) -> str | None:
    """Return a wirepath label string or None if fill is hidden.

    Output shape: "3/4 EMT — 10x18AWG + 2x12AWG — 23.4% fill"
    When hide_fill=True, returns just the cable bundle portion:
      "10x18AWG + 2x12AWG"
    If the bundle is empty, returns None.
    """
    bundle = _format_wire_bundle(wires)
    if not bundle:
        return None

    if hide_fill:
        return bundle

    fill_pct, _ = compute_fill_pct(conduit_kind, trade_size, wires)
    # We could append a warning indicator if over limit later (e.g., "⚠")
    return f"{trade_size} {conduit_kind.upper()} — {bundle} — {fill_pct:.1f}% fill"


__all__ = ["format_wirepath_label"]
