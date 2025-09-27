"""
Workspace state helpers.

This module provides a tiny, UI-agnostic representation of the current workspace
mode and utilities that higher layers can consult to decide which tools or
menus should be active.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class Workspace(Enum):
    MODEL = auto()
    PAPER = auto()


@dataclass(frozen=True)
class ToolPolicy:
    modeling_enabled: bool
    layout_enabled: bool
    export_enabled: bool


def policy_for(workspace: Workspace) -> ToolPolicy:
    """Return coarse tool policy for the given workspace.

    - MODEL: modeling on, layout/export allowed if desired.
    - PAPER: modeling off, layout/export on.
    """
    if workspace is Workspace.PAPER:
        return ToolPolicy(modeling_enabled=False, layout_enabled=True, export_enabled=True)
    return ToolPolicy(modeling_enabled=True, layout_enabled=True, export_enabled=True)


def disabled_tool_kinds(workspace: Workspace) -> frozenset[str]:
    """Return symbolic tool kinds that should be disabled in this workspace.

    This is intentionally generic; the frontend can map these to actual actions.
    """
    if workspace is Workspace.PAPER:
        return frozenset(
            {
                "draw/line",
                "draw/arc",
                "draw/circle",
                "modify/trim",
                "modify/extend",
                "modify/fillet",
                "cad/array",
            }
        )
    return frozenset()


__all__ = ["Workspace", "ToolPolicy", "policy_for", "disabled_tool_kinds"]
