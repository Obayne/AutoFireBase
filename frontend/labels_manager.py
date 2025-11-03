"""Frontend-facing helpers for wirepath labels.

This module has no Qt imports; UI can call these functions to get label strings
and manage the 'hide conduit fill' preference.
"""

from __future__ import annotations

from typing import Dict

from backend.preferences import load_preferences, update_preferences
from cad_core.labels import format_wirepath_label


def get_hide_conduit_fill() -> bool:
    prefs = load_preferences()
    return bool(prefs.get("hide_conduit_fill", False))


def set_hide_conduit_fill(value: bool) -> None:
    update_preferences({"hide_conduit_fill": bool(value)})


def format_label_for_ui(*, conduit_kind: str, trade_size: str, wires: Dict[int, int]) -> str | None:
    hide = get_hide_conduit_fill()
    return format_wirepath_label(
        conduit_kind=conduit_kind, trade_size=trade_size, wires=wires, hide_fill=hide
    )
